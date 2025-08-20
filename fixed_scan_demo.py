#!/usr/bin/env python3
"""
修复版本的扫描演示脚本
解决 API 认证问题
"""

import requests
import json
from typing import Dict, Any
import time

# Render 应用配置
RENDER_URL = "https://aiinventory-ctyd.onrender.com"
API_KEY = "5b35ccc45997eadabdf54f5e42d1eca6d5f6bc806765340c49b952281d2bc67c"

def make_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """发送 API 请求 - 修复版本"""
    # 尝试多种认证方式
    auth_headers = [
        {"Authorization": f"Bearer {API_KEY}"},
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        {"X-API-Key": API_KEY},
        {"api-key": API_KEY}
    ]
    
    url = f"{RENDER_URL}{endpoint}"
    
    for headers in auth_headers:
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.delete(url, headers=headers, timeout=30)
            
            # 检查响应状态
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if response.content else {},
                    "text": response.text,
                    "headers_used": headers
                }
            elif response.status_code == 401:
                print(f"  ⚠️  认证失败，尝试下一个认证方式...")
                continue
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": {},
                    "text": response.text,
                    "error": f"HTTP {response.status_code}"
                }
        
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
            continue
    
    return {"success": False, "error": "所有认证方式都失败了"}

def test_authentication():
    """测试不同的认证方式"""
    print("🔐 测试 API 认证方式...")
    
    # 测试不同的认证头
    auth_tests = [
        ("Bearer Token", {"Authorization": f"Bearer {API_KEY}"}),
        ("X-API-Key", {"X-API-Key": API_KEY}),
        ("api-key", {"api-key": API_KEY}),
        ("Authorization Header", {"Authorization": API_KEY})
    ]
    
    for name, headers in auth_tests:
        print(f"\n  🔍 测试 {name}:")
        try:
            response = requests.get(f"{RENDER_URL}/health", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"    ✅ 成功: HTTP {response.status_code}")
            else:
                print(f"    ❌ 失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"    ❌ 错误: {e}")

def demo_scan_workflow():
    """演示扫描工作流程 - 修复版本"""
    print("🎯 库存扫描系统演示 (修复版本)")
    print("=" * 50)
    
    # 1. 系统状态检查
    print("\n💚 步骤 1: 系统状态检查")
    health = make_request("/health")
    if health["success"]:
        print(f"  ✅ 系统状态: {health['data'].get('status', 'Unknown')}")
        print(f"  ✅ 服务名称: {health['data'].get('service', 'Unknown')}")
        print(f"  ✅ 版本: {health['data'].get('version', 'Unknown')}")
        if "headers_used" in health:
            print(f"  ✅ 使用的认证头: {health['headers_used']}")
    else:
        print(f"  ❌ 系统检查失败: {health.get('error', 'Unknown')}")
        return
    
    # 2. 查看当前订单
    print("\n📋 步骤 2: 查看待处理订单")
    orders = make_request("/api/orders")
    if orders["success"]:
        if isinstance(orders["data"], list):
            order_list = orders["data"]
        elif isinstance(orders["data"], dict) and "orders" in orders["data"]:
            order_list = orders["data"]["orders"]
        else:
            order_list = []
        
        if order_list:
            print(f"  📊 发现 {len(order_list)} 个待处理订单:")
            for i, order in enumerate(order_list, 1):
                print(f"    {i}. 订单号: {order.get('order_id', 'Unknown')}")
                print(f"       商品: {order.get('sku', 'Unknown')}")
                print(f"       数量: {order.get('qty', 0)}")
                print(f"       状态: {order.get('status', 'Unknown')}")
                print(f"       发货日期: {order.get('ship_date', 'Unknown')}")
                print()
        else:
            print("  ℹ️  当前没有待处理订单")
    else:
        print(f"  ❌ 获取订单失败: {orders.get('error', 'Unknown')}")
    
    # 3. 查看库存分配
    print("\n📦 步骤 3: 查看库存分配")
    allocations = make_request("/api/allocations")
    if allocations["success"]:
        if isinstance(allocations["data"], list):
            alloc_list = allocations["data"]
        elif isinstance(allocations["data"], dict) and "allocations" in allocations["data"]:
            alloc_list = allocations["data"]["allocations"]
        else:
            alloc_list = []
        
        if alloc_list:
            print(f"  📊 发现 {len(alloc_list)} 个库存分配:")
            for i, alloc in enumerate(alloc_list, 1):
                print(f"    {i}. 库位: {alloc.get('bin_id', 'Unknown')}")
                print(f"       物品: {alloc.get('item_id', 'Unknown')}")
                print(f"       数量: {alloc.get('qty', 0)}")
                print(f"       状态: {alloc.get('status', 'Unknown')}")
                print()
        else:
            print("  ℹ️  当前没有库存分配记录")
    else:
        print(f"  ❌ 获取分配失败: {allocations.get('error', 'Unknown')}")
    
    # 4. 模拟扫描操作
    print("\n📱 步骤 4: 模拟扫描操作")
    print("  🔍 模拟扫描库位 'A-01'...")
    time.sleep(1)
    print("  📸 拍照中...")
    time.sleep(1)
    print("  🤖 AI 识别中...")
    time.sleep(1)
    print("  ✅ 识别结果: 库位 A-01")
    
    # 5. 模拟物品扫描
    print("\n📦 步骤 5: 模拟物品扫描")
    print("  🔍 模拟扫描物品 'SKU-001'...")
    time.sleep(1)
    print("  📸 拍照中...")
    time.sleep(1)
    print("  🤖 AI 识别中...")
    time.sleep(1)
    print("  ✅ 识别结果: SKU-001 (测试物品1)")
    
    # 6. 库存查询演示
    print("\n🔍 步骤 6: 库存查询演示")
    print("  💬 用户查询: 'SKU-001 在哪里？'")
    
    # 模拟查询结果
    if orders["success"] and isinstance(orders["data"], list):
        order_list = orders["data"]
        sku_001_orders = [o for o in order_list if o.get('sku') == 'SKU-001']
        if sku_001_orders:
            order = sku_001_orders[0]
            print(f"  🤖 AI 回答: 找到 SKU-001 的订单")
            print(f"     订单号: {order.get('order_id')}")
            print(f"     数量: {order.get('qty')}")
            print(f"     状态: {order.get('status')}")
        else:
            print("  🤖 AI 回答: 未找到 SKU-001 的相关信息")
    
    # 7. 系统功能总结
    print("\n🎯 步骤 7: 系统功能总结")
    print("  ✅ 可用的功能:")
    print("     - 系统健康监控")
    print("     - 订单管理")
    print("     - 库存分配查询")
    print("     - 基础数据管理")
    
    print("\n  🔧 需要完善的功能:")
    print("     - 库位管理 (bins API)")
    print("     - 物品管理 (items API)")
    print("     - 快照上传 (snapshots API)")
    print("     - 自然语言查询 (NLQ API)")
    
    print("\n  📱 扫描功能状态:")
    print("     - 基础框架: ✅ 正常")
    print("     - 数据查询: ✅ 正常")
    print("     - 图片识别: ⚠️  需要修复")
    print("     - AI 问答: ⚠️  需要修复")
    
    print("\n🎉 演示完成！")
    print("\n💡 建议:")
    print("  1. 先修复 bins 和 items API")
    print("  2. 然后修复 snapshots API")
    print("  3. 最后完善 NLQ 功能")
    print("  4. 添加真实的图片扫描功能")

if __name__ == "__main__":
    # 先测试认证
    test_authentication()
    
    # 然后运行演示
    print("\n" + "="*50)
    demo_scan_workflow()
