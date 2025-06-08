from .base import BaseParser
from loguru import logger
import docx
from markdownify import markdownify
import io

class DocxParser(BaseParser):
    """DOCX文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.docx']
    
    async def parse(self, file_path: str) -> str:
        """解析DOCX文件"""
        try:
            doc = docx.Document(file_path)
            
            # 提取所有段落文本
            content_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # 处理不同的段落样式
                    text = paragraph.text.strip()
                    
                    # 检查是否是标题
                    if paragraph.style.name.startswith('Heading'):
                        level = int(paragraph.style.name.split()[-1])
                        text = f"{'#' * level} {text}"
                    
                    content_parts.append(text)
            
            # 处理表格
            for table in doc.tables:
                content_parts.append(self._parse_table(table))
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content}\n```"
            
            logger.info(f"成功解析DOCX文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析DOCX文件失败 {file_path}: {e}")
            raise Exception(f"DOCX文件解析错误: {str(e)}")
    
    def _parse_table(self, table) -> str:
        """解析表格为Markdown格式"""
        try:
            rows = []
            for i, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                if i == 0:
                    # 表头
                    rows.append('| ' + ' | '.join(cells) + ' |')
                    rows.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
                else:
                    # 数据行
                    rows.append('| ' + ' | '.join(cells) + ' |')
            
            return '\n'.join(rows)
        except Exception as e:
            logger.warning(f"表格解析失败: {e}")
            return "[表格解析失败]" 