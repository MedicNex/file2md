from abc import ABC, abstractmethod
from typing import Union
import os
import tempfile

class BaseParser(ABC):
    """文档解析器基类"""
    
    def __init__(self):
        self.temp_files = []
    
    @abstractmethod
    async def parse(self, file_path: str) -> str:
        """
        解析文档并返回Markdown文本
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            Markdown格式的文本内容
        """
        pass
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """返回支持的文件扩展名列表"""
        return []
    
    def create_temp_file(self, suffix: str = "", content: Union[str, bytes] = None) -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        if content:
            if isinstance(content, str):
                temp_file.write(content.encode('utf-8'))
            else:
                temp_file.write(content)
        
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def cleanup(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        self.temp_files.clear()
    
    def __del__(self):
        """析构函数，确保清理临时文件"""
        self.cleanup() 