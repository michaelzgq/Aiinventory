#!/usr/bin/env python3
"""
Render 功能测试脚本
用于在 Render 部署后测试所有系统功能
"""

import requests
import json
import time
from typing import Dict, Any, List

class RenderFunctionalTester:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_health_endpoints(self) -> bool:
        """测试健康检查端点"""
        print("\n🏥 测试健康检查端点...")
        
        try:
            # 基础健康检查
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("基础健康检查", True)
            else:
                self.log_test("基础健康检查", False, f"状态码: {response.status_code}")
                return False
            
            # 详细健康检查
            response = requests.get(f"{self.base_url}/health/detailed", timeout=10)
            if response.status_code == 200:
                data = response.json()
                db_status = data.get('database', {}).get('status', 'unknown')
                self.log_test("详细健康检查", True, f"数据库状态: {db_status}")
            else:
                self.log_test("详细健康检查", False, f"状态码: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("健康检查", False, f"异常: {str(e)}")
            return False
    
    def test_api_documentation(self) -> bool:
        """测试 API 文档"""
        print("\n📚 测试 API 文档...")
        
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API 文档访问", True)
                return True
            else:
                self.log_test("API 文档访问", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API 文档访问", False, f"异常: {str(e)}")
            return False
    
    def test_data_endpoints(self) -> bool:
        """测试数据端点"""
        print("\n📊 测试数据端点...")
        
        endpoints = [
            ('/api/bins', '库位查询'),
            ('/api/orders', '订单查询'),
            ('/api/allocations', '分配查询'),
            ('/api/snapshots', '快照查询')
        ]
        
        all_passed = True
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
                    self.log_test(description, True, f"返回 {count} 条记录")
                else:
                    self.log_test(description, False, f"状态码: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(description, False, f"异常: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_nlq_endpoints(self) -> bool:
        """测试自然语言查询端点"""
        print("\n🗣️ 测试自然语言查询...")
        
        try:
            # 获取查询示例
            response = requests.get(f"{self.base_url}/api/nlq/examples", headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.log_test("NLQ 示例查询", True)
            else:
                self.log_test("NLQ 示例查询", False, f"状态码: {response.status_code}")
                return False
            
            # 测试自然语言查询
            test_query = {
                "query": "A54库位有什么商品？",
                "language": "zh"
            }
            
            response = requests.post(
                f"{self.base_url}/api/nlq/query", 
                headers=self.headers,
                json=test_query,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                intent = data.get('intent', 'unknown')
                self.log_test("NLQ 查询处理", True, f"识别意图: {intent}")
            else:
                self.log_test("NLQ 查询处理", False, f"状态码: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("自然语言查询", False, f"异常: {str(e)}")
            return False
    
    def test_reconciliation_endpoints(self) -> bool:
        """测试对账端点"""
        print("\n🤖 测试库存对账...")
        
        try:
            # 获取对账状态
            response = requests.get(f"{self.base_url}/api/reconcile/status", headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.log_test("对账状态查询", True)
            else:
                self.log_test("对账状态查询", False, f"状态码: {response.status_code}")
                return False
            
            # 获取异常列表
            response = requests.get(f"{self.base_url}/api/reconcile/anomalies", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                self.log_test("异常查询", True, f"发现 {count} 个异常")
            else:
                self.log_test("异常查询", False, f"状态码: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("库存对账", False, f"异常: {str(e)}")
            return False
    
    def test_report_endpoints(self) -> bool:
        """测试报告端点"""
        print("\n📋 测试报告生成...")
        
        try:
            # 测试库存报告
            response = requests.get(f"{self.base_url}/api/reconcile/reports/inventory", headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.log_test("库存报告生成", True)
            else:
                self.log_test("库存报告生成", False, f"状态码: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("报告生成", False, f"异常: {str(e)}")
            return False
    
    def test_label_endpoints(self) -> bool:
        """测试标签端点"""
        print("\n🏷️ 测试标签生成...")
        
        try:
            # 获取标签模板
            response = requests.get(f"{self.base_url}/api/labels/templates", headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.log_test("标签模板查询", True)
            else:
                self.log_test("标签模板查询", False, f"状态码: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("标签生成", False, f"异常: {str(e)}")
            return False
    
    def test_dashboard_endpoints(self) -> bool:
        """测试仪表板端点"""
        print("\n📊 测试仪表板端点...")
        
        endpoints = [
            ('/api/orders/today', '今日订单统计'),
            ('/api/snapshots/today', '今日快照统计'),
            ('/api/reconcile/anomalies/today', '今日异常统计'),
            ('/api/snapshots/bins/today', '今日扫描库位统计')
        ]
        
        all_passed = True
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0)
                    self.log_test(description, True, f"数量: {count}")
                else:
                    self.log_test(description, False, f"状态码: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(description, False, f"异常: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print(f"🚀 开始测试 Render 部署: {self.base_url}")
        print(f"🔑 API 密钥: {self.api_key[:8]}...")
        
        start_time = time.time()
        
        # 运行所有测试
        tests = [
            self.test_health_endpoints,
            self.test_api_documentation,
            self.test_data_endpoints,
            self.test_nlq_endpoints,
            self.test_reconciliation_endpoints,
            self.test_report_endpoints,
            self.test_label_endpoints,
            self.test_dashboard_endpoints
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_func.__name__, False, f"测试异常: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 生成测试报告
        print(f"\n{'='*60}")
        print("📊 测试结果汇总")
        print(f"{'='*60}")
        print(f"✅ 通过: {passed}/{total}")
        print(f"❌ 失败: {total - passed}/{total}")
        print(f"⏱️ 耗时: {duration:.2f} 秒")
        print(f"📈 成功率: {(passed/total)*100:.1f}%")
        
        # 显示失败的测试
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed/total)*100,
            'duration': duration,
            'results': self.test_results
        }

def main():
    """主函数"""
    print("🧪 Render 功能测试脚本")
    print("="*50)
    
    # 获取测试参数
    base_url = input("请输入 Render 应用 URL (例如: https://your-app.onrender.com): ").strip()
    if not base_url:
        print("❌ 请输入有效的 URL")
        return
    
    api_key = input("请输入 API 密钥: ").strip()
    if not api_key:
        print("❌ 请输入 API 密钥")
        return
    
    # 创建测试器并运行测试
    tester = RenderFunctionalTester(base_url, api_key)
    results = tester.run_all_tests()
    
    # 保存测试结果
    with open('render_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: render_test_results.json")
    
    # 给出建议
    if results['success_rate'] >= 90:
        print("🎉 系统运行良好！建议可以开始导入测试数据进行深度测试。")
    elif results['success_rate'] >= 70:
        print("⚠️ 系统基本正常，但部分功能需要检查。建议检查失败的端点。")
    else:
        print("🚨 系统存在较多问题，建议检查部署配置和日志。")

if __name__ == "__main__":
    main()
