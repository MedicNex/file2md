#!/usr/bin/env python3
"""
格式验证脚本 - 验证支持的文件格式数量和分类
用于确保代码更新后格式支持的正确性
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.registry import ParserRegistry
from collections import defaultdict

def verify_formats():
    """验证支持的文件格式"""
    print("🔍 验证支持的文件格式...")
    
    registry = ParserRegistry()
    extensions = registry.get_supported_extensions()
    
    # 按解析器分组
    parser_groups = defaultdict(list)
    for ext in sorted(extensions):
        parser_class = registry.get_parser(ext)
        if parser_class:
            parser_groups[parser_class.__name__].append(ext)
    
    print(f"✅ 总计支持：{len(extensions)} 种文件格式")
    print(f"📋 解析器数量：{len(parser_groups)} 个")
    
    # 验证预期数量
    expected_total = 106
    expected_parsers = 13
    
    if len(extensions) == expected_total:
        print(f"✅ 格式数量验证通过：{len(extensions)}/{expected_total}")
    else:
        print(f"❌ 格式数量不匹配：期望 {expected_total}，实际 {len(extensions)}")
        return False
    
    if len(parser_groups) == expected_parsers:
        print(f"✅ 解析器数量验证通过：{len(parser_groups)}/{expected_parsers}")
    else:
        print(f"❌ 解析器数量不匹配：期望 {expected_parsers}，实际 {len(parser_groups)}")
        return False
    
    # 显示主要类别统计
    code_parser_count = len(parser_groups.get('CodeParser', []))
    image_parser_count = len(parser_groups.get('ImageParser', []))
    svg_parser_count = len(parser_groups.get('SvgParser', []))
    
    print(f"\n📊 主要类别：")
    print(f"- CodeParser: {code_parser_count} 种")
    print(f"- ImageParser: {image_parser_count} 种") 
    print(f"- SvgParser: {svg_parser_count} 种")
    
    return True

if __name__ == "__main__":
    success = verify_formats()
    sys.exit(0 if success else 1) 