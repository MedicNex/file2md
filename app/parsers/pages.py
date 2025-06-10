from .base import BaseParser
from loguru import logger
import zipfile
import os
import tempfile
import json
import plistlib
from xml.etree import ElementTree as ET

class PagesParser(BaseParser):
    """Pages (.pages) 文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.pages']
    
    async def parse(self, file_path: str) -> str:
        """解析Pages文件"""
        try:
            # 安全性检查
            if not self._validate_archive_security(file_path):
                raise Exception("存档文件安全验证失败")
                
            # Pages文件实际上是一个ZIP包
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_parts = []
                
                # 尝试读取预览内容
                try:
                    preview_content = self._extract_preview_content(zip_file)
                    if preview_content:
                        content_parts.append(preview_content)
                except Exception as e:
                    logger.warning(f"提取Pages预览内容失败: {e}")
                
                # 尝试从metadata.plist读取基本信息
                try:
                    metadata_content = self._extract_metadata_content(zip_file)
                    if metadata_content:
                        content_parts.append(metadata_content)
                except Exception as e:
                    logger.warning(f"提取Pages元数据失败: {e}")
                
                # 尝试从buildVersionHistory.plist读取版本信息
                try:
                    version_content = self._extract_version_content(zip_file)
                    if version_content:
                        content_parts.append(version_content)
                except Exception as e:
                    logger.warning(f"提取Pages版本信息失败: {e}")
                
                # 获取文件列表信息
                file_list = self._get_file_structure(zip_file)
                if file_list:
                    content_parts.append(f"## 文件结构\n{file_list}")
            
            # 如果没有提取到任何内容，返回基本信息
            if not content_parts:
                content_parts.append("Pages文档文件 - 暂无可提取的文本内容")
                content_parts.append("这是一个Apple Pages文字处理文档，包含格式化文本内容")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content}\n```"
            
            logger.info(f"成功解析Pages文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析Pages文件失败 {file_path}: {e}")
            raise Exception(f"Pages文件解析错误: {str(e)}")
    
    def _validate_archive_security(self, file_path: str) -> bool:
        """验证存档文件安全性"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小（限制为100MB）
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:
                logger.error(f"Pages文件过大: {file_size} bytes")
                return False
                
            # 检查是否为有效的ZIP文件
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # 检查ZIP文件内容总大小（解压后）
                    total_size = 0
                    for info in zip_file.infolist():
                        # 防止路径遍历攻击
                        if os.path.isabs(info.filename) or '..' in info.filename:
                            logger.error(f"检测到可疑文件路径: {info.filename}")
                            return False
                        
                        # 检查单个文件大小
                        if info.file_size > 50 * 1024 * 1024:  # 50MB限制
                            logger.error(f"存档中文件过大: {info.filename} ({info.file_size} bytes)")
                            return False
                            
                        total_size += info.file_size
                        
                        # 检查总解压大小（防止ZIP炸弹）
                        if total_size > 500 * 1024 * 1024:  # 500MB限制
                            logger.error(f"存档解压后总大小过大: {total_size} bytes")
                            return False
                    
                    # 检查文件数量
                    if len(zip_file.infolist()) > 10000:
                        logger.error("存档包含过多文件")
                        return False
                        
            except zipfile.BadZipFile:
                logger.error("文件不是有效的ZIP格式")
                return False
            
            return True
        except Exception as e:
            logger.error(f"存档安全验证失败: {e}")
            return False
    
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
                    if 'BNSubject' in doc_meta:
                        content_parts.append(f"**主题**: {doc_meta['BNSubject']}")
                    if 'BNKeywords' in doc_meta:
                        content_parts.append(f"**关键词**: {', '.join(doc_meta['BNKeywords'])}")
                
                if 'BNApplicationVersion' in metadata:
                    content_parts.append(f"**创建版本**: {metadata['BNApplicationVersion']}")
                
                if 'BNDocumentWordCount' in metadata:
                    content_parts.append(f"**字数统计**: {metadata['BNDocumentWordCount']}")
                
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