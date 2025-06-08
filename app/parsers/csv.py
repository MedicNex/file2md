from .base import BaseParser
from loguru import logger
import pandas as pd
from tabulate import tabulate
import chardet

class CsvParser(BaseParser):
    """CSV文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.csv']
    
    async def parse(self, file_path: str) -> str:
        """解析CSV文件"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 处理NaN值
            df = df.fillna('')
            
            content_parts = []
            
            # 添加基本信息
            content_parts.append(f"# CSV数据文件")
            content_parts.append(f"**数据行数**: {len(df)}")
            content_parts.append(f"**数据列数**: {len(df.columns)}")
            
            # 转换为Markdown表格
            content_parts.append("## 数据内容")
            
            # 如果数据太多，只显示前100行
            display_df = df.head(100) if len(df) > 100 else df
            markdown_table = tabulate(display_df, headers='keys', tablefmt='github', showindex=False)
            content_parts.append(markdown_table)
            
            if len(df) > 100:
                content_parts.append(f"*注意: 为了便于阅读，此处仅显示前100行数据，实际文件包含{len(df)}行数据*")
            
            # 添加数据统计
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                content_parts.append("## 数值列统计")
                stats_data = []
                for col in numeric_cols:
                    stats_data.append([
                        col,
                        f"{df[col].count()}",
                        f"{df[col].mean():.2f}" if df[col].count() > 0 else "N/A",
                        f"{df[col].std():.2f}" if df[col].count() > 0 else "N/A",
                        f"{df[col].min():.2f}" if df[col].count() > 0 else "N/A",
                        f"{df[col].max():.2f}" if df[col].count() > 0 else "N/A"
                    ])
                
                stats_df = pd.DataFrame(stats_data, columns=['列名', '计数', '平均值', '标准差', '最小值', '最大值'])
                stats_table = tabulate(stats_df, headers='keys', tablefmt='github', showindex=False)
                content_parts.append(stats_table)
            
            # 添加文本列信息
            text_cols = df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                content_parts.append("## 文本列信息")
                text_info = []
                for col in text_cols:
                    unique_count = df[col].nunique()
                    most_common = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                    text_info.append([col, f"{unique_count}", str(most_common)[:50]])
                
                text_df = pd.DataFrame(text_info, columns=['列名', '唯一值数量', '最常见值'])
                text_table = tabulate(text_df, headers='keys', tablefmt='github', showindex=False)
                content_parts.append(text_table)
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            markdown_content = f"```sheet\n{raw_content}\n```"
            
            logger.info(f"成功解析CSV文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析CSV文件失败 {file_path}: {e}")
            raise Exception(f"CSV文件解析错误: {str(e)}") 