#!/usr/bin/env python3
"""
Render 自动数据导入脚本
自动将测试数据导入到 Render 部署的应用中
"""

import requests
import json
import time
import os
from typing import Dict, Any, List

class RenderDataImporter:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.import_results = []
    
    def log_import(self, operation: str, success: bool, details: str = ""):
        """记录导入结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} {operation}")
        if details:
            print(f"   详情: {details}")
        
        self.import_results.append({
            'operation': operation,
            'success': success,
            'details': details
        })
    
    def test_connection(self) -> bool:
        """测试连接"""
        print("🔗 测试 Render 连接...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_import("连接测试", True, "系统连接正常")
                return True
            else:
                self.log_import("连接测试", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_import("连接测试", False, f"连接异常: {str(e)}")
            return False
    
    def import_bins(self) -> bool:
        """导入库位数据"""
        print("\n📁 导入库位数据...")
        try:
            with open('sample_data/bins.csv', 'rb') as f:
                files = {'file': ('bins.csv', f, 'text/csv')}
                response = requests.post(
                    f"{self.base_url}/api/ingest/bins",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('imported_count', 0)
                self.log_import("库位导入", True, f"成功导入 {count} 条记录")
                return True
            else:
                error_detail = response.text
                self.log_import("库位导入", False, f"状态码: {response.status_code}, 错误: {error_detail}")
                return False
                
        except Exception as e:
            self.log_import("库位导入", False, f"导入异常: {str(e)}")
            return False
    
    def import_orders(self) -> bool:
        """导入订单数据"""
        print("\n📋 导入订单数据...")
        try:
            with open('sample_data/orders.csv', 'rb') as f:
                files = {'file': ('orders.csv', f, 'text/csv')}
                response = requests.post(
                    f"{self.base_url}/api/ingest/orders",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('imported_count', 0)
                self.log_import("订单导入", True, f"成功导入 {count} 条记录")
                return True
            else:
                error_detail = response.text
                self.log_import("订单导入", False, f"状态码: {response.status_code}, 错误: {error_detail}")
                return False
                
        except Exception as e:
            self.log_import("订单导入", False, f"导入异常: {str(e)}")
            return False
    
    def import_allocations(self) -> bool:
        """导入分配数据"""
        print("\n📦 导入分配数据...")
        try:
            with open('sample_data/allocations.csv', 'rb') as f:
                files = {'file': ('allocations.csv', f, 'text/csv')}
                response = requests.post(
                    f"{self.base_url}/api/ingest/allocations",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('imported_count', 0)
                self.log_import("分配导入", True, f"成功导入 {count} 条记录")
                return True
            else:
                error_detail = response.text
                self.log_import("分配导入", False, f"状态码: {response.status_code}, 错误: {error_detail}")
                return False
                
        except Exception as e:
            self.log_import("分配导入", False, f"导入异常: {str(e)}")
            return False
    
    def import_snapshots(self) -> bool:
        """导入快照数据"""
        print("\n📸 导入快照数据...")
        try:
            with open('sample_data/snapshots.csv', 'rb') as f:
                files = {'file': ('snapshots.csv', f, 'text/csv')}
                response = requests.post(
                    f"{self.base_url}/api/ingest/snapshots",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('imported_count', 0)
                self.log_import("快照导入", True, f"成功导入 {count} 条记录")
                return True
            else:
                error_detail = response.text
                self.log_import("快照导入", False, f"状态码: {response.status_code}, 错误: {error_detail}")
                return False
                
        except Exception as e:
            self.log_import("快照导入", False, f"导入异常: {str(e)}")
            return False
    
    def verify_import(self) -> bool:
        """验证导入结果"""
        print("\n🔍 验证导入结果...")
        
        endpoints = [
            ('/api/bins', '库位数据'),
            ('/api/orders', '订单数据'),
            ('/api/allocations', '分配数据'),
            ('/api/snapshots', '快照数据')
        ]
        
        all_verified = True
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict) and 'snapshots' in data:
                        count = len(data['snapshots'])
                    else:
                        count = 0
                    self.log_import(f"验证{description}", True, f"确认 {count} 条记录")
                else:
                    self.log_import(f"验证{description}", False, f"状态码: {response.status_code}")
                    all_verified = False
            except Exception as e:
                self.log_import(f"验证{description}", False, f"验证异常: {str(e)}")
                all_verified = False
        
        return all_verified
    
    def run_import(self) -> Dict[str, Any]:
        """运行完整导入流程"""
        print(f"🚀 开始自动导入到 Render: {self.base_url}")
        print(f"🔑 API 密钥: {self.api_key[:8]}...")
        
        start_time = time.time()
        
        # 1. 测试连接
        if not self.test_connection():
            print("❌ 连接测试失败，无法继续导入")
            return {'success': False, 'error': '连接失败'}
        
        # 2. 按顺序导入数据
        import_steps = [
            (self.import_bins, "库位数据"),
            (self.import_orders, "订单数据"),
            (self.import_allocations, "分配数据"),
            (self.import_snapshots, "快照数据")
        ]
        
        all_success = True
        for import_func, description in import_steps:
            print(f"\n📥 正在导入{description}...")
            if not import_func():
                all_success = False
                print(f"⚠️ {description}导入失败，但继续导入其他数据...")
                time.sleep(2)  # 等待一下再继续
        
        # 3. 验证导入结果
        if all_success:
            print("\n🔍 验证导入结果...")
            verify_success = self.verify_import()
        else:
            verify_success = False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 生成导入报告
        print(f"\n{'='*60}")
        print("📊 导入结果汇总")
        print(f"{'='*60}")
        
        success_count = sum(1 for r in self.import_results if r['success'])
        total_count = len(self.import_results)
        
        print(f"✅ 成功: {success_count}/{total_count}")
        print(f"❌ 失败: {total_count - success_count}/{total_count}")
        print(f"⏱️ 耗时: {duration:.2f} 秒")
        print(f"📈 成功率: {(success_count/total_count)*100:.1f}%")
        
        # 显示失败的导入
        failed_imports = [r for r in self.import_results if not r['success']]
        if failed_imports:
            print(f"\n❌ 失败的导入:")
            for imp in failed_imports:
                print(f"  • {imp['operation']}: {imp['details']}")
        
        return {
            'success': all_success and verify_success,
            'total_operations': total_count,
            'successful_operations': success_count,
            'success_rate': (success_count/total_count)*100,
            'duration': duration,
            'results': self.import_results
        }

def main():
    """主函数"""
    print("🚀 Render 自动数据导入工具")
    print("="*50)
    
    # 获取导入参数
    base_url = input("请输入 Render 应用 URL (例如: https://your-app.onrender.com): ").strip()
    if not base_url:
        print("❌ 请输入有效的 URL")
        return
    
    api_key = input("请输入 API 密钥: ").strip()
    if not api_key:
        print("❌ 请输入 API 密钥")
        return
    
    # 确认导入
    print(f"\n📋 导入配置:")
    print(f"  URL: {base_url}")
    print(f"  API Key: {api_key[:8]}...")
    
    confirm = input("\n确认开始导入? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 导入已取消")
        return
    
    # 创建导入器并运行
    importer = RenderDataImporter(base_url, api_key)
    results = importer.run_import()
    
    # 保存导入结果
    with open('render_import_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 导入结果已保存到: render_import_results.json")
    
    # 给出建议
    if results['success']:
        print("🎉 数据导入成功！现在可以开始测试系统功能了。")
        print("💡 建议运行功能测试脚本验证所有功能:")
        print("   python render_functional_test.py")
    else:
        print("⚠️ 部分数据导入失败，请检查上述错误信息。")
        print("💡 可以重新运行导入脚本，或者手动导入失败的数据。")

if __name__ == "__main__":
    main()
