#!/usr/bin/env python3
"""
简单的扫描测试模式
使用可用的 API 端点进行测试
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

def test_available_features():
    """测试可用的功能"""
    print("🎯 测试可用的扫描功能...")
    
    # 1. 检查健康状态
    print("\n💚 健康检查:")
    health = make_request("/health")
    if health["success"]:
        print(f"  ✅ 应用状态: {health['data'].get('status', 'Unknown')}")
        print(f"  ✅ 服务名称: {health['data'].get('service', 'Unknown')}")
        print(f"  ✅ 版本: {health['data'].get('version', 'Unknown')}")
    else:
        print(f"  ❌ 健康检查失败: {health.get('error', 'Unknown')}")
    
    # 2. 检查分配数据
    print("\n📦 分配数据检查:")
    allocations = make_request("/api/allocations")
    if allocations["success"]:
        # 处理不同的数据结构
        if isinstance(allocations["data"], list):
            alloc_count = len(allocations["data"])
            print(f"  ✅ 当前分配数量: {alloc_count}")
            if alloc_count > 0:
                print("  📋 分配详情:")
                for alloc in allocations["data"][:3]:  # 显示前3个
                    if isinstance(alloc, dict):
                        print(f"    - {alloc.get('bin_id', 'Unknown')} -> {alloc.get('item_id', 'Unknown')}")
        elif isinstance(allocations["data"], dict) and "allocations" in allocations["data"]:
            alloc_count = len(allocations["data"]["allocations"])
            print(f"  ✅ 当前分配数量: {alloc_count}")
            if alloc_count > 0:
                print("  📋 分配详情:")
                for alloc in allocations["data"]["allocations"][:3]:  # 显示前3个
                    print(f"    - {alloc.get('bin_id', 'Unknown')} -> {alloc.get('item_id', 'Unknown')}")
        else:
            print(f"  ℹ️  分配数据结构: {type(allocations['data'])}")
            print(f"  📋 数据内容: {allocations['data']}")
    else:
        print(f"  ❌ 分配检查失败: {allocations.get('error', 'Unknown')}")
    
    # 3. 检查订单数据
    print("\n📋 订单数据检查:")
    orders = make_request("/api/orders")
    if orders["success"]:
        # 处理不同的数据结构
        if isinstance(orders["data"], list):
            order_count = len(orders["data"])
            print(f"  ✅ 当前订单数量: {order_count}")
            if order_count > 0:
                print("  📋 订单详情:")
                for order in orders["data"][:3]:  # 显示前3个
                    if isinstance(order, dict):
                        print(f"    - {order.get('order_id', 'Unknown')}: {order.get('sku', 'Unknown')} x{order.get('qty', 0)}")
        elif isinstance(orders["data"], dict) and "orders" in orders["data"]:
            order_count = len(orders["data"]["orders"])
            print(f"  ✅ 当前订单数量: {order_count}")
            if order_count > 0:
                print("  📋 订单详情:")
                for order in orders["data"]["orders"][:3]:  # 显示前3个
                    print(f"    - {order.get('order_id', 'Unknown')}: {order.get('sku', 'Unknown')} x{order.get('qty', 0)}")
        else:
            print(f"  ℹ️  订单数据结构: {type(orders['data'])}")
            print(f"  📋 数据内容: {orders['data']}")
    else:
        print(f"  ❌ 订单检查失败: {orders.get('error', 'Unknown')}")
    
    # 4. 测试自然语言查询
    print("\n🤖 自然语言查询测试:")
    nlq_test = make_request("/api/nlq/query?q=show me all allocations")
    if nlq_test["success"]:
        print(f"  ✅ NLQ 查询成功: {nlq_test['data'].get('answer', 'No answer')}")
    else:
        print(f"  ❌ NLQ 查询失败: {nlq_test.get('error', 'Unknown')}")
    
    # 5. 测试快照上传（模拟）
    print("\n📸 快照功能测试:")
    print("  ℹ️  快照上传需要图片文件，这里只测试 API 可用性")
    # 尝试获取快照列表
    snapshots = make_request("/api/snapshots")
    if snapshots["success"]:
        if isinstance(snapshots["data"], list):
            snapshot_count = len(snapshots["data"])
        elif isinstance(snapshots["data"], dict) and "snapshots" in snapshots["data"]:
            snapshot_count = len(snapshots["data"]["snapshots"])
        else:
            snapshot_count = 0
        print(f"  ✅ 快照 API 可用，当前数量: {snapshot_count}")
    else:
        print(f"  ❌ 快照 API 不可用: {snapshots.get('error', 'Unknown')}")
    
    # 6. 扫描功能总结
    print("\n🎯 扫描功能总结:")
    if allocations["success"] and orders["success"]:
        print("  ✅ 基础数据查询功能正常")
        print("  ✅ 可以进行库存查询和订单管理")
        if nlq_test["success"]:
            print("  ✅ 自然语言查询功能正常")
        else:
            print("  ⚠️  自然语言查询功能需要检查")
        
        print("\n  📱 可以使用的功能:")
        print("    - 查看库存分配")
        print("    - 查看订单状态")
        print("    - 使用自然语言查询库存")
        print("    - 基础的数据管理")
        
        print("\n  🔧 需要修复的功能:")
        print("    - 库位管理 (bins API)")
        print("    - 物品管理 (items API)")
        print("    - 快照上传 (snapshots API)")
    else:
        print("  ❌ 基础功能不可用，需要进一步诊断")

if __name__ == "__main__":
    test_available_features()
