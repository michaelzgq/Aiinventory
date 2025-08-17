import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class QRCodeDetector:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
    
    def decode_qr_codes(self, image: np.ndarray) -> List[str]:
        """Decode QR codes from image using OpenCV"""
        try:
            retval, decoded_info, points, _ = self.detector.detectAndDecodeMulti(image)
            if retval:
                return [info for info in decoded_info if info.strip()]
            return []
        except Exception as e:
            logger.error(f"QR decoding error: {e}")
            return []
    
    def decode_single_qr(self, image: np.ndarray) -> Optional[str]:
        """Decode single QR code from image"""
        try:
            retval, decoded_info, points = self.detector.detectAndDecode(image)
            if retval and decoded_info.strip():
                return decoded_info.strip()
            return None
        except Exception as e:
            logger.error(f"Single QR decoding error: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better QR detection"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Adaptive threshold for better contrast
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image
    
    def decode_with_preprocessing(self, image: np.ndarray) -> List[str]:
        """Try multiple preprocessing approaches for QR detection"""
        results = []
        
        # Try original image
        codes = self.decode_qr_codes(image)
        results.extend(codes)
        
        # Try preprocessed image
        if not results:
            processed = self.preprocess_image(image)
            codes = self.decode_qr_codes(processed)
            results.extend(codes)
        
        # Try different rotations if still no results
        if not results:
            for angle in [90, 180, 270]:
                rotated = self._rotate_image(image, angle)
                codes = self.decode_qr_codes(rotated)
                results.extend(codes)
                if results:
                    break
        
        return list(set(results))  # Remove duplicates
    
    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by given angle"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (width, height))


def decode_image_bytes(image_bytes: bytes) -> Tuple[List[str], float]:
    """Decode QR codes from image bytes and return confidence score"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return [], 0.0
        
        detector = QRCodeDetector()
        codes = detector.decode_with_preprocessing(image)
        
        # Simple confidence calculation based on number of codes found
        confidence = min(1.0, len(codes) * 0.5) if codes else 0.0
        
        return codes, confidence
    
    except Exception as e:
        logger.error(f"Error decoding image bytes: {e}")
        return [], 0.0


def is_valid_item_id(code: str) -> bool:
    """Check if decoded string looks like a valid item ID"""
    if not code or len(code) < 4:
        return False
    
    # Basic validation - starts with known prefixes
    valid_prefixes = ["PALT-", "ITEM-", "SKU-", "LOT-"]
    return any(code.startswith(prefix) for prefix in valid_prefixes) or code.isalnum()


def filter_item_codes(codes: List[str]) -> List[str]:
    """Filter codes to only return valid item IDs"""
    return [code for code in codes if is_valid_item_id(code)]