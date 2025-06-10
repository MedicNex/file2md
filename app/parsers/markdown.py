from .base import BaseParser
from loguru import logger
import chardet

class MarkdownParser(BaseParser):
    """Markdown文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.md', '.markdown']
    
    async def parse(self, file_path: str) -> str:
        """解析Markdown文件，保持原有格式"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected_encoding = chardet.detect(raw_data)
                encoding = detected_encoding.get('encoding') or 'utf-8'
                confidence = detected_encoding.get('confidence', 0)
                
                logger.info(f"检测到Markdown文件编码: {encoding} (置信度: {confidence:.2f})")
            
            # 使用更robust的编码读取策略
            content = None
            encodings_to_try = [encoding, 'utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for try_encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=try_encoding) as f:
                        content = f.read()
                    logger.info(f"成功使用编码 {try_encoding} 读取Markdown文件")
                    break
                except UnicodeDecodeError as ude:
                    logger.warning(f"编码 {try_encoding} 读取失败: {ude}")
                    continue
            
            if content is None:
                # 最后尝试二进制读取并尽力解码
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
                logger.warning(f"使用utf-8 errors='replace'模式读取文件")
            
            # 处理换行符
            content = content.replace('\\n', '\n')
            
            # 直接返回markdown内容，不包装在代码块中
            logger.info(f"成功解析Markdown文件: {file_path}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"解析Markdown文件失败 {file_path}: {e}")
            raise Exception(f"Markdown文件解析错误: {str(e)}") 