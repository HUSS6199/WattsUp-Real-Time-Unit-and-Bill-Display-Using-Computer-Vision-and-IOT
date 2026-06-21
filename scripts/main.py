import time, os, base64, requests, re
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# --- SETTINGS ---
API_KEY = "1gLG8UA6XCar41KxMw3x"
PROJECT = "ocr-digivault"
VERSION = "2"
FIREBASE_URL = "https://wattsup-meter-default-rtdb.asia-southeast1.firebasedatabase.app/"
NOTIFICATION_LIMIT = 50.0
INFERENCE_URL = "https://detect.roboflow.com"

# Filter Settings
STRICT_KWH_ONLY = True
KWH_MIN_CONFIDENCE = 0.05  # Lowered to 5% so it easily catches the kWh label even if it flickers

# Noise rejection: ignore detections too close to top/bottom edge (y < 50 or y > 910 in 960px frame)
MIN_Y_PIXELS = 50
MAX_Y_PIXELS = 910

# Decimal adjustments
DECIMAL_SHIFT = 2
CAPTURE_INTERVAL = 3  # Lowered to 3 seconds for easier hand-held testing

# Stability Filter
CONSECUTIVE_READINGS_REQUIRED = 2
recent_readings = []

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        print("✅ Firebase initialized successfully.")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        print("Make sure 'serviceAccountKey.json' is in the same folder as this script.")

usage_ref = db.reference('current_usage')
history_ref = db.reference('meter_readings')


def get_predictions(data):
    """Extract predictions list from Roboflow standard response."""
    if isinstance(data, dict) and "predictions" in data:
        return data["predictions"]
    return []


def assemble_digits(predictions, img_height=480):
    if not predictions or not isinstance(predictions, list):
        return "", set()

    valid = []
    detected_classes = set()

    for p in predictions:
        if not isinstance(p, dict):
            continue

        cls = str(p.get('class', '')).strip().lower()
        conf = float(p.get('confidence', 0))
        x = float(p.get('x', 0))
        y = float(p.get('y', 0))

        # Reject edge noise
        if y < MIN_Y_PIXELS or y > MAX_Y_PIXELS:
            continue

        # Use the lowered confidence for detecting labels like 'kwh'
        if conf >= KWH_MIN_CONFIDENCE:
            detected_classes.add(cls)

        # Keep a strict 15% confidence for actual numbers so we don't get junk math
        if cls not in '0123456789.' or conf < 0.15:
            continue

        # x is center; derive left edge for left-to-right sorting
        w = float(p.get('width', 0))
        left = x - w / 2
        valid.append((left, cls))

    if len(valid) < 3:
        return "", detected_classes

    # Sort left-to-right
    valid.sort(key=lambda t: t[0])
    text = ''.join([c for _, c in valid])

    # Cleanup: collapse 3+ identical consecutive digits (LCD ghosting)
    text = re.sub(r'(\d)\1{2,}', r'\1\1', text)
    # Cleanup: multiple dots
    text = re.sub(r'\.{2,}', '.', text)
    return text, detected_classes


def send_to_firebase(units, bill, is_alert):
    try:
        now = datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')

        previous_data = usage_ref.get()
        prev_units = previous_data.get('units', 0) if previous_data else 0

        if units > prev_units:
            consumption = units - prev_units
            history_ref.push({
                'timestamp': timestamp_str,
                'units': units,
                'consumption_delta': round(consumption, 2),
                'bill_pkr': round(bill + 400, 0)
            })
            print(f"  📈 Logged History! Consumption since last reading: +{round(consumption, 2)} kWh")

        usage_ref.update({
            'units': round(units, 2),
            'bill_pkr': round(bill + 400, 0),
            'trigger_notification': is_alert,
            'last_sync': now.strftime('%H:%M:%S')
        })
        print(f"  ✅ Firebase Current Usage updated: {units} kWh")
    except Exception as e:
        print(f"  🔥 Firebase write failed: {e}")


