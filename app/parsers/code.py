from .base import BaseParser
from loguru import logger
import chardet

class CodeParser(BaseParser):
    """代码文件解析器"""
    
    # 文件扩展名到语言类型的映射
    EXTENSION_TO_LANGUAGE = {
        '.py': 'python',
        '.js': 'javascript', 
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.json': 'json',
        '.r': 'r',
        '.R': 'r',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.cmd': 'batch',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.sql': 'sql',
        '.dockerfile': 'dockerfile',
        '.dockerignore': 'text',
        '.gitignore': 'text',
        '.gitattributes': 'text',
        '.editorconfig': 'text',
        '.env': 'bash',
        '.makefile': 'makefile',
        '.make': 'makefile',
        '.cmake': 'cmake',
        '.gradle': 'gradle',
        '.groovy': 'groovy',
        '.lua': 'lua',
        '.perl': 'perl',
        '.pl': 'perl',
        '.vim': 'vim',
        '.vimrc': 'vim',
        '.tex': 'latex',
        '.m': 'matlab',
        '.mat': 'matlab',
        '.jl': 'julia',
        '.clj': 'clojure',
        '.cljs': 'clojure',
        '.elm': 'elm',
        '.erl': 'erlang',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.fs': 'fsharp',
        '.fsx': 'fsharp',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.dart': 'dart',
        '.proto': 'protobuf',
        '.graphql': 'graphql',
        '.gql': 'graphql',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.astro': 'astro',
        '.postcss': 'postcss',
        '.styl': 'stylus',
    }
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return list(cls.EXTENSION_TO_LANGUAGE.keys())
    
    async def parse(self, file_path: str) -> str:
        """解析代码文件"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 获取文件扩展名
            import os
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # 获取对应的编程语言
            language = self.EXTENSION_TO_LANGUAGE.get(file_extension, 'text')
            
            # 处理换行符
            content = content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            formatted_content = f"```{language}\n{content.strip()}\n```"
            
            logger.info(f"成功解析代码文件: {file_path}, 语言: {language}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"解析代码文件失败 {file_path}: {e}")
            raise Exception(f"代码文件解析错误: {str(e)}") 