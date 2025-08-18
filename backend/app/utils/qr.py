"""
QR Code and Barcode Detection using OpenCV
支持 QR 码和一维码识别
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import base64
import re

logger = logging.getLogger(__name__)

# 尝试导入 OpenCV
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    logger.info("OpenCV 已启用")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV 未安装，QR 检测功能将使用备用方案")
    # 创建虚拟 numpy 以避免导入错误
    class DummyNumpy:
        def __array__(self): return []
        def __getitem__(self, key): return self
        def __setitem__(self, key, value): pass
        def shape(self): return (0,)
        def dtype(self): return 'uint8'
        def astype(self, dtype): return self
    np = DummyNumpy()


class QRCodeDetector:
	"""QR 码和一维码检测器"""
	
	def __init__(self):
		"""初始化检测器"""
		if not OPENCV_AVAILABLE:
			logger.warning("OpenCV 不可用，QR 检测器将使用备用方案")
			self.qr_detector = None
			self.detector = None
			return
			
		self.qr_detector = cv2.QRCodeDetector()
		self.zbar_detector = None
		# 向后兼容：tests 里会检查 `.detector`
		self.detector = self.qr_detector
		
		# 尝试导入 zbar 用于一维码检测
		try:
			import pyzbar
			self.zbar_detector = pyzbar
			logger.info("ZBar 一维码检测器已启用")
		except ImportError:
			logger.warning("ZBar 未安装，一维码检测功能受限")
	
	def detect_qr_codes(self, image: np.ndarray) -> List[Dict[str, Any]]:
		"""检测图像中的 QR 码"""
		if not OPENCV_AVAILABLE:
			logger.warning("OpenCV 不可用，无法检测 QR 码")
			return []
			
		try:
			# 转换为灰度图
			if len(image.shape) == 3:
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			else:
				gray = image
			
			# 使用 OpenCV 检测 QR 码
			retval, decoded_info, points, straight_qrcode = self.qr_detector.detectAndDecodeMulti(gray)
			
			results = []
			if retval:
				for i, (text, point, straight) in enumerate(zip(decoded_info, points, straight_qrcode)):
					if text:  # 只返回成功解码的
						# 计算边界框
						bbox = self._points_to_bbox(point)
						confidence = self._calculate_region_confidence(gray, bbox)
						
						results.append({
							'text': text,
							'bbox': bbox,
							'confidence': confidence,
							'type': 'qr',
							'index': i
						})
						logger.info(f"检测到 QR 码: {text}, 置信度: {confidence:.2f}")
			
			return results
			
		except Exception as e:
			logger.error(f"QR 码检测失败: {e}")
			return []
	
	def detect_barcodes(self, image: np.ndarray) -> List[Dict[str, Any]]:
		"""检测图像中的一维码"""
		if not OPENCV_AVAILABLE:
			return []
			
		if not self.zbar_detector:
			return []
		
		try:
			# 转换为灰度图
			if len(image.shape) == 3:
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			else:
				gray = image
			
			# 使用 ZBar 检测一维码
			barcodes = self.zbar_detector.pyzbar.decode(gray)
			
			results = []
			for barcode in barcodes:
				text = barcode.data.decode('utf-8')
				bbox = self._zbar_bbox_to_bbox(barcode.rect)
				confidence = self._calculate_region_confidence(gray, bbox)
				
				results.append({
					'text': text,
					'bbox': bbox,
					'confidence': confidence,
					'type': 'barcode',
					'format': barcode.type
				})
				logger.info(f"检测到一维码: {text}, 格式: {barcode.type}, 置信度: {confidence:.2f}")
			
			return results
			
		except Exception as e:
			logger.error(f"一维码检测失败: {e}")
			return []
	
	def detect_all_codes(self, image: np.ndarray) -> List[Dict[str, Any]]:
		"""检测图像中的所有码（QR + 一维码）"""
		if not OPENCV_AVAILABLE:
			return []
		qr_results = self.detect_qr_codes(image)
		barcode_results = self.detect_barcodes(image)
		all_results = qr_results + barcode_results
		all_results.sort(key=lambda x: x['confidence'], reverse=True)
		return all_results
	
	# 兼容旧 tests：预处理应返回灰度 uint8
	def preprocess_image(self, image: np.ndarray) -> np.ndarray:
		if not OPENCV_AVAILABLE:
			return image
		try:
			if len(image.shape) == 3:
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			else:
				gray = image
			# 轻度模糊 + 自适应阈值，提升对比度
			blurred = cv2.GaussianBlur(gray, (3, 3), 0)
			thresh = cv2.adaptiveThreshold(
				blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
			)
			return thresh
		except Exception as e:
			logger.error(f"Image preprocessing error: {e}")
			return image
	
	def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
		if not OPENCV_AVAILABLE:
			return image
		try:
			height, width = image.shape[:2]
			center = (width // 2, height // 2)
			matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
			return cv2.warpAffine(image, matrix, (width, height))
		except Exception as e:
			logger.error(f"Image rotation error: {e}")
			return image
	
	def _calculate_region_confidence(self, gray_image: np.ndarray, bbox: Dict[str, int]) -> float:
		"""根据图像区域质量估计置信度，用于检测结果"""
		if not OPENCV_AVAILABLE:
			return 0.5
		try:
			x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
			if x < 0 or y < 0 or x + w > gray_image.shape[1] or y + h > gray_image.shape[0]:
				return 0.5
			roi = gray_image[y:y+h, x:x+w]
			contrast = np.std(roi)
			sharpness = np.var(cv2.Laplacian(roi, cv2.CV_64F))
			brightness = np.mean(roi)
			contrast_norm = min(contrast / 50.0, 1.0)
			sharpness_norm = min(sharpness / 100.0, 1.0)
			brightness_norm = 1.0 - abs(brightness - 128) / 128
			confidence = (contrast_norm * 0.4 + sharpness_norm * 0.4 + brightness_norm * 0.2)
			return max(0.0, min(1.0, confidence))
		except Exception:
			return 0.5
	
	# 兼容旧 tests：计算综合置信度的旧接口
	def _calculate_confidence(self, qr_confidence: float, ocr_confidence: float, item_count: int, has_bin_id: bool) -> float:
		base_confidence = qr_confidence
		if item_count > 0:
			base_confidence = min(1.0, base_confidence + (item_count * 0.1))
		if has_bin_id:
			base_confidence = min(1.0, base_confidence + 0.2)
		if ocr_confidence > 0:
			base_confidence = min(1.0, (base_confidence + ocr_confidence) / 2)
		return round(base_confidence, 2)
	
	def detect_from_file(self, image_path: str) -> List[Dict[str, Any]]:
		if not OPENCV_AVAILABLE:
			return []
		try:
			image = cv2.imread(image_path)
			if image is None:
				logger.error(f"无法读取图像文件: {image_path}")
				return []
			return self.detect_all_codes(image)
		except Exception as e:
			logger.error(f"从文件检测失败: {e}")
			return []
	
	def detect_from_base64(self, base64_string: str) -> List[Dict[str, Any]]:
		if not OPENCV_AVAILABLE:
			return []
		try:
			image_data = base64.b64decode(base64_string)
			nparr = np.frombuffer(image_data, np.uint8)
			image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
			if image is None:
				logger.error("无法解码 base64 图像数据")
				return []
			return self.detect_all_codes(image)
		except Exception as e:
			logger.error(f"从 base64 检测失败: {e}")
			return []
	
	def _points_to_bbox(self, points: np.ndarray) -> Dict[str, int]:
		if not OPENCV_AVAILABLE:
			return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
		x_coords = [p[0] for p in points]
		y_coords = [p[1] for p in points]
		return {
			'x': int(min(x_coords)),
			'y': int(min(y_coords)),
			'width': int(max(x_coords) - min(x_coords)),
			'height': int(max(y_coords) - min(y_coords))
		}
	
	def _zbar_bbox_to_bbox(self, rect) -> Dict[str, int]:
		if not OPENCV_AVAILABLE:
			return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
		return {
			'x': rect.left,
			'y': rect.top,
			'width': rect.width,
			'height': rect.height
		}


# 便捷函数：从图像字节中检测码（新接口）
def detect_codes_from_image(image_data: bytes, enhance: bool = True) -> List[Dict[str, Any]]:
	if not OPENCV_AVAILABLE:
		logger.warning("OpenCV 不可用，无法检测图像中的码")
		return []
	try:
		nparr = np.frombuffer(image_data, np.uint8)
		image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		if image is None:
			logger.error("无法解码图像数据")
			return []
		# 图像增强
		if enhance:
			# 使用与 preprocess 相同的增强逻辑
			detector = QRCodeDetector()
			image = detector.preprocess_image(image)
		# 检测
		detector = QRCodeDetector()
		results = detector.detect_all_codes(image)
		logger.info(f"检测到 {len(results)} 个码")
		return results
	except Exception as e:
		logger.error(f"图像码检测失败: {e}")
		return []


# 兼容旧 tests：返回 (codes, confidence)
def decode_image_bytes(image_bytes: bytes) -> Tuple[List[str], float]:
	if not OPENCV_AVAILABLE:
		return [], 0.0
	try:
		if not image_bytes:
			return [], 0.0
		nparr = np.frombuffer(image_bytes, np.uint8)
		image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		if image is None:
			return [], 0.0
		detector = QRCodeDetector()
		results = detector.detect_all_codes(image)
		codes = [r['text'] for r in results if r.get('text')]
		confidence = min(1.0, len(codes) * 0.5) if codes else 0.0
		return codes, confidence
	except Exception as e:
		logger.error(f"Error decoding image bytes: {e}")
		return [], 0.0


# 兼容旧 tests：物品 ID 校验与过滤
def is_valid_item_id(code: str) -> bool:
	if not code or len(code) < 4:
		return False
	# 标准前缀
	if re.match(r'^PALT-\d+', code):
		return True
	if re.match(r'^ITEM-\d+', code):
		return True
	if re.match(r'^SKU-[A-Z]+\d*$', code):
		return True
	if re.match(r'^LOT-[A-Z0-9]+$', code):
		return True
	# 纯大写字母数字，长度>=4
	if code.isalnum() and code.isupper() and len(code) >= 4:
		return True
	return False


def filter_item_codes(codes: List[str]) -> List[str]:
	return [c for c in codes if is_valid_item_id(c)]


# 兼容：保持旧函数名
def validate_qr_content(text: str) -> bool:
	return is_valid_item_id(text) or bool(re.match(r'^[A-Z]\d{1,2}$', text)) or bool(re.match(r'^S-\d{1,2}$', text))