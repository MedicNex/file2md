from .base import BaseParser
from loguru import logger
import mammoth
from markdownify import markdownify

class DocParser(BaseParser):
    """DOC文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.doc']
    
    async def parse(self, file_path: str) -> str:
        """解析DOC文件"""
        try:
            # 使用mammoth将DOC转换为HTML
            with open(file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value
                
                # 记录警告信息
                if result.messages:
                    for message in result.messages:
                        logger.warning(f"DOC转换警告: {message}")
            
            # 将HTML转换为Markdown
            raw_content = markdownify(html_content, heading_style="ATX")
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content.strip()}\n```"
            
            logger.info(f"成功解析DOC文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析DOC文件失败 {file_path}: {e}")
            raise Exception(f"DOC文件解析错误: {str(e)}") 