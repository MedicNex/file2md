from typing import Dict, Type
from .base import BaseParser
from .txt import PlainParser
from .docx import DocxParser
from .doc import DocParser
from .pdf import PdfParser
from .pptx import PptxParser
from .excel import ExcelParser
from .csv import CsvParser
from .image import ImageParser
from .code import CodeParser

class ParserRegistry:
    """解析器注册表"""
    
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """注册默认解析器"""
        parsers = [
            PlainParser,
            DocxParser,
            DocParser,
            PdfParser,
            PptxParser,
            ExcelParser,
            CsvParser,
            ImageParser,
            CodeParser
        ]
        
        for parser_class in parsers:
            for ext in parser_class.get_supported_extensions():
                self._parsers[ext.lower()] = parser_class
    
    def register(self, extension: str, parser_class: Type[BaseParser]):
        """注册新的解析器"""
        self._parsers[extension.lower()] = parser_class
    
    def get_parser(self, extension: str) -> Type[BaseParser]:
        """获取文件扩展名对应的解析器"""
        return self._parsers.get(extension.lower())
    
    def get_supported_extensions(self) -> list[str]:
        """获取所有支持的文件扩展名"""
        return list(self._parsers.keys())
    
    def is_supported(self, extension: str) -> bool:
        """检查是否支持指定的文件扩展名"""
        return extension.lower() in self._parsers

# 全局解析器注册表实例
parser_registry = ParserRegistry() 