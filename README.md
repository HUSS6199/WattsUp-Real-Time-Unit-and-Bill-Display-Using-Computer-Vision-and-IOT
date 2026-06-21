# WattsUp: Real-Time Utility Meter Monitoring

## Overview
WattsUp retrofits legacy electricity meters using a **Raspberry Pi 4** and **Pi Camera V3** to capture screen images every 4.5 minutes. A custom **YOLOv8 model** isolates the LCD display, while **OpenCV** and **OCR** extract kWh usage. Validated data is sent to **Firebase**, powering a real-time web dashboard for usage tracking and billing.

## Key Features
- ✅ Automated image capture (4.5-minute intervals)
- ✅ YOLOv8-powered digit detection
- ✅ Real-time kWh extraction with OCR
- ✅ Firebase real-time database integration
- ✅ Web dashboard for visualization
- ✅ Automatic billing calculation
- ✅ Alert notifications on usage thresholds

## Project Structure
```
WattsUp/
├── scripts/
│   └── main.py                 # Main monitoring script (runs on Pi)
├── cv_model/
│   └── inference.py            # YOLOv8 inference logic
├── ocr/
│   └── extract_digits.py       # Digit extraction & assembly
├── firebase/
│   ├── database.py             # Firebase operations
│   └── config/
├── web_dashboard/              # Frontend visualization
├── hardware/
│   └── setup.md                # Pi & camera setup guide
├── tests/
│   └── test_ocr.py
├── requirements.txt
└── README.md
```

## Hardware Setup
- **Raspberry Pi 4** (4GB+ RAM recommended)
- **Pi Camera V3** (12MP with autofocus)
- Stable Wi-Fi connection
- SD Card (32GB+ recommended)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/HUSS6199/WattsUp-Real-Time-Unit-and-Bill-Display-Using-Computer-Vision-and-IOT.git
cd WattsUp-Real-Time-Unit-and-Bill-Display-Using-Computer-Vision-and-IOT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Firebase Setup
- Download your Firebase service account key
- Save as `serviceAccountKey.json` in the `scripts/` directory
- Keep this file private (add to `.gitignore`)

### 4. Configure Settings
Edit `scripts/main.py` to set:
- `API_KEY` (Roboflow API key)
- `PROJECT` (Roboflow project name)
- `NOTIFICATION_LIMIT` (Alert threshold in kWh)

### 5. Run on Raspberry Pi
```bash
python3 scripts/main.py
```

## Roboflow Model Configuration
- **Model**: ocr-digivault v2
- **Purpose**: Detect LCD digits and kWh label
- **Confidence Threshold**: 5% for labels, 15% for digits
- **Edge Filtering**: Rejects detections at image boundaries

## Firebase Data Structure
```json
{
  "current_usage": {
    "units": 125.45,
    "bill_pkr": 2300,
    "trigger_notification": false,
    "last_sync": "14:32:15"
  },
  "meter_readings": {
    "reading_id": {
      "timestamp": "2026-06-21 14:32:15",
      "units": 125.45,
      "consumption_delta": 2.5,
      "bill_pkr": 2300
    }
  }
}
```

## Billing Calculation
- **Tier 1**: 0-100 kWh @ Rs. 16.48/kWh
- **Tier 2**: >100 kWh @ Rs. 22.95/kWh
- **Fixed Charge**: Rs. 400/month

## Troubleshooting

### Camera Not Detected
```bash
rpicam-still -t 1000 --nopreview -o test.jpg
```

### Firebase Connection Failed
- Verify `serviceAccountKey.json` is in the correct location
- Check Wi-Fi connection
- Confirm Firebase URL in settings

### OCR Accuracy Issues
- Ensure adequate lighting on meter display
- Check camera focus distance
- Review Roboflow model predictions

## Performance Metrics
- Average inference time: 2-3 seconds
- Image capture: ~1 second
- Firebase sync: <1 second
- Total cycle time: ~4-5 seconds (configurable)

## Future Enhancements
- [ ] Multi-meter support
- [ ] ML-based anomaly detection
- [ ] Historical trend analysis
- [ ] Mobile app integration
- [ ] Predictive billing forecasts

## License
MIT License - See LICENSE file for details

## Contact
For issues or contributions, please open a GitHub issue.
