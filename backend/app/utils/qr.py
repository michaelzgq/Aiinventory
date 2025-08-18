"""
QR Code and Barcode Detection using OpenCV
支持 QR 码和一维码识别
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import base64

logger = logging.getLogger(__name__)


class QRCodeDetector:
    """QR 码和一维码检测器"""
    
    def __init__(self):
        """初始化检测器"""
        self.qr_detector = cv2.QRCodeDetector()
        self.zbar_detector = None
        
        # 尝试导入 zbar 用于一维码检测
        try:
            import pyzbar
            self.zbar_detector = pyzbar
            logger.info("ZBar 一维码检测器已启用")
        except ImportError:
            logger.warning("ZBar 未安装，一维码检测功能受限")
    
    def detect_qr_codes(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        检测图像中的 QR 码
        
        Args:
            image: OpenCV 图像数组
            
        Returns:
            检测结果列表，每个包含 text, bbox, confidence
        """
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
                        confidence = self._calculate_confidence(gray, bbox)
                        
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
        """
        检测图像中的一维码
        
        Args:
            image: OpenCV 图像数组
            
        Returns:
            检测结果列表
        """
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
                confidence = self._calculate_confidence(gray, bbox)
                
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
        """
        检测图像中的所有码（QR + 一维码）
        
        Args:
            image: OpenCV 图像数组
            
        Returns:
            所有检测结果
        """
        qr_results = self.detect_qr_codes(image)
        barcode_results = self.detect_barcodes(image)
        
        # 合并结果，按置信度排序
        all_results = qr_results + barcode_results
        all_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return all_results
    
    def detect_from_file(self, image_path: str) -> List[Dict[str, Any]]:
        """
        从文件路径检测码
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            检测结果列表
        """
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
        """
        从 base64 字符串检测码
        
        Args:
            base64_string: base64 编码的图像数据
            
        Returns:
            检测结果列表
        """
        try:
            # 解码 base64
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
        """将点坐标转换为边界框"""
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        return {
            'x': int(min(x_coords)),
            'y': int(min(y_coords)),
            'width': int(max(x_coords) - min(x_coords)),
            'height': int(max(y_coords) - min(y_coords))
        }
    
    def _zbar_bbox_to_bbox(self, rect) -> Dict[str, int]:
        """将 ZBar 矩形转换为边界框"""
        return {
            'x': rect.left,
            'y': rect.top,
            'width': rect.width,
            'height': rect.height
        }
    
    def _calculate_confidence(self, gray_image: np.ndarray, bbox: Dict[str, int]) -> float:
        """
        计算检测结果的置信度
        
        Args:
            gray_image: 灰度图像
            bbox: 边界框
            
        Returns:
            置信度 (0.0 - 1.0)
        """
        try:
            # 提取边界框区域
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            
            # 边界检查
            if x < 0 or y < 0 or x + w > gray_image.shape[1] or y + h > gray_image.shape[0]:
                return 0.5  # 边界越界，中等置信度
            
            roi = gray_image[y:y+h, x:x+w]
            
            # 计算图像质量指标
            # 1. 对比度
            contrast = np.std(roi)
            
            # 2. 清晰度（拉普拉斯方差）
            laplacian = cv2.Laplacian(roi, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # 3. 亮度
            brightness = np.mean(roi)
            
            # 归一化指标
            contrast_norm = min(contrast / 50.0, 1.0)  # 对比度越高越好
            sharpness_norm = min(sharpness / 100.0, 1.0)  # 清晰度越高越好
            brightness_norm = 1.0 - abs(brightness - 128) / 128  # 亮度接近中等最好
            
            # 综合置信度
            confidence = (contrast_norm * 0.4 + sharpness_norm * 0.4 + brightness_norm * 0.2)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"置信度计算失败: {e}")
            return 0.5  # 默认中等置信度
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像增强，提高码的识别率
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 1. 直方图均衡化
            enhanced = cv2.equalizeHist(gray)
            
            # 2. 高斯模糊去噪
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # 3. 锐化
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            # 4. 对比度增强
            enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"图像增强失败: {e}")
            return image


# 全局检测器实例
qr_detector = QRCodeDetector()


def detect_codes_from_image(image_data: bytes, enhance: bool = True) -> List[Dict[str, Any]]:
    """
    从图像数据检测码的便捷函数
    
    Args:
        image_data: 图像字节数据
        enhance: 是否进行图像增强
        
    Returns:
        检测结果列表
    """
    try:
        # 转换为 numpy 数组
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error("无法解码图像数据")
            return []
        
        # 图像增强
        if enhance:
            image = qr_detector.enhance_image(image)
        
        # 检测码
        results = qr_detector.detect_all_codes(image)
        
        logger.info(f"检测到 {len(results)} 个码")
        return results
        
    except Exception as e:
        logger.error(f"图像码检测失败: {e}")
        return []


def validate_qr_content(text: str) -> bool:
    """
    验证 QR 码内容是否符合预期格式
    
    Args:
        text: QR 码文本内容
        
    Returns:
        是否符合格式
    """
    if not text:
        return False
    
    # 检查是否为托盘号格式 (PALT-XXXX)
    if text.startswith('PALT-') and len(text) == 9:
        return True
    
    # 检查是否为 SKU 格式 (SKU-XXXX)
    if text.startswith('SKU-') and len(text) == 7:
        return True
    
    # 检查是否为库位号格式 (A54, S-01)
    if (len(text) == 3 and text[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' and text[1:].isdigit()) or \
       (len(text) == 4 and text[0] == 'S' and text[1] == '-' and text[2:].isdigit()):
        return True
    
    # 其他格式暂时接受
    return True