import re
from typing import Optional, Tuple
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Check for OpenCV availability
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available")

# Try to import PaddleOCR
PADDLE_OCR_AVAILABLE = False
try:
    if settings.use_paddle_ocr and OPENCV_AVAILABLE:
        from paddleocr import PaddleOCR
        PADDLE_OCR_AVAILABLE = True
        logger.info("PaddleOCR initialized successfully")
except ImportError:
    logger.warning("PaddleOCR not available, falling back to basic text detection")


class BinOCRDetector:
    def __init__(self):
        self.ocr_engine = None
        if PADDLE_OCR_AVAILABLE:
            try:
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    show_log=False
                )
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr_engine = None
    
    def extract_bin_id(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """Extract bin ID from image using OCR"""
        if self.ocr_engine is None:
            return None, 0.0
        
        try:
            # Run OCR
            results = self.ocr_engine.ocr(image, cls=True)
            
            if not results or not results[0]:
                return None, 0.0
            
            # Extract text and find bin ID patterns
            all_text = []
            confidences = []
            
            for line in results[0]:
                if len(line) >= 2:
                    text = line[1][0]
                    conf = line[1][1]
                    all_text.append(text)
                    confidences.append(conf)
            
            # Look for bin ID patterns
            bin_id = self._find_bin_pattern(' '.join(all_text))
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return bin_id, avg_confidence
        
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return None, 0.0
    
    def _find_bin_pattern(self, text: str) -> Optional[str]:
        """Find bin ID pattern in OCR text"""
        text = text.upper().strip()
        
        # Pattern 1: Letter followed by numbers (A54, B12, etc.)
        pattern1 = re.search(r'\b([A-Z]\d{1,3})\b', text)
        if pattern1:
            return pattern1.group(1)
        
        # Pattern 2: S- prefix for staging bins (S-01, S-02, etc.)
        pattern2 = re.search(r'\b(S-\d{1,2})\b', text)
        if pattern2:
            return pattern2.group(1)
        
        # Pattern 3: Multi-character prefix (BIN-123, LOC-A54, etc.)
        pattern3 = re.search(r'\b([A-Z]{2,4}-[A-Z0-9]{1,4})\b', text)
        if pattern3:
            return pattern3.group(1)
        
        # Pattern 4: Simple alphanumeric (if it looks like a bin)
        pattern4 = re.search(r'\b([A-Z]{1,2}\d{1,3}[A-Z]?)\b', text)
        if pattern4:
            return pattern4.group(1)
        
        return None
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Sharpen
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            return sharpened
        
        except Exception as e:
            logger.error(f"OCR preprocessing error: {e}")
            return image


def extract_bin_from_image(image_bytes: bytes) -> Tuple[Optional[str], float]:
    """Extract bin ID from image bytes"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return None, 0.0
        
        detector = BinOCRDetector()
        
        # Try original image first
        bin_id, confidence = detector.extract_bin_id(image)
        
        # Try preprocessed image if first attempt failed
        if not bin_id or confidence < 0.5:
            processed = detector.preprocess_for_ocr(image)
            bin_id_2, confidence_2 = detector.extract_bin_id(processed)
            if confidence_2 > confidence:
                bin_id, confidence = bin_id_2, confidence_2
        
        return bin_id, confidence
    
    except Exception as e:
        logger.error(f"Error extracting bin from image: {e}")
        return None, 0.0


def is_valid_bin_id(bin_id: str) -> bool:
    """Validate if string looks like a valid bin ID"""
    if not bin_id:
        return False
    
    bin_id = bin_id.upper().strip()
    
    # Check against known staging bins
    if bin_id in settings.staging_bins_list:
        return True
    
    # Pattern validation
    patterns = [
        r'^[A-Z]\d{1,3}$',          # A54, B12
        r'^S-\d{1,2}$',             # S-01, S-02
        r'^[A-Z]{2,4}-[A-Z0-9]{1,4}$',  # BIN-A54
        r'^[A-Z]{1,2}\d{1,3}[A-Z]?$'   # A54A, BC123
    ]
    
    return any(re.match(pattern, bin_id) for pattern in patterns)