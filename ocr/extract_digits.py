"""OCR and digit extraction from Roboflow predictions."""

import re
from typing import Tuple, Set, List, Dict


def assemble_digits(predictions: List[Dict], img_height: int = 480) -> Tuple[str, Set[str]]:
    """
    Assemble detected digits into a single reading string.
    
    Args:
        predictions: List of prediction dicts from Roboflow
        img_height: Height of image (used for edge filtering)
    
    Returns:
        Tuple of (assembled_string, detected_classes_set)
    """
    if not predictions or not isinstance(predictions, list):
        return "", set()

    valid = []
    detected_classes = set()

    # Constants for edge noise rejection
    MIN_Y_PIXELS = 50
    MAX_Y_PIXELS = 910
    KWH_MIN_CONFIDENCE = 0.05  # Low threshold for labels
    DIGIT_MIN_CONFIDENCE = 0.15  # Strict threshold for digits

    for p in predictions:
        if not isinstance(p, dict):
            continue

        cls = str(p.get('class', '')).strip().lower()
        conf = float(p.get('confidence', 0))
        x = float(p.get('x', 0))
        y = float(p.get('y', 0))
        w = float(p.get('width', 0))

        # Reject edge noise
        if y < MIN_Y_PIXELS or y > MAX_Y_PIXELS:
            continue

        # Track detected classes (for filtering)
        if conf >= KWH_MIN_CONFIDENCE:
            detected_classes.add(cls)

        # Only keep digit predictions with strict confidence
        if cls not in '0123456789.' or conf < DIGIT_MIN_CONFIDENCE:
            continue

        # Calculate left edge for left-to-right sorting
        left = x - w / 2
        valid.append((left, cls))

    if len(valid) < 3:
        return "", detected_classes

    # Sort left-to-right
    valid.sort(key=lambda t: t[0])
    text = ''.join([c for _, c in valid])

    # Cleanup: collapse 3+ identical consecutive digits (LCD ghosting artifacts)
    text = re.sub(r'(\d)\1{2,}', r'\1\1', text)
    
    # Cleanup: multiple consecutive dots
    text = re.sub(r'\.{2,}', '.', text)
    
    return text, detected_classes


def extract_value(reading: str, decimal_shift: int = 2) -> float:
    """
    Extract numeric value from assembled reading string.
    
    Args:
        reading: Assembled digit string (e.g., "12345")
        decimal_shift: Number of decimal places to shift right
    
    Returns:
        Parsed float value, or None if invalid
    """
    if not reading or len(reading) < 3:
        return None

    numbers = re.findall(r"\d+\.?\d*", reading)
    if not numbers:
        return None

    # Get longest number (most likely the meter reading)
    num_str = max(numbers, key=len)

    try:
        if '.' in num_str:
            units = float(num_str)
        elif decimal_shift > 0:
            units = float(num_str) / (10 ** decimal_shift)
        else:
            units = float(num_str)
        
        return units
    except ValueError:
        return None


def validate_reading(units: float) -> bool:
    """
    Validate if meter reading is within realistic bounds.
    
    Args:
        units: Meter reading in kWh
    
    Returns:
        True if valid, False otherwise
    """
    if units is None:
        return False
    
    return 0.1 <= units <= 999999


def check_forbidden_labels(detected_classes: Set[str]) -> bool:
    """
    Check if forbidden power labels are detected (kW, W, A, etc.)
    Indicates meter is showing power, not energy.
    
    Args:
        detected_classes: Set of detected class labels
    
    Returns:
        True if forbidden labels found, False otherwise
    """
    forbidden = {'kw', 'w', 'a', 'amps', 'volts', 'v'}
    return bool(detected_classes.intersection(forbidden))


def check_kwh_label(detected_classes: Set[str]) -> bool:
    """
    Check if 'kWh' label is detected (energy reading).
    
    Args:
        detected_classes: Set of detected class labels
    
    Returns:
        True if kWh found, False otherwise
    """
    return 'kwh' in detected_classes
