#!/usr/bin/env python3
"""
清理 Render 上的测试数据脚本
"""

import requests
import json
from typing import List, Dict, Any

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
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json() if response.content else {}}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def cleanup_data():
    """清理所有测试数据"""
    print("🧹 开始清理 Render 上的测试数据...")
    
    # 1. 清理快照数据
    print("\n📸 清理快照数据...")
    snapshots = make_request("/api/snapshots")
    if snapshots["success"] and "snapshots" in snapshots["data"]:
        for snapshot in snapshots["data"]["snapshots"]:
            result = make_request(f"/api/snapshots/{snapshot['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除快照 {snapshot['id']}")
            else:
                print(f"  ❌ 删除快照失败: {result['error']}")
    
    # 2. 清理异常数据
    print("\n⚠️ 清理异常数据...")
    anomalies = make_request("/api/reconcile/anomalies")
    if anomalies["success"] and "anomalies" in anomalies["data"]:
        for anomaly in anomalies["data"]["anomalies"]:
            result = make_request(f"/api/reconcile/anomalies/{anomaly['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除异常 {anomaly['id']}")
            else:
                print(f"  ❌ 删除异常失败: {result['error']}")
    
    # 3. 清理分配数据
    print("\n📦 清理分配数据...")
    allocations = make_request("/api/allocations")
    if allocations["success"] and "allocations" in allocations["data"]:
        for allocation in allocations["data"]["allocations"]:
            result = make_request(f"/api/allocations/{allocation['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除分配 {allocation['id']}")
            else:
                print(f"  ❌ 删除分配失败: {result['error']}")
    
    # 4. 清理订单数据
    print("\n📋 清理订单数据...")
    orders = make_request("/api/orders")
    if orders["success"] and "orders" in orders["data"]:
        for order in orders["data"]["orders"]:
            result = make_request(f"/api/orders/{order['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除订单 {order['id']}")
            else:
                print(f"  ❌ 删除订单失败: {result['error']}")
    
    # 5. 清理库位数据
    print("\n🏠 清理库位数据...")
    bins = make_request("/api/bins")
    if bins["success"] and "bins" in bins["data"]:
        for bin_item in bins["data"]["bins"]:
            result = make_request(f"/api/bins/{bin_item['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除库位 {bin_item['id']}")
            else:
                print(f"  ❌ 删除库位失败: {result['error']}")
    
    # 6. 清理物品数据
    print("\n📦 清理物品数据...")
    items = make_request("/api/items")
    if items["success"] and "items" in items["data"]:
        for item in items["data"]["items"]:
            result = make_request(f"/api/items/{item['id']}", "DELETE")
            if result["success"]:
                print(f"  ✅ 删除物品 {item['id']}")
            else:
                print(f"  ❌ 删除物品失败: {result['error']}")
    
    print("\n🎉 数据清理完成！")
    
    # 7. 验证清理结果
    print("\n🔍 验证清理结果...")
    verify_cleanup()

def verify_cleanup():
    """验证清理结果"""
    endpoints = [
        ("快照", "/api/snapshots"),
        ("异常", "/api/reconcile/anomalies"),
        ("分配", "/api/allocations"),
        ("订单", "/api/orders"),
        ("库位", "/api/bins"),
        ("物品", "/api/items")
    ]
    
    for name, endpoint in endpoints:
        result = make_request(endpoint)
        if result["success"]:
            if "snapshots" in result["data"]:
                count = len(result["data"]["snapshots"])
            elif "anomalies" in result["data"]:
                count = len(result["data"]["anomalies"])
            elif "allocations" in result["data"]:
                count = len(result["data"]["allocations"])
            elif "orders" in result["data"]:
                count = len(result["data"]["orders"])
            elif "bins" in result["data"]:
                count = len(result["data"]["bins"])
            elif "items" in result["data"]:
                count = len(result["data"]["items"])
            else:
                count = 0
            
            print(f"  {name}: {count} 条记录")
        else:
            print(f"  {name}: 检查失败 - {result['error']}")

if __name__ == "__main__":
    cleanup_data()
