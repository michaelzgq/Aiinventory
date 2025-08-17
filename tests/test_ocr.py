import pytest
import numpy as np
from backend.app.utils.ocr import BinOCRDetector, is_valid_bin_id


class TestBinOCRDetector:
    def setup_method(self):
        self.detector = BinOCRDetector()
    
    def test_init(self):
        """Test BinOCRDetector initialization"""
        assert self.detector is not None
    
    def test_find_bin_pattern(self):
        """Test bin ID pattern detection"""
        test_cases = [
            ("A54", "A54"),
            ("Bin A54 Location", "A54"),
            ("S-01", "S-01"),
            ("Staging S-02", "S-02"),
            ("BIN-A54", "BIN-A54"),
            ("LOC-B123", "LOC-B123"),
            ("Random text", None),
            ("", None),
        ]
        
        for text, expected in test_cases:
            result = self.detector._find_bin_pattern(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_preprocess_for_ocr(self):
        """Test OCR preprocessing"""
        # Create a test image
        image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        processed = self.detector.preprocess_for_ocr(image)
        
        assert processed is not None
        assert processed.shape == image.shape
        assert processed.dtype == np.uint8
    
    @pytest.mark.parametrize("bin_id,expected", [
        ("A54", True),
        ("B123", True),
        ("S-01", True),
        ("S-02", True),
        ("BIN-A54", True),
        ("LOC-B123", True),
        ("A54A", True),
        ("BC123", True),
        ("", False),
        ("A", False),
        ("123", False),
        ("ABCD", False),
        ("A1234", False),
        ("invalid-bin", False),
    ])
    def test_is_valid_bin_id(self, bin_id, expected):
        """Test bin ID validation"""
        assert is_valid_bin_id(bin_id) == expected


class TestOCRProcessing:
    def test_extract_bin_from_image_empty(self):
        """Test handling of empty image bytes"""
        from backend.app.utils.ocr import extract_bin_from_image
        
        bin_id, confidence = extract_bin_from_image(b"")
        assert bin_id is None
        assert confidence == 0.0
    
    def test_extract_bin_from_image_invalid(self):
        """Test handling of invalid image data"""
        from backend.app.utils.ocr import extract_bin_from_image
        
        bin_id, confidence = extract_bin_from_image(b"invalid_image_data")
        assert bin_id is None
        assert confidence == 0.0