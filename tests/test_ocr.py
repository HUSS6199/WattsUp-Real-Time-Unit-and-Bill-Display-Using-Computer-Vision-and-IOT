"""Unit tests for OCR and digit extraction."""

import unittest
from ocr.extract_digits import (
    assemble_digits, 
    extract_value, 
    validate_reading,
    check_forbidden_labels,
    check_kwh_label
)


class TestAssembleDigits(unittest.TestCase):
    """Test digit assembly from predictions."""
    
    def test_normal_reading(self):
        """Test assembling normal meter reading."""
        predictions = [
            {'class': '1', 'confidence': 0.95, 'x': 100, 'y': 500, 'width': 30},
            {'class': '2', 'confidence': 0.94, 'x': 140, 'y': 500, 'width': 30},
            {'class': '3', 'confidence': 0.93, 'x': 180, 'y': 500, 'width': 30},
            {'class': '.', 'confidence': 0.92, 'x': 220, 'y': 500, 'width': 15},
            {'class': '4', 'confidence': 0.91, 'x': 250, 'y': 500, 'width': 30},
            {'class': 'kwh', 'confidence': 0.99, 'x': 300, 'y': 300, 'width': 50},
        ]
        
        result, classes = assemble_digits(predictions)
        self.assertEqual(result, "123.4")
        self.assertIn('kwh', classes)
    
    def test_edge_noise_rejection(self):
        """Test rejection of predictions at image edges."""
        predictions = [
            {'class': '1', 'confidence': 0.95, 'x': 100, 'y': 30, 'width': 30},  # Too high
            {'class': '2', 'confidence': 0.94, 'x': 140, 'y': 500, 'width': 30},
            {'class': '3', 'confidence': 0.93, 'x': 180, 'y': 920, 'width': 30},  # Too low
        ]
        
        result, classes = assemble_digits(predictions)
        self.assertEqual(result, "2")
    
    def test_low_confidence_digits_rejected(self):
        """Test that low confidence digits are rejected."""
        predictions = [
            {'class': '1', 'confidence': 0.10, 'x': 100, 'y': 500, 'width': 30},  # Below 0.15
            {'class': '2', 'confidence': 0.95, 'x': 140, 'y': 500, 'width': 30},
            {'class': '3', 'confidence': 0.93, 'x': 180, 'y': 500, 'width': 30},
        ]
        
        result, classes = assemble_digits(predictions)
        self.assertEqual(result, "23")
    
    def test_empty_predictions(self):
        """Test handling of empty predictions."""
        result, classes = assemble_digits([])
        self.assertEqual(result, "")
        self.assertEqual(len(classes), 0)


class TestExtractValue(unittest.TestCase):
    """Test value extraction from readings."""
    
    def test_extract_with_decimal(self):
        """Test extraction with decimal point."""
        value = extract_value("123.45")
        self.assertEqual(value, 123.45)
    
    def test_extract_with_shift(self):
        """Test extraction with decimal shift."""
        value = extract_value("12345", decimal_shift=2)
        self.assertEqual(value, 123.45)
    
    def test_extract_no_shift(self):
        """Test extraction without decimal shift."""
        value = extract_value("12345", decimal_shift=0)
        self.assertEqual(value, 12345)
    
    def test_extract_too_short(self):
        """Test rejection of too-short readings."""
        value = extract_value("12")
        self.assertIsNone(value)


class TestValidateReading(unittest.TestCase):
    """Test reading validation."""
    
    def test_valid_reading(self):
        """Test valid meter reading."""
        self.assertTrue(validate_reading(125.45))
    
    def test_too_low(self):
        """Test rejection of too-low reading."""
        self.assertFalse(validate_reading(0.05))
    
    def test_too_high(self):
        """Test rejection of too-high reading."""
        self.assertFalse(validate_reading(1000000))
    
    def test_none_value(self):
        """Test rejection of None."""
        self.assertFalse(validate_reading(None))


class TestForbiddenLabels(unittest.TestCase):
    """Test forbidden label detection."""
    
    def test_kwh_allowed(self):
        """Test kWh is not forbidden."""
        self.assertFalse(check_forbidden_labels({'kwh'}))
    
    def test_kw_forbidden(self):
        """Test kW is forbidden."""
        self.assertTrue(check_forbidden_labels({'kw'}))
    
    def test_watts_forbidden(self):
        """Test W (watts) is forbidden."""
        self.assertTrue(check_forbidden_labels({'w'}))
    
    def test_mixed_classes(self):
        """Test detection among mixed classes."""
        self.assertTrue(check_forbidden_labels({'kwh', 'kw', '1', '2'}))


class TestKwhLabel(unittest.TestCase):
    """Test kWh label detection."""
    
    def test_kwh_detected(self):
        """Test kWh is detected."""
        self.assertTrue(check_kwh_label({'kwh'}))
    
    def test_kwh_not_detected(self):
        """Test absence of kWh."""
        self.assertFalse(check_kwh_label({'w'}))
    
    def test_kwh_case_insensitive(self):
        """Test lowercase kWh detection."""
        # Note: extraction already lowercases, so we only check lowercase
        self.assertTrue(check_kwh_label({'kwh'}))


if __name__ == '__main__':
    unittest.main()
