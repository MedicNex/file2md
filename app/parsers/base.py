from abc import ABC, abstractmethod
from typing import Union, List, Optional
import os
import tempfile
import re
import aiofiles
import aiofiles.os
from loguru import logger

class BaseParser(ABC):
    """
    文档解析器基类
    
    提供异步文件操作和临时文件管理功能
    """
    
    def __init__(self):
        self.temp_files: List[str] = []
    
    @abstractmethod
    async def parse(self, file_path: str) -> str:
        """
        解析文档并返回Markdown文本
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            Markdown格式的文本内容
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 文件权限不足
            Exception: 解析过程中的其他错误
        """
        pass
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """返回支持的文件扩展名列表"""
        return []
    
    async def read_file_async(self, file_path: str, mode: str = 'r', encoding: str = 'utf-8') -> Union[str, bytes]:
        """
        异步读取文件内容
        
        Args:
            file_path: 文件路径
            mode: 读取模式 ('r' 或 'rb')
            encoding: 文本编码（仅在文本模式下使用）
            
        Returns:
            文件内容（字符串或字节）
        """
        try:
            if 'b' in mode:
                async with aiofiles.open(file_path, mode) as f:  # type: ignore
                    return await f.read()
            else:
                async with aiofiles.open(file_path, mode, encoding=encoding) as f:  # type: ignore
                    return await f.read()
        except Exception as e:
            logger.error(f"异步读取文件失败 {file_path}: {e}")
            raise
    
    async def write_file_async(self, file_path: str, content: Union[str, bytes], mode: str = 'w', encoding: str = 'utf-8') -> None:
        """
        异步写入文件内容
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            mode: 写入模式 ('w' 或 'wb')
            encoding: 文本编码（仅在文本模式下使用）
        """
        try:
            if 'b' in mode:
                async with aiofiles.open(file_path, mode) as f:  # type: ignore
                    await f.write(content)
            else:
                async with aiofiles.open(file_path, mode, encoding=encoding) as f:  # type: ignore
                    await f.write(content)
        except Exception as e:
            logger.error(f"异步写入文件失败 {file_path}: {e}")
            raise
    
    async def create_temp_file_async(self, suffix: str = "", content: Union[str, bytes, None] = None) -> str:
        """
        异步创建临时文件
        
        Args:
            suffix: 临时文件后缀
            content: 要写入的内容（可选）
            
        Returns:
            临时文件路径
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name
        temp_file.close()  # 关闭文件描述符，以便异步写入
        
        if content:
            if isinstance(content, str):
                await self.write_file_async(temp_file_path, content, mode='w')
            else:
                await self.write_file_async(temp_file_path, content, mode='wb')
        
        self.temp_files.append(temp_file_path)
        return temp_file_path
    
    def create_temp_file(self, suffix: str = "", content: Union[str, bytes, None] = None) -> str:
        """
        创建临时文件（同步版本，保持向后兼容）
        
        Args:
            suffix: 临时文件后缀
            content: 要写入的内容（可选）
            
        Returns:
            临时文件路径
        """
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
    
    async def cleanup_async(self) -> None:
        """异步清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if await aiofiles.os.path.exists(temp_file):
                    await aiofiles.os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"异步清理临时文件失败 {temp_file}: {e}")
        self.temp_files.clear()
    
    def cleanup(self) -> None:
        """清理临时文件（同步版本，保持向后兼容）"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"清理临时文件失败 {temp_file}: {e}")
        self.temp_files.clear()
    
    def __del__(self):
        """析构函数，确保清理临时文件"""
        self.cleanup() 