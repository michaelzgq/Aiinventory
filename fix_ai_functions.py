#!/usr/bin/env python3
"""
修复图片识别和AI问答功能
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

def test_ai_functions():
    """测试AI功能"""
    print("🤖 测试AI功能...")
    
    # 1. 测试自然语言查询
    print("\n💬 测试自然语言查询:")
    test_queries = [
        "A54现在有什么？",
        "找 SKU-001",
        "今天有多少异常",
        "库存总览"
    ]
    
    for query in test_queries:
        print(f"\n  🔍 查询: '{query}'")
        result = make_request("/api/nlq/query", "POST", {"text": query})
        if result["success"]:
            print(f"    ✅ 成功: {result['data'].get('answer', 'No answer')}")
        else:
            print(f"    ❌ 失败: {result.get('error', 'Unknown error')}")
    
    # 2. 测试查询示例
    print("\n📋 测试查询示例:")
    examples = make_request("/api/nlq/examples")
    if examples["success"]:
        print("  ✅ 查询示例API正常")
        if "examples" in examples["data"]:
            for category, queries in examples["data"]["examples"].items():
                print(f"    {category}: {len(queries)} 个示例")
    else:
        print(f"  ❌ 查询示例API失败: {examples.get('error', 'Unknown error')}")
    
    # 3. 测试支持的意图
    print("\n🎯 测试支持的意图:")
    intents = make_request("/api/nlq/intents")
    if intents["success"]:
        print("  ✅ 意图API正常")
        if "intents" in intents["data"]:
            for intent, details in intents["data"]["intents"].items():
                print(f"    {intent}: {details.get('description', 'No description')}")
    else:
        print(f"  ❌ 意图API失败: {intents.get('error', 'Unknown error')}")
    
    # 4. 测试图片识别相关API
    print("\n📸 测试图片识别相关API:")
    
    # 测试快照API
    snapshots = make_request("/api/snapshots")
    if snapshots["success"]:
        print("  ✅ 快照API正常")
    else:
        print(f"  ❌ 快照API失败: {snapshots.get('error', 'Unknown error')}")
    
    # 测试库位API
    bins = make_request("/api/bins")
    if bins["success"]:
        print("  ✅ 库位API正常")
    else:
        print(f"  ❌ 库位API失败: {bins.get('error', 'Unknown error')}")
    
    # 测试物品API
    items = make_request("/api/items")
    if items["success"]:
        print("  ✅ 物品API正常")
    else:
        print(f"  ❌ 物品API失败: {items.get('error', 'Unknown error')}")

def create_test_data_for_ai():
    """为AI功能创建测试数据"""
    print("\n🔧 为AI功能创建测试数据...")
    
    # 1. 创建测试库位
    print("\n🏠 创建测试库位:")
    test_bins = [
        {"bin_id": "A54", "zone": "Zone-A", "coords": "100,200"},
        {"bin_id": "S-01", "zone": "Staging", "coords": "50,100"}
    ]
    
    for bin_data in test_bins:
        result = make_request("/api/bins", "POST", bin_data)
        if result["success"]:
            print(f"  ✅ 创建库位 {bin_data['bin_id']}")
        else:
            print(f"  ❌ 创建库位失败: {result.get('error', 'Unknown error')}")
    
    # 2. 创建测试物品
    print("\n📦 创建测试物品:")
    test_items = [
        {"item_id": "PALT-0001", "name": "测试托盘1", "description": "用于AI测试的托盘1"},
        {"item_id": "PALT-0002", "name": "测试托盘2", "description": "用于AI测试的托盘2"}
    ]
    
    for item_data in test_items:
        result = make_request("/api/items", "POST", item_data)
        if result["success"]:
            print(f"  ✅ 创建物品 {item_data['item_id']}")
        else:
            print(f"  ❌ 创建物品失败: {result.get('error', 'Unknown error')}")
    
    # 3. 创建测试分配
    print("\n📋 创建测试分配:")
    test_allocations = [
        {"bin_id": "A54", "item_id": "PALT-0001", "qty": 2},
        {"bin_id": "S-01", "item_id": "PALT-0002", "qty": 1}
    ]
    
    for alloc_data in test_allocations:
        result = make_request("/api/allocations", "POST", alloc_data)
        if result["success"]:
            print(f"  ✅ 创建分配 {alloc_data['bin_id']} -> {alloc_data['item_id']}")
        else:
            print(f"  ❌ 创建分配失败: {result.get('error', 'Unknown error')}")

def main():
    """主函数"""
    print("🔧 修复图片识别和AI问答功能")
    print("=" * 50)
    
    # 测试AI功能
    test_ai_functions()
    
    # 创建测试数据
    create_test_data_for_ai()
    
    print("\n🎉 修复完成！")
    print("\n💡 建议:")
    print("  1. 刷新浏览器页面")
    print("  2. 测试自然语言查询功能")
    print("  3. 测试图片扫描功能")
    print("  4. 如果还有问题，检查浏览器控制台错误")

if __name__ == "__main__":
    main()
