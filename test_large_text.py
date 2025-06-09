#!/usr/bin/env python3
"""
大文本文件测试脚本

用于测试后端对大文本文件的处理能力
"""

import asyncio
import tempfile
import os
import requests
from pathlib import Path

def create_large_text_file(lines: int, filename: str = None) -> str:
    """创建包含指定行数的大文本文件"""
    if filename is None:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        filename = temp_file.name
        temp_file.close()
    
    print(f"正在创建包含 {lines} 行的测试文件: {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(lines):
            f.write(f"这是第 {i+1} 行文本内容。Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n")
    
    file_size = os.path.getsize(filename)
    print(f"文件创建完成，大小: {file_size} bytes ({file_size / 1024:.1f} KB)")
    return filename

def test_api_upload(file_path: str, api_url: str = "http://localhost:8080/v1/convert"):
    """测试API上传"""
    api_key = "dev-test-key-123"
    
    print(f"正在测试API上传: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/plain')}
        headers = {'Authorization': f'Bearer {api_key}'}
        
        try:
            response = requests.post(api_url, files=files, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 转换成功!")
                print(f"   文件名: {result.get('filename')}")
                print(f"   大小: {result.get('size')} bytes")
                print(f"   处理时间: {result.get('duration_ms')} ms")
                
                content = result.get('content', '')
                content_lines = content.count('\n')
                print(f"   输出行数: {content_lines}")
                print(f"   输出字符数: {len(content)}")
                
                # 只显示前几行和后几行
                lines = content.split('\n')
                if len(lines) > 10:
                    print("   输出内容预览:")
                    for i, line in enumerate(lines[:5]):
                        print(f"     {i+1}: {line}")
                    print("     ...")
                    for i, line in enumerate(lines[-3:], len(lines)-3):
                        print(f"     {i+1}: {line}")
                else:
                    print(f"   输出内容:\n{content}")
                
            else:
                print(f"❌ 转换失败: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   错误信息: {error_detail}")
                except:
                    print(f"   错误信息: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败，请确保服务正在运行")
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def main():
    """主测试函数"""
    print("=== 大文本文件处理测试 ===\n")
    
    # 测试不同大小的文件
    test_cases = [
        ("小文件", 100),
        ("中等文件", 1000),  
        ("大文件", 5000),
        ("超大文件", 10000),
        ("极大文件", 20000),
    ]
    
    for test_name, line_count in test_cases:
        print(f"\n--- {test_name} ({line_count} 行) ---")
        
        # 创建测试文件
        test_file = create_large_text_file(line_count)
        
        try:
            # 测试API
            test_api_upload(test_file)
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.unlink(test_file)
                print(f"已清理测试文件: {test_file}")
        
        print("-" * 50)

if __name__ == "__main__":
    main() 