#!/usr/bin/env python3
"""
快速导入脚本 - 使用预设的 Render 配置
"""

import requests
import json
import time

# 配置信息
RENDER_URL = "https://aiinventory-ctyd.onrender.com"
API_KEY = "5b35ccc45997eadabdf54f5e42d1eca6d5f6bc806765340c49b952281d2bc67c"

def test_connection():
    """测试连接"""
    print("🔗 测试 Render 连接...")
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 连接成功！系统运行正常")
            return True
        else:
            print(f"❌ 连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接异常: {str(e)}")
        return False

def import_data(file_path, endpoint_name, description):
    """导入数据文件"""
    print(f"\n📥 正在导入{description}...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (f'{endpoint_name}.csv', f, 'text/csv')}
            response = requests.post(
                f"{RENDER_URL}/api/ingest/{endpoint_name}",
                headers={'Authorization': f'Bearer {API_KEY}'},
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('imported_count', 0)
            print(f"✅ {description}导入成功: {count} 条记录")
            return True
        else:
            print(f"❌ {description}导入失败: 状态码 {response.status_code}")
            print(f"   错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {description}导入异常: {str(e)}")
        return False

def verify_import():
    """验证导入结果"""
    print("\n🔍 验证导入结果...")
    
    endpoints = [
        ('/api/bins', '库位数据'),
        ('/api/orders', '订单数据'),
        ('/api/allocations', '分配数据'),
        ('/api/snapshots', '快照数据')
    ]
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{RENDER_URL}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict) and 'snapshots' in data:
                    count = len(data['snapshots'])
                else:
                    count = 0
                print(f"✅ {description}: 确认 {count} 条记录")
            else:
                print(f"❌ {description}: 验证失败，状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: 验证异常 {str(e)}")

def main():
    """主函数"""
    print("🚀 开始自动导入到 Render")
    print("="*50)
    print(f"🌐 URL: {RENDER_URL}")
    print(f"🔑 API Key: {API_KEY[:8]}...")
    
    # 1. 测试连接
    if not test_connection():
        print("❌ 无法连接到 Render，请检查网络或应用状态")
        return
    
    # 2. 按顺序导入数据
    import_steps = [
        ('sample_data/bins.csv', 'bins', '库位数据'),
        ('sample_data/orders.csv', 'orders', '订单数据'),
        ('sample_data/allocations.csv', 'allocations', '分配数据'),
        ('sample_data/snapshots.csv', 'snapshots', '快照数据')
    ]
    
    success_count = 0
    total_count = len(import_steps)
    
    for file_path, endpoint, description in import_steps:
        if import_data(file_path, endpoint, description):
            success_count += 1
        else:
            print(f"⚠️ {description}导入失败，但继续导入其他数据...")
            time.sleep(2)
    
    # 3. 验证导入结果
    if success_count > 0:
        verify_import()
    
    # 4. 生成报告
    print(f"\n{'='*50}")
    print("📊 导入结果汇总")
    print(f"{'='*50}")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    print(f"📈 成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有数据导入成功！")
        print("💡 现在可以开始测试系统功能了")
    else:
        print(f"\n⚠️ 部分数据导入失败，成功导入了 {success_count} 个文件")
        print("💡 可以重新运行导入脚本，或者手动导入失败的数据")

if __name__ == "__main__":
    main()
