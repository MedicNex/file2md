from .base import BaseParser
from loguru import logger
import zipfile
import os
import tempfile
import json
import plistlib
from xml.etree import ElementTree as ET

class NumbersParser(BaseParser):
    """Numbers (.numbers) 文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.numbers']
    
    async def parse(self, file_path: str) -> str:
        """解析Numbers文件"""
        try:
            # 首先尝试使用numbers-parser库
            try:
                return await self._parse_with_numbers_parser(file_path)
            except (ImportError, ModuleNotFoundError) as e:
                logger.info(f"numbers-parser库不可用，使用基础解析: {e}")
                return await self._parse_basic(file_path)
            except Exception as e:
                logger.warning(f"numbers-parser解析失败，回退到基础解析: {e}")
                return await self._parse_basic(file_path)
            
        except Exception as e:
            logger.error(f"解析Numbers文件失败 {file_path}: {e}")
            raise Exception(f"Numbers文件解析错误: {str(e)}")
    
    async def _parse_with_numbers_parser(self, file_path: str) -> str:
        """使用numbers-parser库解析"""
        try:
            # 尝试导入numbers-parser库
            from numbers_parser import Document
            
            # 解析Numbers文档
            doc = Document(file_path)
            content_parts = []
            
            # 添加文档基本信息
            content_parts.append("## Numbers电子表格")
            
            # 遍历所有表格
            for sheet_idx, sheet in enumerate(doc.sheets, 1):
                sheet_parts = [f"### 表格 {sheet_idx}: {sheet.name}"]
                
                # 遍历表格中的所有表
                for table_idx, table in enumerate(sheet.tables, 1):
                    table_parts = [f"#### 表 {table_idx} ({table.num_rows}行 x {table.num_cols}列)"]
                    
                    # 提取表格数据
                    try:
                        # 获取表头
                        if table.num_rows > 0:
                            headers = []
                            for col in range(min(table.num_cols, 10)):  # 限制列数
                                try:
                                    cell_value = table.cell(0, col).value
                                    headers.append(str(cell_value) if cell_value is not None else "")
                                except:
                                    headers.append("")
                            
                            if any(headers):
                                table_parts.append(f"**表头**: {' | '.join(headers)}")
                        
                        # 获取少量数据示例
                        data_rows = []
                        for row in range(1, min(table.num_rows, 6)):  # 最多5行数据
                            row_data = []
                            for col in range(min(table.num_cols, 10)):  # 限制列数
                                try:
                                    cell_value = table.cell(row, col).value
                                    row_data.append(str(cell_value) if cell_value is not None else "")
                                except:
                                    row_data.append("")
                            data_rows.append(' | '.join(row_data))
                        
                        if data_rows:
                            table_parts.append("**数据示例**:")
                            table_parts.extend(data_rows)
                            if table.num_rows > 6:
                                table_parts.append(f"... (还有 {table.num_rows - 6} 行数据)")
                    
                    except Exception as e:
                        table_parts.append(f"*表格数据提取失败: {e}*")
                    
                    sheet_parts.append('\n'.join(table_parts))
                
                content_parts.append('\n\n'.join(sheet_parts))
            
            if not content_parts or len(content_parts) == 1:
                content_parts.append("Numbers文件解析完成，但未找到可显示的表格数据")
            
            raw_content = '\n\n---\n\n'.join(content_parts)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```sheet\n{raw_content}\n```"
            
            logger.info(f"成功使用numbers-parser解析Numbers文件: {file_path}")
            return markdown_content
            
        except ImportError:
            logger.warning("numbers-parser库未安装，使用基础解析方法")
            raise Exception("numbers-parser not available")
    
    async def _parse_basic(self, file_path: str) -> str:
        """基础解析方法"""
        try:
            # Numbers文件实际上是一个ZIP包
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_parts = []
                
                # 尝试读取预览内容
                try:
                    preview_content = self._extract_preview_content(zip_file)
                    if preview_content:
                        content_parts.append(preview_content)
                except Exception as e:
                    logger.warning(f"提取Numbers预览内容失败: {e}")
                
                # 尝试从metadata.plist读取基本信息
                try:
                    metadata_content = self._extract_metadata_content(zip_file)
                    if metadata_content:
                        content_parts.append(metadata_content)
                except Exception as e:
                    logger.warning(f"提取Numbers元数据失败: {e}")
                
                # 尝试从buildVersionHistory.plist读取版本信息
                try:
                    version_content = self._extract_version_content(zip_file)
                    if version_content:
                        content_parts.append(version_content)
                except Exception as e:
                    logger.warning(f"提取Numbers版本信息失败: {e}")
                
                # 获取文件列表信息
                file_list = self._get_file_structure(zip_file)
                if file_list:
                    content_parts.append(f"## 文件结构\n{file_list}")
            
            # 如果没有提取到任何内容，返回基本信息
            if not content_parts:
                content_parts.append("Numbers电子表格文件 - 暂无可提取的数据内容")
                content_parts.append("这是一个Apple Numbers电子表格文件，包含表格和数据")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```sheet\n{raw_content}\n```"
            
            logger.info(f"成功基础解析Numbers文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"基础解析Numbers文件失败 {file_path}: {e}")
            raise
    
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