def process_reading(predictions):
    reading, detected_classes = assemble_digits(predictions)

    # FILTER: Reject kW, W, A
    forbidden = {'kw', 'w', 'a', 'amps', 'volts', 'v'}
    found_forbidden = detected_classes.intersection(forbidden)
    if found_forbidden:
        print(f"  🚫 Ignored Frame: Screen is showing {found_forbidden}, waiting for KWH...")
        return

    # FILTER: Require kWh with minimum confidence
    kwh_found = 'kwh' in detected_classes
    if STRICT_KWH_ONLY and not kwh_found:
        print(f"  🚫 Ignored Frame: 'kWh' label not detected. Classes found: {detected_classes}")
        return

    print(f"\n🔧 Assembled reading: '{reading}'")

    if not reading or len(reading) < 3:
        print("  🚫 Too few digits — skipped Firebase")
        return

    numbers = re.findall(r"\d+\.?\d*", reading)
    if not numbers:
        print(f"  🚫 No valid number in '{reading}' — skipped Firebase")
        return

    num_str = max(numbers, key=len)

    if '.' in num_str:
        units = float(num_str)
    elif DECIMAL_SHIFT > 0:
        units = float(num_str) / (10 ** DECIMAL_SHIFT)
    else:
        units = float(num_str)

    if units < 0.1 or units > 999999:
        print(f"  🚫 Value {units} unrealistic — skipped Firebase")
        return

    # --- STABILITY FILTER ---
    recent_readings.append(units)
    if len(recent_readings) > CONSECUTIVE_READINGS_REQUIRED:
        recent_readings.pop(0)

    if len(recent_readings) < CONSECUTIVE_READINGS_REQUIRED or len(set(recent_readings)) > 1:
        print(f"  ⏳ Stability Filter: Waiting for {CONSECUTIVE_READINGS_REQUIRED} identical consecutive readings... (Buffer: {recent_readings})")
        return
    # ------------------------

    bill = (units * 16.48) if units <= 100 else (100 * 16.48) + ((units - 100) * 22.95)
    is_alert = units > NOTIFICATION_LIMIT

    send_to_firebase(units, bill, is_alert)
    print(f"  💰 Bill: Rs. {bill+400:.0f} | Alert: {is_alert}")


def infer_with_retry(image_b64, retries=3, delay=5):
    url = f"{INFERENCE_URL}/{PROJECT}/{VERSION}?api_key={API_KEY}"
    for attempt in range(retries):
        try:
            # Send the base64 string directly to the new model
            res = requests.post(url, data=image_b64, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=(15, 60))
            if res.status_code == 200:
                return res.json()
            print(f"⚠️ HTTP {res.status_code}: {res.text[:100]}")
        except Exception as e:
            print(f"⚠️ Connection error (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    return None


# --- MAIN LOOP ---
print(f"🚀 Starting WattsUp Native Pi Monitor (ocr-digivault/2 MODE)...")
print("=" * 50)

while True:
    print(f"\n📸 [{time.strftime('%H:%M:%S')}] Capturing frame...")

    # Increased resolution to 1280x960 so the tiny 'kWh' and decimal don't get pixelated
    exit_code = os.system(
        "rpicam-still -t 1000 --nopreview --width 1280 --height 960 -o frame.jpg >/dev/null 2>&1"
    )

    if exit_code != 0 or not os.path.exists("frame.jpg"):
        print("⚠️ Camera capture failed!")
        time.sleep(10)
        continue

    try:
        with open("frame.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Failed to read image file: {e}")
        time.sleep(5)
        continue

    data = infer_with_retry(img_b64)

    if data:
        predictions = get_predictions(data)
        if predictions:
            process_reading(predictions)
        else:
            print("  ⚠️ No predictions in response")
    else:
        print("⚠️ Inference unavailable, waiting...")

    time.sleep(CAPTURE_INTERVAL)
