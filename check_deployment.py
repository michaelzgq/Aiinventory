#!/usr/bin/env python3
"""
监控 Render 部署状态
"""

import requests
import time
import json

RENDER_URL = "https://aiinventory-ctyd.onrender.com"
API_KEY = "5b35ccc45997eadabdf54f5e42d1eca6d5f6bc806765340c49b952281d2bc67c"

def check_health():
    """检查系统健康状态"""
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, "系统运行正常"
        else:
            return False, f"状态码: {response.status_code}"
    except Exception as e:
        return False, f"连接异常: {str(e)}"

def check_ingest_endpoints():
    """检查 ingest 端点是否可用"""
    endpoints = [
        ('/api/ingest/bins', '库位导入'),
        ('/api/ingest/orders', '订单导入'),
        ('/api/ingest/allocations', '分配导入'),
        ('/api/ingest/snapshots', '快照导入')
    ]
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    available_endpoints = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{RENDER_URL}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 405:  # Method Not Allowed - 端点存在但不支持 GET
                available_endpoints.append(description)
            elif response.status_code == 200:
                available_endpoints.append(description)
        except Exception:
            pass
    
    return available_endpoints

def main():
    """主函数"""
    print("🔍 监控 Render 部署状态")
    print("="*50)
    print(f"🌐 URL: {RENDER_URL}")
    
    max_attempts = 30  # 最多等待 5 分钟
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n⏰ 第 {attempt} 次检查...")
        
        # 检查健康状态
        is_healthy, health_msg = check_health()
        if is_healthy:
            print(f"✅ 健康检查: {health_msg}")
            
            # 检查 ingest 端点
            print("🔍 检查 ingest 端点...")
            available_endpoints = check_ingest_endpoints()
            
            if len(available_endpoints) == 4:
                print("🎉 所有 ingest 端点已可用！")
                print("📥 现在可以开始导入测试数据了")
                
                # 运行导入
                print("\n🚀 开始自动导入测试数据...")
                import subprocess
                subprocess.run(["python", "quick_import.py"])
                break
            else:
                print(f"⚠️ 部分端点可用: {', '.join(available_endpoints)}")
                print("⏳ 继续等待部署完成...")
        else:
            print(f"❌ 健康检查失败: {health_msg}")
            print("⏳ 继续等待部署完成...")
        
        if attempt < max_attempts:
            print("⏳ 等待 10 秒后重试...")
            time.sleep(10)
    
    if attempt >= max_attempts:
        print("⏰ 等待超时，请手动检查部署状态")

if __name__ == "__main__":
    main()
