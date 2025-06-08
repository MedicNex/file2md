from abc import ABC, abstractmethod
from typing import Union
import os
import tempfile
import re

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
    
    def convert_code_blocks_to_html(self, content: str) -> str:
        """
        将Markdown代码块转换为HTML code标签
        
        Args:
            content: 包含Markdown代码块的文本
            
        Returns:
            转换后的文本，代码块被替换为HTML标签
        """
        # 匹配 ```language 开头和 ``` 结尾的代码块
        def replace_code_block(match):
            language = match.group(1).strip() if match.group(1) else ""
            code_content = match.group(2)
            
            # 如果有语言标识，添加到class中
            if language:
                return f'<code class="language-{language}">\n{code_content}\n</code>'
            else:
                return f'<code>\n{code_content}\n</code>'
        
        # 更精确的正则表达式匹配代码块
        # 匹配 ```可选语言标识符
        # 然后匹配代码内容（非贪婪匹配）
        # 最后匹配结束的```
        pattern = r'```(\w+)?\s*\n(.*?)\n```'
        result = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)
        
        return result
    
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