from .base import BaseParser
from loguru import logger
import chardet
import aiofiles
import os
from app.config import config

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
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取文件大小和扩展名
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            language = self.EXTENSION_TO_LANGUAGE.get(file_extension, 'text')
            
            logger.info(f"开始解析代码文件: {file_path}, 大小: {file_size} bytes, 语言: {language}")
            
            # 检测文件编码（只读取前几KB用于编码检测）
            sample_size = min(file_size, 10240)  # 最多读取10KB用于编码检测
            with open(file_path, 'rb') as f:
                raw_sample = f.read(sample_size)
                detected_encoding = chardet.detect(raw_sample)
                encoding = detected_encoding.get('encoding') or 'utf-8'
                confidence = detected_encoding.get('confidence', 0)
                
                logger.info(f"检测到文件编码: {encoding} (置信度: {confidence:.2f})")
            
            # 使用异步方式读取文件内容，并且有编码降级策略
            try:
                content = await self.read_file_async(file_path, mode='r', encoding=encoding)
            except UnicodeDecodeError as e:
                logger.warning(f"使用检测编码 {encoding} 读取失败，尝试使用 utf-8: {e}")
                # 如果检测的编码失败，尝试使用utf-8
                try:
                    content = await self.read_file_async(file_path, mode='r', encoding='utf-8')
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    # 如果utf-8也失败，使用latin-1（不会失败）
                    logger.warning("utf-8 编码也失败，使用 latin-1 编码读取")
                    content = await self.read_file_async(file_path, mode='r', encoding='latin-1')
                    encoding = 'latin-1'
            
            # 确保content是字符串类型
            if isinstance(content, bytes):
                content = content.decode(encoding, errors='replace')
            
            # 统计文件信息
            line_count = content.count('\n') + 1 if content else 0
            char_count = len(content)
            
            logger.info(f"文件读取成功: {line_count} 行, {char_count} 字符, 编码: {encoding}")
            
            # 检查代码文件大小限制
            if char_count > config.MAX_TEXT_CHARS:
                raise Exception(f"代码文件过大: {char_count} 字符，最大允许: {config.MAX_TEXT_CHARS} 字符")
            
            if line_count > config.MAX_TEXT_LINES:
                raise Exception(f"代码文件行数过多: {line_count} 行，最大允许: {config.MAX_TEXT_LINES} 行")
            
            # 处理换行符
            content = content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            formatted_content = f"```{language}\n{content.strip()}\n```"
            
            logger.info(f"成功解析代码文件: {file_path}, 语言: {language}")
            return formatted_content
            
        except FileNotFoundError as e:
            logger.error(f"文件不存在: {file_path}")
            raise Exception(f"文件不存在: {str(e)}")
        except PermissionError as e:
            logger.error(f"文件权限不足: {file_path}")
            raise Exception(f"文件权限不足: {str(e)}")
        except MemoryError as e:
            logger.error(f"文件过大，内存不足: {file_path}")
            raise Exception(f"文件过大，内存不足: {str(e)}")
        except Exception as e:
            logger.error(f"解析代码文件失败 {file_path}: {e}")
            raise Exception(f"代码文件解析错误: {str(e)}") 