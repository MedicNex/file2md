#!/usr/bin/env python3
"""
MedicNex File2Markdown 服务测试脚本
"""

import requests
import json
import os
import tempfile
from pathlib import Path

# 服务配置
BASE_URL = "http://localhost:8080"
API_KEY = "dev-test-key-123"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/v1/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    print("✅ 健康检查通过\n")

def test_supported_types():
    """测试获取支持的文件类型"""
    print("🔍 测试获取支持的文件类型...")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/v1/supported-types", headers=headers)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"支持的扩展名: {data['supported_extensions']}")
    print(f"总数: {data['total_count']}")
    assert response.status_code == 200
    print("✅ 获取支持类型成功\n")

def test_convert_text_file():
    """测试转换文本文件"""
    print("🔍 测试转换文本文件...")
    
    # 创建测试文本文件
    test_content = """# 测试文档

这是一个测试文档，包含以下内容：

## 章节1
- 列表项1
- 列表项2

## 章节2
这是一些普通文本内容。

### 子章节
更多内容...
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        with open(temp_file_path, 'rb') as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/v1/convert", headers=headers, files=files)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"文件名: {data['filename']}")
            print(f"大小: {data['size']} bytes")
            print(f"处理时间: {data['duration_ms']} ms")
            print(f"转换结果:\n{data['markdown'][:200]}...")
            print("✅ 文本文件转换成功\n")
        else:
            print(f"❌ 转换失败: {response.text}")
    
    finally:
        os.unlink(temp_file_path)

def test_convert_csv_file():
    """测试转换CSV文件"""
    print("🔍 测试转换CSV文件...")
    
    # 创建测试CSV文件
    csv_content = """姓名,年龄,城市,薪资
张三,25,北京,8000
李四,30,上海,12000
王五,28,广州,9500
赵六,35,深圳,15000
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        temp_file_path = f.name
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        with open(temp_file_path, 'rb') as f:
            files = {"file": ("test.csv", f, "text/csv")}
            response = requests.post(f"{BASE_URL}/v1/convert", headers=headers, files=files)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"文件名: {data['filename']}")
            print(f"大小: {data['size']} bytes")
            print(f"处理时间: {data['duration_ms']} ms")
            print(f"转换结果:\n{data['markdown'][:500]}...")
            print("✅ CSV文件转换成功\n")
        else:
            print(f"❌ 转换失败: {response.text}")
    
    finally:
        os.unlink(temp_file_path)

def test_invalid_api_key():
    """测试无效API Key"""
    print("🔍 测试无效API Key...")
    
    headers = {"Authorization": "Bearer invalid-key"}
    response = requests.get(f"{BASE_URL}/v1/supported-types", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 401
    print("✅ API Key验证正常\n")

def test_unsupported_file_type():
    """测试不支持的文件类型"""
    print("🔍 测试不支持的文件类型...")
    
    # 创建一个不支持的文件类型
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        f.write(b"test content")
        temp_file_path = f.name
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        with open(temp_file_path, 'rb') as f:
            files = {"file": ("test.xyz", f, "application/octet-stream")}
            response = requests.post(f"{BASE_URL}/v1/convert", headers=headers, files=files)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        assert response.status_code == 415
        print("✅ 文件类型验证正常\n")
    
    finally:
        os.unlink(temp_file_path)

def main():
    """运行所有测试"""
    print("🚀 开始测试 MedicNex File2Markdown 服务\n")
    
    try:
        test_health_check()
        test_supported_types()
        test_convert_text_file()
        test_convert_csv_file()
        test_invalid_api_key()
        test_unsupported_file_type()
        
        print("🎉 所有测试通过！服务运行正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 