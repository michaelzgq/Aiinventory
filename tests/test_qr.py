import pytest
import numpy as np
import cv2
from backend.app.utils.qr import QRCodeDetector, is_valid_item_id, filter_item_codes


class TestQRCodeDetector:
    def setup_method(self):
        self.detector = QRCodeDetector()
    
    def test_init(self):
        """Test QRCodeDetector initialization"""
        assert self.detector is not None
        assert hasattr(self.detector, 'detector')
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create a simple test image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[25:75, 25:75] = [255, 255, 255]  # White square
        
        processed = self.detector.preprocess_image(image)
        
        assert processed is not None
        assert len(processed.shape) == 2  # Should be grayscale
        assert processed.dtype == np.uint8
    
    def test_rotate_image(self):
        """Test image rotation"""
        image = np.zeros((100, 100), dtype=np.uint8)
        image[10:20, 10:90] = 255  # Horizontal line
        
        rotated = self.detector._rotate_image(image, 90)
        
        assert rotated.shape == image.shape
        assert rotated.dtype == image.dtype
    
    @pytest.mark.parametrize("item_id,expected", [
        ("PALT-0001", True),
        ("ITEM-12345", True),
        ("SKU-ABC123", True),
        ("LOT-XYZ789", True),
        ("ABC123DEF", True),
        ("", False),
        ("A", False),
        ("AB", False),
        ("XYZ", False),
        ("invalid-id", False),
    ])
    def test_is_valid_item_id(self, item_id, expected):
        """Test item ID validation"""
        assert is_valid_item_id(item_id) == expected
    
    def test_filter_item_codes(self):
        """Test filtering of item codes"""
        codes = ["PALT-0001", "invalid", "ITEM-123", "xyz", "SKU-ABC", ""]
        filtered = filter_item_codes(codes)
        
        expected = ["PALT-0001", "ITEM-123", "SKU-ABC"]
        assert filtered == expected


class TestQRProcessing:
    def test_decode_image_bytes_empty(self):
        """Test handling of empty image bytes"""
        from backend.app.utils.qr import decode_image_bytes
        
        codes, confidence = decode_image_bytes(b"")
        assert codes == []
        assert confidence == 0.0
    
    def test_decode_image_bytes_invalid(self):
        """Test handling of invalid image data"""
        from backend.app.utils.qr import decode_image_bytes
        
        codes, confidence = decode_image_bytes(b"invalid_image_data")
        assert codes == []
        assert confidence == 0.0
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        detector = QRCodeDetector()
        
        # Test with no codes
        confidence = detector._calculate_confidence(0.0, 0.0, 0, False)
        assert confidence == 0.0
        
        # Test with QR codes found
        confidence = detector._calculate_confidence(0.8, 0.0, 2, True)
        assert confidence > 0.8
        
        # Test with OCR detection
        confidence = detector._calculate_confidence(0.5, 0.7, 1, True)
        assert confidence >= 0.5