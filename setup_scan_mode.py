#!/usr/bin/env python3
"""
设置扫描模式所需的最小数据
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
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json() if response.content else {}}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def setup_scan_mode():
    """设置扫描模式所需的最小数据"""
    print("🔧 设置扫描模式...")
    
    # 1. 创建基本库位
    print("\n🏠 创建基本库位...")
    basic_bins = [
        {"bin_id": "A-01", "zone": "A区", "coords": "10,20"},
        {"bin_id": "A-02", "zone": "A区", "coords": "15,25"},
        {"bin_id": "B-01", "zone": "B区", "coords": "30,40"},
        {"bin_id": "B-02", "zone": "B区", "coords": "35,45"}
    ]
    
    for bin_data in basic_bins:
        result = make_request("/api/bins", "POST", bin_data)
        if result["success"]:
            print(f"  ✅ 创建库位 {bin_data['bin_id']}")
        else:
            print(f"  ❌ 创建库位失败: {result['error']}")
    
    # 2. 创建基本物品
    print("\n📦 创建基本物品...")
    basic_items = [
        {"item_id": "SKU-001", "name": "测试物品1", "description": "用于扫描测试的物品1"},
        {"item_id": "SKU-002", "name": "测试物品2", "description": "用于扫描测试的物品2"},
        {"item_id": "SKU-003", "name": "测试物品3", "description": "用于扫描测试的物品3"}
    ]
    
    for item_data in basic_items:
        result = make_request("/api/items", "POST", item_data)
        if result["success"]:
            print(f"  ✅ 创建物品 {item_data['item_id']}")
        else:
            print(f"  ❌ 创建物品失败: {result['error']}")
    
    # 3. 创建基本分配
    print("\n📋 创建基本分配...")
    basic_allocations = [
        {"bin_id": "A-01", "item_id": "SKU-001", "qty": 5},
        {"bin_id": "A-02", "item_id": "SKU-002", "qty": 3},
        {"bin_id": "B-01", "item_id": "SKU-003", "qty": 2}
    ]
    
    for alloc_data in basic_allocations:
        result = make_request("/api/allocations", "POST", alloc_data)
        if result["success"]:
            print(f"  ✅ 创建分配 {alloc_data['bin_id']} -> {alloc_data['item_id']}")
        else:
            print(f"  ❌ 创建分配失败: {result['error']}")
    
    # 4. 创建测试订单
    print("\n📋 创建测试订单...")
    test_orders = [
        {"order_id": "TEST-001", "ship_date": "2025-08-20", "sku": "SKU-001", "qty": 2, "status": "pending"},
        {"order_id": "TEST-002", "ship_date": "2025-08-20", "sku": "SKU-002", "qty": 1, "status": "pending"}
    ]
    
    for order_data in test_orders:
        result = make_request("/api/orders", "POST", order_data)
        if result["success"]:
            print(f"  ✅ 创建订单 {order_data['order_id']}")
        else:
            print(f"  ❌ 创建订单失败: {result['error']}")
    
    print("\n🎉 扫描模式设置完成！")
    
    # 5. 验证设置结果
    print("\n🔍 验证设置结果...")
    verify_setup()

def verify_setup():
    """验证设置结果"""
    endpoints = [
        ("库位", "/api/bins"),
        ("物品", "/api/items"),
        ("分配", "/api/allocations"),
        ("订单", "/api/orders")
    ]
    
    for name, endpoint in endpoints:
        result = make_request(endpoint)
        if result["success"]:
            if "bins" in result["data"]:
                count = len(result["data"]["bins"])
            elif "items" in result["data"]:
                count = len(result["data"]["items"])
            elif "allocations" in result["data"]:
                count = len(result["data"]["allocations"])
            elif "orders" in result["data"]:
                count = len(result["data"]["orders"])
            else:
                count = 0
            
            print(f"  {name}: {count} 条记录")
        else:
            print(f"  {name}: 检查失败 - {result['error']}")

if __name__ == "__main__":
    setup_scan_mode()
