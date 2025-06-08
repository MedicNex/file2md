from .base import BaseParser
from loguru import logger
import subprocess
import tempfile
import os
import zipfile
import xml.etree.ElementTree as ET
import re

class OdtParser(BaseParser):
    """ODT文档解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.odt']
    
    async def parse(self, file_path: str) -> str:
        """解析ODT文件"""
        try:
            # 首先尝试使用pandoc转换
            content = await self._pandoc_parse(file_path)
            if content:
                return content
            
            # 如果pandoc失败，使用内置解析器
            return await self._internal_parse(file_path)
                
        except Exception as e:
            logger.error(f"解析ODT文件失败 {file_path}: {e}")
            raise Exception(f"ODT文件解析错误: {str(e)}")
    
    async def _pandoc_parse(self, file_path: str) -> str:
        """使用pandoc解析ODT文件"""
        try:
            # 创建临时输出文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
                temp_md_path = temp_md.name
            
            self.temp_files.append(temp_md_path)
            
            # 使用pandoc转换ODT到Markdown
            result = subprocess.run([
                'pandoc', 
                file_path,
                '-t', 'markdown',
                '-o', temp_md_path,
                '--wrap=none'  # 不自动换行
            ], capture_output=True, text=True, check=True)
            
            # 读取转换后的Markdown内容
            with open(temp_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"使用pandoc成功解析ODT文件: {file_path}")
            return content.strip()
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Pandoc转换ODT失败: {e}")
            return None
        except FileNotFoundError:
            logger.warning("Pandoc未安装，使用内置解析器")
            return None
    
    async def _internal_parse(self, file_path: str) -> str:
        """内置ODT解析器"""
        try:
            # ODT是ZIP格式，解压获取content.xml
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # 读取content.xml
                content_xml = zip_file.read('content.xml').decode('utf-8')
                
            # 解析XML内容
            root = ET.fromstring(content_xml)
            
            # 定义OpenDocument命名空间
            namespaces = {
                'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
            }
            
            # 提取文本内容
            content_parts = []
            
            # 查找文档正文
            body = root.find('.//office:body/office:text', namespaces)
            if body is not None:
                content_parts.extend(self._extract_text_elements(body, namespaces))
            
            # 组合内容
            content = '\n\n'.join(content_parts)
            
            # 清理多余的空行
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            logger.info(f"使用内置解析器成功解析ODT文件: {file_path}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"内置ODT解析失败: {e}")
            raise Exception(f"ODT文件解析错误: {str(e)}")
    
    def _extract_text_elements(self, element, namespaces):
        """递归提取文本元素"""
        content_parts = []
        
        for child in element:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if tag_name == 'h':  # 标题
                level = child.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}outline-level', '1')
                text = self._get_element_text(child)
                if text.strip():
                    content_parts.append(f"{'#' * int(level)} {text.strip()}")
            
            elif tag_name == 'p':  # 段落
                text = self._get_element_text(child)
                if text.strip():
                    content_parts.append(text.strip())
            
            elif tag_name == 'list':  # 列表
                list_items = self._extract_list_items(child, namespaces)
                if list_items:
                    content_parts.extend(list_items)
            
            elif tag_name == 'table':  # 表格
                table_content = self._extract_table(child, namespaces)
                if table_content:
                    content_parts.append(table_content)
            
            else:
                # 递归处理其他元素
                sub_content = self._extract_text_elements(child, namespaces)
                content_parts.extend(sub_content)
        
        return content_parts
    
    def _get_element_text(self, element):
        """获取元素的文本内容"""
        text_parts = []
        
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            if child.text:
                text_parts.append(child.text)
            if child.tail:
                text_parts.append(child.tail)
        
        if element.tail:
            text_parts.append(element.tail)
        
        return ''.join(text_parts)
    
    def _extract_list_items(self, list_element, namespaces):
        """提取列表项"""
        items = []
        
        for item in list_element.findall('.//text:list-item', namespaces):
            text = self._get_element_text(item)
            if text.strip():
                items.append(f"- {text.strip()}")
        
        return items
    
    def _extract_table(self, table_element, namespaces):
        """提取表格内容"""
        try:
            rows = []
            
            for row in table_element.findall('.//table:table-row', namespaces):
                cells = []
                for cell in row.findall('.//table:table-cell', namespaces):
                    cell_text = self._get_element_text(cell)
                    cells.append(cell_text.strip() if cell_text else '')
                
                if cells and any(cell for cell in cells):
                    rows.append('| ' + ' | '.join(cells) + ' |')
            
            if rows:
                # 添加表格头分隔符
                if len(rows) > 1:
                    header_separator = '| ' + ' | '.join(['---'] * len(rows[0].split('|')[1:-1])) + ' |'
                    rows.insert(1, header_separator)
                
                return '\n'.join(rows)
        
        except Exception as e:
            logger.warning(f"表格提取失败: {e}")
        
        return None 