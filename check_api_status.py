#!/usr/bin/env python3
"""
检查 Render API 端点状态
"""

import requests
import json
from typing import Dict, Any

# Render 应用配置
RENDER_URL = "https://aiinventory-ctyd.onrender.com"
API_KEY = "5b35ccc45997eadabdf54f5e42d1eca6d5f6bc806765340c49b952281d2bc67c"

def make_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """发送 API 请求"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{RENDER_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.delete(url, headers=headers, timeout=30)
        
        return {
            "success": response.status_code in [200, 201],
            "status_code": response.status_code,
            "data": response.json() if response.content else {},
            "text": response.text
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_api_status():
    """检查所有 API 端点状态"""
    print("🔍 检查 Render API 端点状态...")
    
    # 基础端点
    basic_endpoints = [
        ("健康检查", "/health", "GET"),
        ("状态", "/api/status", "GET"),
        ("API 信息", "/docs", "GET")
    ]
    
    print("\n📋 基础端点检查:")
    for name, endpoint, method in basic_endpoints:
        result = make_request(endpoint, method)
        if result["success"]:
            print(f"  ✅ {name}: HTTP {result['status_code']}")
        else:
            print(f"  ❌ {name}: {result.get('error', f'HTTP {result.get("status_code", "Unknown")}')}")
    
    # 数据端点
    data_endpoints = [
        ("库位列表", "/api/bins", "GET"),
        ("物品列表", "/api/items", "GET"),
        ("分配列表", "/api/allocations", "GET"),
        ("订单列表", "/api/orders", "GET"),
        ("快照列表", "/api/snapshots", "GET")
    ]
    
    print("\n📊 数据端点检查:")
    for name, endpoint, method in data_endpoints:
        result = make_request(endpoint, method)
        if result["success"]:
            print(f"  ✅ {name}: HTTP {result['status_code']}")
        else:
            print(f"  ❌ {name}: {result.get('error', f'HTTP {result.get("status_code", "Unknown")}')}")
            if "text" in result and result["text"]:
                print(f"     错误详情: {result['text'][:100]}...")
    
    # 创建端点测试
    print("\n➕ 创建端点测试:")
    
    # 测试创建库位
    test_bin = {"bin_id": "TEST-BIN", "zone": "测试区", "coords": "0,0"}
    result = make_request("/api/bins", "POST", test_bin)
    if result["success"]:
        print(f"  ✅ 创建库位: HTTP {result['status_code']}")
        # 删除测试库位
        make_request(f"/api/bins/TEST-BIN", "DELETE")
    else:
        print(f"  ❌ 创建库位: {result.get('error', f'HTTP {result.get("status_code", "Unknown")}')}")
        if "text" in result and result["text"]:
            print(f"     错误详情: {result['text'][:100]}...")
    
    # 测试创建物品
    test_item = {"item_id": "TEST-ITEM", "name": "测试物品", "description": "测试用"}
    result = make_request("/api/items", "POST", test_item)
    if result["success"]:
        print(f"  ✅ 创建物品: HTTP {result['status_code']}")
        # 删除测试物品
        make_request(f"/api/items/TEST-ITEM", "DELETE")
    else:
        print(f"  ❌ 创建物品: {result.get('error', f'HTTP {result.get("status_code", "Unknown")}')}")
        if "text" in result and result["text"]:
            print(f"     错误详情: {result['text'][:100]}...")

if __name__ == "__main__":
    check_api_status()
