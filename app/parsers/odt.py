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
            # 安全性检查
            if not self._validate_file_security(file_path):
                raise Exception("文件安全验证失败")
                
            # 首先尝试使用pandoc转换
            content = await self._pandoc_parse(file_path)
            if content:
                return self._sanitize_content(content)
            
            # 如果pandoc失败，使用内置解析器
            content = await self._internal_parse(file_path)
            return self._sanitize_content(content)
                
        except Exception as e:
            logger.error(f"解析ODT文件失败 {file_path}: {e}")
            raise Exception(f"ODT文件解析错误: {str(e)}")
    
    async def _pandoc_parse(self, file_path: str) -> str:
        """使用pandoc解析ODT文件"""
        try:
            # 创建临时输出文件，指定UTF-8编码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md_path = temp_md.name
            
            self.temp_files.append(temp_md_path)
            
            # 使用pandoc转换ODT到Markdown
            result = subprocess.run([
                'pandoc', 
                os.path.abspath(file_path),  # 使用绝对路径防止路径遍历
                '-t', 'markdown',
                '-o', temp_md_path,
                '--wrap=none',  # 不自动换行
                '--sandbox'  # 启用沙箱模式
            ], capture_output=True, text=True, check=True, timeout=30)  # 添加超时
            
            # 读取转换后的Markdown内容
            with open(temp_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"使用pandoc成功解析ODT文件: {file_path}")
            return content.strip()
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Pandoc转换ODT超时: {file_path}")
            return None
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
    
    def _validate_file_security(self, file_path: str) -> bool:
        """验证文件安全性"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小（限制为50MB）
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                logger.error(f"文件过大: {file_size} bytes")
                return False
            
            # 检查文件路径，防止路径遍历攻击
            abs_path = os.path.abspath(file_path)
            if '..' in file_path or abs_path != os.path.normpath(abs_path):
                logger.error(f"检测到可疑文件路径: {file_path}")
                return False
            
            # 验证ZIP文件结构（ODT是ZIP格式）
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # 检查是否包含必要的ODT文件
                    if 'content.xml' not in zip_file.namelist():
                        logger.error("无效的ODT文件结构")
                        return False
            except zipfile.BadZipFile:
                logger.error("文件不是有效的ZIP/ODT格式")
                return False
            
            return True
        except Exception as e:
            logger.error(f"文件安全验证失败: {e}")
            return False
    
    def _sanitize_content(self, content: str) -> str:
        """清理内容，防止注入攻击"""
        if not content:
            return content
        
        # 限制内容长度
        if len(content) > 1000000:  # 1MB 文本限制
            content = content[:1000000] + "\n\n... (内容被截断，超过限制)"
        
        # 清理潜在的markdown注入
        content = content.replace('```', '\\`\\`\\`')
        
        # 清理HTML标签（保留基本格式）
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content