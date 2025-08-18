"""
Storage Management for Inventory AI
支持本地文件存储和 S3 对象存储
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import mimetypes
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class StorageManager:
    """存储管理器"""
    
    def __init__(self, storage_backend: str = "local", 
                 local_dir: str = "./storage",
                 s3_config: Optional[Dict[str, str]] = None):
        """
        初始化存储管理器
        
        Args:
            storage_backend: 存储后端类型 ("local" 或 "s3")
            local_dir: 本地存储目录
            s3_config: S3 配置信息
        """
        self.storage_backend = storage_backend
        self.local_dir = Path(local_dir)
        self.s3_config = s3_config or {}
        
        # 初始化存储
        self._initialize_storage()
    
    def _initialize_storage(self):
        """初始化存储系统"""
        if self.storage_backend == "local":
            self._init_local_storage()
        elif self.storage_backend == "s3":
            self._init_s3_storage()
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _init_local_storage(self):
        """初始化本地存储"""
        try:
            # 创建存储目录结构
            directories = [
                self.local_dir / "photos",
                self.local_dir / "reports",
                self.local_dir / "temp",
                self.local_dir / "labels"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建存储目录: {directory}")
            
            logger.info(f"本地存储初始化完成: {self.local_dir}")
            
        except Exception as e:
            logger.error(f"本地存储初始化失败: {e}")
            raise
    
    def _init_s3_storage(self):
        """初始化 S3 存储"""
        try:
            # 这里可以添加 S3 客户端初始化代码
            # 暂时使用本地存储作为备用
            logger.warning("S3 存储暂未实现，使用本地存储作为备用")
            self.storage_backend = "local"
            self._init_local_storage()
            
        except Exception as e:
            logger.error(f"S3 存储初始化失败: {e}")
            # 回退到本地存储
            self.storage_backend = "local"
            self._init_local_storage()
    
    def save_file(self, file_data: bytes, filename: str, 
                  subdirectory: str = "", 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        保存文件
        
        Args:
            file_data: 文件数据
            filename: 文件名
            subdirectory: 子目录
            metadata: 元数据
            
        Returns:
            文件引用路径
        """
        if self.storage_backend == "local":
            return self._save_file_local(file_data, filename, subdirectory, metadata)
        elif self.storage_backend == "s3":
            return self._save_file_s3(file_data, filename, subdirectory, metadata)
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _save_file_local(self, file_data: bytes, filename: str, 
                         subdirectory: str = "", 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """本地保存文件"""
        try:
            # 构建文件路径
            if subdirectory:
                file_dir = self.local_dir / subdirectory
                file_dir.mkdir(parents=True, exist_ok=True)
            else:
                file_dir = self.local_dir
            
            # 生成唯一文件名
            unique_filename = self._generate_unique_filename(filename)
            file_path = file_dir / unique_filename
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 保存元数据（如果有）
            if metadata:
                metadata_path = file_path.with_suffix('.json')
                import json
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 返回相对路径作为引用
            relative_path = str(file_path.relative_to(self.local_dir))
            logger.info(f"文件保存成功: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"本地文件保存失败: {e}")
            raise
    
    def _save_file_s3(self, file_data: bytes, filename: str, 
                      subdirectory: str = "", 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """S3 保存文件（暂未实现）"""
        # TODO: 实现 S3 文件保存
        logger.warning("S3 存储暂未实现，回退到本地存储")
        return self._save_file_local(file_data, filename, subdirectory, metadata)
    
    def get_file(self, file_ref: str) -> Optional[bytes]:
        """
        获取文件内容
        
        Args:
            file_ref: 文件引用路径
            
        Returns:
            文件数据，如果不存在返回 None
        """
        if self.storage_backend == "local":
            return self._get_file_local(file_ref)
        elif self.storage_backend == "s3":
            return self._get_file_s3(file_ref)
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _get_file_local(self, file_ref: str) -> Optional[bytes]:
        """本地获取文件"""
        try:
            file_path = self.local_dir / file_ref
            
            if not file_path.exists():
                logger.warning(f"文件不存在: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"本地文件读取失败: {e}")
            return None
    
    def _get_file_s3(self, file_ref: str) -> Optional[bytes]:
        """S3 获取文件（暂未实现）"""
        logger.warning("S3 存储暂未实现，回退到本地存储")
        return self._get_file_local(file_ref)
    
    def get_file_url(self, file_ref: str) -> Optional[str]:
        """
        获取文件访问 URL
        
        Args:
            file_ref: 文件引用路径
            
        Returns:
            文件访问 URL
        """
        if self.storage_backend == "local":
            return self._get_file_url_local(file_ref)
        elif self.storage_backend == "s3":
            return self._get_file_url_s3(file_ref)
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _get_file_url_local(self, file_ref: str) -> Optional[str]:
        """本地文件 URL"""
        # 本地存储返回相对路径
        return f"/storage/{file_ref}"
    
    def _get_file_url_s3(self, file_ref: str) -> Optional[str]:
        """S3 文件 URL（暂未实现）"""
        # TODO: 实现 S3 文件 URL 生成
        logger.warning("S3 存储暂未实现，回退到本地存储")
        return self._get_file_url_local(file_ref)
    
    def delete_file(self, file_ref: str) -> bool:
        """
        删除文件
        
        Args:
            file_ref: 文件引用路径
            
        Returns:
            是否删除成功
        """
        if self.storage_backend == "local":
            return self._delete_file_local(file_ref)
        elif self.storage_backend == "s3":
            return self._delete_file_s3(file_ref)
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _delete_file_local(self, file_ref: str) -> bool:
        """本地删除文件"""
        try:
            file_path = self.local_dir / file_ref
            
            if not file_path.exists():
                logger.warning(f"文件不存在，无法删除: {file_path}")
                return False
            
            # 删除主文件
            file_path.unlink()
            
            # 删除元数据文件（如果存在）
            metadata_path = file_path.with_suffix('.json')
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.info(f"文件删除成功: {file_ref}")
            return True
            
        except Exception as e:
            logger.error(f"本地文件删除失败: {e}")
            return False
    
    def _delete_file_s3(self, file_ref: str) -> bool:
        """S3 删除文件（暂未实现）"""
        logger.warning("S3 存储暂未实现，回退到本地存储")
        return self._delete_file_local(file_ref)
    
    def list_files(self, subdirectory: str = "") -> List[Dict[str, Any]]:
        """
        列出目录中的文件
        
        Args:
            subdirectory: 子目录
            
        Returns:
            文件信息列表
        """
        if self.storage_backend == "local":
            return self._list_files_local(subdirectory)
        elif self.storage_backend == "s3":
            return self._list_files_s3(subdirectory)
        else:
            raise ValueError(f"不支持的存储后端: {self.storage_backend}")
    
    def _list_files_local(self, subdirectory: str = "") -> List[Dict[str, Any]]:
        """本地列出文件"""
        try:
            if subdirectory:
                dir_path = self.local_dir / subdirectory
            else:
                dir_path = self.local_dir
            
            if not dir_path.exists():
                return []
            
            files = []
            for file_path in dir_path.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'path': str(file_path.relative_to(self.local_dir))
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"本地文件列表获取失败: {e}")
            return []
    
    def _list_files_s3(self, subdirectory: str = "") -> List[Dict[str, Any]]:
        """S3 列出文件（暂未实现）"""
        logger.warning("S3 存储暂未实现，回退到本地存储")
        return self._list_files_local(subdirectory)
    
    def _generate_unique_filename(self, filename: str) -> str:
        """生成唯一文件名"""
        # 获取文件扩展名
        name, ext = os.path.splitext(filename)
        
        # 添加时间戳和哈希值确保唯一性
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(f"{filename}_{timestamp}".encode()).hexdigest()[:8]
        
        return f"{name}_{timestamp}_{hash_suffix}{ext}"
    
    def get_file_info(self, file_ref: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_ref: 文件引用路径
            
        Returns:
            文件信息字典
        """
        try:
            file_path = self.local_dir / file_ref
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            # 获取 MIME 类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # 获取元数据（如果存在）
            metadata = {}
            metadata_path = file_path.with_suffix('.json')
            if metadata_path.exists():
                import json
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"元数据读取失败: {e}")
            
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'mime_type': mime_type or 'application/octet-stream',
                'metadata': metadata,
                'path': str(file_path.relative_to(self.local_dir))
            }
            
        except Exception as e:
            logger.error(f"文件信息获取失败: {e}")
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        清理临时文件
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的文件数量
        """
        try:
            temp_dir = self.local_dir / "temp"
            if not temp_dir.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            cleaned_count = 0
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.info(f"清理临时文件: {file_path.name}")
                        except Exception as e:
                            logger.warning(f"临时文件清理失败: {file_path.name}, 错误: {e}")
            
            logger.info(f"临时文件清理完成，共清理 {cleaned_count} 个文件")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"临时文件清理失败: {e}")
            return 0


# 全局存储管理器实例
storage_manager = StorageManager()


def get_storage_manager() -> StorageManager:
    """获取存储管理器实例"""
    return storage_manager


def save_image_file(image_data: bytes, filename: str, 
                   subdirectory: str = "photos") -> str:
    """
    保存图像文件的便捷函数
    
    Args:
        image_data: 图像数据
        filename: 文件名
        subdirectory: 子目录
        
    Returns:
        文件引用路径
    """
    return storage_manager.save_file(image_data, filename, subdirectory)


def get_image_url(file_ref: str) -> Optional[str]:
    """
    获取图像 URL 的便捷函数
    
    Args:
        file_ref: 文件引用路径
        
    Returns:
        图像访问 URL
    """
    return storage_manager.get_file_url(file_ref)