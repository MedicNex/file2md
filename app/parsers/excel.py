from .base import BaseParser
from loguru import logger
import pandas as pd
from tabulate import tabulate

class ExcelParser(BaseParser):
    """Excel文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.xls', '.xlsx']
    
    async def parse(self, file_path: str) -> str:
        """解析Excel文件"""
        try:
            content_parts = []
            
            # 读取所有工作表
            xlsx_file = pd.ExcelFile(file_path)
            
            for sheet_name in xlsx_file.sheet_names:
                try:
                    # 读取工作表数据
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # 跳过空工作表
                    if df.empty:
                        continue
                    
                    # 处理NaN值
                    df = df.fillna('')
                    
                    # 添加工作表标题
                    content_parts.append(f"## 工作表: {sheet_name}")
                    
                    # 转换为Markdown表格
                    markdown_table = tabulate(df, headers='keys', tablefmt='github', showindex=False)
                    content_parts.append(markdown_table)
                    
                    # 添加基本统计信息
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        content_parts.append("### 数据统计")
                        stats_data = []
                        for col in numeric_cols:
                            stats_data.append([
                                col,
                                f"{df[col].count()}",
                                f"{df[col].mean():.2f}" if df[col].count() > 0 else "N/A",
                                f"{df[col].min():.2f}" if df[col].count() > 0 else "N/A",
                                f"{df[col].max():.2f}" if df[col].count() > 0 else "N/A"
                            ])
                        
                        stats_df = pd.DataFrame(stats_data, columns=['列名', '计数', '平均值', '最小值', '最大值'])
                        stats_table = tabulate(stats_df, headers='keys', tablefmt='github', showindex=False)
                        content_parts.append(stats_table)
                    
                except Exception as sheet_error:
                    logger.warning(f"工作表 {sheet_name} 解析失败: {sheet_error}")
                    content_parts.append(f"## 工作表: {sheet_name}\n\n*工作表解析失败: {str(sheet_error)}*")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            markdown_content = f"```sheet\n{raw_content or 'Excel文件为空或无法提取内容'}\n```"
            
            logger.info(f"成功解析Excel文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析Excel文件失败 {file_path}: {e}")
            raise Exception(f"Excel文件解析错误: {str(e)}") 