from .base import BaseParser
from loguru import logger
import zipfile
import os
import tempfile
import json
import plistlib
from xml.etree import ElementTree as ET

class KeynoteParser(BaseParser):
    """Keynote (.key) 文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.key']
    
    async def parse(self, file_path: str) -> str:
        """解析Keynote文件"""
        try:
            # Keynote文件实际上是一个ZIP包
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_parts = []
                
                # 尝试读取预览内容
                try:
                    preview_content = self._extract_preview_content(zip_file)
                    if preview_content:
                        content_parts.append(preview_content)
                except Exception as e:
                    logger.warning(f"提取Keynote预览内容失败: {e}")
                
                # 尝试从metadata.plist读取基本信息
                try:
                    metadata_content = self._extract_metadata_content(zip_file)
                    if metadata_content:
                        content_parts.append(metadata_content)
                except Exception as e:
                    logger.warning(f"提取Keynote元数据失败: {e}")
                
                # 尝试从buildVersionHistory.plist读取版本信息
                try:
                    version_content = self._extract_version_content(zip_file)
                    if version_content:
                        content_parts.append(version_content)
                except Exception as e:
                    logger.warning(f"提取Keynote版本信息失败: {e}")
                
                # 获取文件列表信息
                file_list = self._get_file_structure(zip_file)
                if file_list:
                    content_parts.append(f"## 文件结构\n{file_list}")
            
            # 如果没有提取到任何内容，返回基本信息
            if not content_parts:
                content_parts.append("Keynote演示文稿文件 - 暂无可提取的文本内容")
                content_parts.append("这是一个Apple Keynote演示文稿文件，包含幻灯片内容")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```slideshow\n{raw_content}\n```"
            
            logger.info(f"成功解析Keynote文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析Keynote文件失败 {file_path}: {e}")
            raise Exception(f"Keynote文件解析错误: {str(e)}")
    
    def _extract_preview_content(self, zip_file: zipfile.ZipFile) -> str:
        """提取预览内容"""
        try:
            # 查找预览文件
            preview_files = [f for f in zip_file.namelist() if 'preview' in f.lower() and f.endswith('.jpg')]
            if preview_files:
                return f"## 预览\n包含 {len(preview_files)} 个预览图片"
        except Exception:
            pass
        return ""
    
    def _extract_metadata_content(self, zip_file: zipfile.ZipFile) -> str:
        """提取元数据内容"""
        try:
            if 'metadata.plist' in zip_file.namelist():
                metadata_data = zip_file.read('metadata.plist')
                metadata = plistlib.loads(metadata_data)
                
                content_parts = ["## 文档信息"]
                
                if 'BNDocumentMetadata' in metadata:
                    doc_meta = metadata['BNDocumentMetadata']
                    if 'BNTitle' in doc_meta:
                        content_parts.append(f"**标题**: {doc_meta['BNTitle']}")
                    if 'BNAuthor' in doc_meta:
                        content_parts.append(f"**作者**: {doc_meta['BNAuthor']}")
                
                if 'BNApplicationVersion' in metadata:
                    content_parts.append(f"**创建版本**: {metadata['BNApplicationVersion']}")
                
                return '\n'.join(content_parts)
        except Exception:
            pass
        return ""
    
    def _extract_version_content(self, zip_file: zipfile.ZipFile) -> str:
        """提取版本信息"""
        try:
            if 'buildVersionHistory.plist' in zip_file.namelist():
                version_data = zip_file.read('buildVersionHistory.plist')
                version_info = plistlib.loads(version_data)
                
                if isinstance(version_info, list) and version_info:
                    latest_version = version_info[0]
                    if 'BNBuildVersion' in latest_version:
                        return f"## 版本信息\n**构建版本**: {latest_version['BNBuildVersion']}"
        except Exception:
            pass
        return ""
    
    def _get_file_structure(self, zip_file: zipfile.ZipFile) -> str:
        """获取文件结构信息"""
        try:
            files = zip_file.namelist()
            
            # 统计不同类型的文件
            iwa_files = [f for f in files if f.endswith('.iwa')]
            image_files = [f for f in files if any(f.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif'])]
            
            structure_info = []
            structure_info.append(f"- 总文件数: {len(files)}")
            structure_info.append(f"- IWA数据文件: {len(iwa_files)}")
            structure_info.append(f"- 图片文件: {len(image_files)}")
            
            # 显示主要目录
            directories = set()
            for file in files:
                if '/' in file:
                    directories.add(file.split('/')[0])
            
            if directories:
                structure_info.append(f"- 主要目录: {', '.join(sorted(directories))}")
            
            return '\n'.join(structure_info)
        except Exception:
            return "" 