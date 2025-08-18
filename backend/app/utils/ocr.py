"""
OCR Library for Bin Location Recognition using PaddleOCR
库位号 OCR 识别工具
"""

import logging
from typing import List, Dict, Any, Optional
import re
from pathlib import Path
import base64

logger = logging.getLogger(__name__)

# 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
    logger.info("PaddleOCR 已启用")
except ImportError:
    PADDLE_OCR_AVAILABLE = False
    logger.warning("PaddleOCR 未安装，OCR 功能将使用备用方案")


class BinOCRProcessor:
    """库位号 OCR 识别处理器"""
    
    def __init__(self, use_paddle_ocr: bool = True):
        """
        初始化 OCR 处理器
        
        Args:
            use_paddle_ocr: 是否使用 PaddleOCR
        """
        self.use_paddle_ocr = use_paddle_ocr and PADDLE_OCR_AVAILABLE
        self.paddle_ocr = None
        
        if self.use_paddle_ocr:
            try:
                # 初始化 PaddleOCR，使用中文模型
                self.paddle_ocr = PaddleOCR(
                    use_angle_cls=True,  # 使用角度分类器
                    lang='ch',  # 中文模型
                    use_gpu=False,  # CPU 模式
                    show_log=False  # 不显示日志
                )
                logger.info("PaddleOCR 初始化成功")
            except Exception as e:
                logger.error(f"PaddleOCR 初始化失败: {e}")
                self.use_paddle_ocr = False
                self.paddle_ocr = None
    
    def extract_bin_id_from_text(self, text: str) -> Optional[str]:
        """
        从文本中提取库位号
        
        Args:
            text: OCR 识别的文本
            
        Returns:
            提取的库位号，如果没有找到返回 None
        """
        if not text:
            return None
        
        # 清理文本
        text = text.strip().upper()
        
        # 库位号模式匹配
        bin_patterns = [
            # 标准库位格式：A54, B12, C08
            r'^[A-Z]\d{1,2}$',
            # 出库区格式：S-01, S-02
            r'^S-\d{1,2}$',
            # 带前缀的格式：BIN-A54, LOC-B12
            r'(?:BIN|LOC)[-_]([A-Z]\d{1,2})$',
            # 带后缀的格式：A54-BIN, B12-LOC
            r'^([A-Z]\d{1,2})(?:[-_]BIN|[-_]LOC)$',
            # 包含空格的格式：A 54, B 12
            r'^([A-Z])\s*(\d{1,2})$'
        ]
        
        # 尝试直接匹配
        for pattern in bin_patterns:
            match = re.match(pattern, text)
            if match:
                if len(match.groups()) > 0:
                    # 处理带前缀或后缀的情况
                    if ' ' in text:
                        # 处理空格分隔的情况
                        return f"{match.group(1)}{match.group(2)}"
                    else:
                        return match.group(1)
                else:
                    return text
        
        # 如果没有直接匹配，尝试从文本中提取
        # 查找可能的库位号
        potential_bins = re.findall(r'[A-Z]\d{1,2}', text)
        if potential_bins:
            return potential_bins[0]
        
        # 查找出库区格式
        staging_bins = re.findall(r'S-\d{1,2}', text)
        if staging_bins:
            return staging_bins[0]
        
        return None
    
    def process_ocr_result(self, ocr_result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理 OCR 识别结果，提取库位号
        
        Args:
            ocr_result: PaddleOCR 的识别结果
            
        Returns:
            处理后的结果列表
        """
        processed_results = []
        
        for item in ocr_result:
            text = item.get('text', '')
            confidence = item.get('confidence', 0.0)
            bbox = item.get('bbox', [])
            
            # 提取库位号
            bin_id = self.extract_bin_id_from_text(text)
            
            if bin_id:
                processed_results.append({
                    'text': text,
                    'bin_id': bin_id,
                    'confidence': confidence,
                    'bbox': bbox,
                    'type': 'bin_location'
                })
                logger.info(f"OCR 识别到库位号: {bin_id}, 原文: {text}, 置信度: {confidence:.2f}")
        
        return processed_results
    
    def recognize_bin_from_image(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        从图像识别库位号
        
        Args:
            image_data: 图像字节数据
            
        Returns:
            识别结果列表
        """
        if not self.use_paddle_ocr or not self.paddle_ocr:
            logger.warning("PaddleOCR 不可用，使用备用方案")
            return self._fallback_bin_recognition(image_data)
        
        try:
            # 使用 PaddleOCR 识别
            ocr_result = self.paddle_ocr.ocr(image_data, cls=True)
            
            if not ocr_result or not ocr_result[0]:
                logger.info("OCR 未识别到任何文本")
                return []
            
            # 处理识别结果
            results = []
            for line in ocr_result[0]:
                if len(line) >= 2:
                    text = line[1][0]  # 识别的文本
                    confidence = line[1][1]  # 置信度
                    bbox = line[0]  # 边界框
                    
                    # 提取库位号
                    bin_id = self.extract_bin_id_from_text(text)
                    
                    if bin_id:
                        results.append({
                            'text': text,
                            'bin_id': bin_id,
                            'confidence': confidence,
                            'bbox': bbox,
                            'type': 'bin_location'
                        })
                        logger.info(f"OCR 识别到库位号: {bin_id}, 原文: {text}, 置信度: {confidence:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"PaddleOCR 识别失败: {e}")
            return self._fallback_bin_recognition(image_data)
    
    def _fallback_bin_recognition(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        备用库位识别方案（当 PaddleOCR 不可用时）
        
        Args:
            image_data: 图像字节数据
            
        Returns:
            识别结果列表
        """
        logger.info("使用备用库位识别方案")
        
        # 这里可以实现其他 OCR 方案，比如 Tesseract
        # 或者返回空结果，提示用户手动输入
        return []
    
    def validate_bin_id(self, bin_id: str) -> bool:
        """
        验证库位号格式是否正确
        
        Args:
            bin_id: 库位号
            
        Returns:
            格式是否正确
        """
        if not bin_id:
            return False
        
        # 标准库位格式：A54, B12, C08
        if re.match(r'^[A-Z]\d{1,2}$', bin_id):
            return True
        
        # 出库区格式：S-01, S-02
        if re.match(r'^S-\d{1,2}$', bin_id):
            return True
        
        return False
    
    def get_bin_zone(self, bin_id: str) -> str:
        """
        根据库位号获取区域信息
        
        Args:
            bin_id: 库位号
            
        Returns:
            区域信息
        """
        if not bin_id:
            return "unknown"
        
        # 标准库位：A54 -> A区, B12 -> B区
        if re.match(r'^[A-Z]\d{1,2}$', bin_id):
            return f"{bin_id[0]}区"
        
        # 出库区：S-01 -> 出库区
        if bin_id.startswith('S-'):
            return "出库区"
        
        return "其他"
    
    def suggest_bin_id(self, partial_text: str) -> List[str]:
        """
        根据部分文本建议可能的库位号
        
        Args:
            partial_text: 部分文本
            
        Returns:
            建议的库位号列表
        """
        suggestions = []
        
        if not partial_text:
            return suggestions
        
        partial_text = partial_text.strip().upper()
        
        # 如果输入的是单个字母，建议数字
        if len(partial_text) == 1 and partial_text.isalpha():
            for i in range(1, 61):  # A01-A60
                suggestions.append(f"{partial_text}{i:02d}")
        
        # 如果输入的是字母+部分数字
        elif len(partial_text) >= 2 and partial_text[0].isalpha():
            if partial_text[1:].isdigit():
                # 已经是完整格式
                suggestions.append(partial_text)
            else:
                # 部分数字，建议补全
                base = partial_text[0]
                partial_num = partial_text[1:]
                if partial_num.isdigit():
                    for i in range(int(partial_num) * 10, min(int(partial_num) * 10 + 10, 61)):
                        suggestions.append(f"{base}{i:02d}")
        
        # 出库区建议
        if partial_text.startswith('S'):
            for i in range(1, 11):  # S-01 到 S-10
                suggestions.append(f"S-{i:02d}")
        
        return suggestions[:10]  # 限制建议数量


# 全局 OCR 处理器实例
bin_ocr_processor = BinOCRProcessor()


def recognize_bin_from_image_data(image_data: bytes, use_paddle_ocr: bool = True) -> List[Dict[str, Any]]:
    """
    从图像数据识别库位号的便捷函数
    
    Args:
        image_data: 图像字节数据
        use_paddle_ocr: 是否使用 PaddleOCR
        
    Returns:
        识别结果列表
    """
    processor = BinOCRProcessor(use_paddle_ocr=use_paddle_ocr)
    return processor.recognize_bin_from_image(image_data)


def extract_bin_id_from_text(text: str) -> Optional[str]:
    """
    从文本中提取库位号的便捷函数
    
    Args:
        text: 文本内容
        
    Returns:
        提取的库位号
    """
    processor = BinOCRProcessor()
    return processor.extract_bin_id_from_text(text)


def validate_bin_id_format(bin_id: str) -> bool:
    """
    验证库位号格式的便捷函数
    
    Args:
        bin_id: 库位号
        
    Returns:
        格式是否正确
    """
    processor = BinOCRProcessor()
    return processor.validate_bin_id(bin_id)