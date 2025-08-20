#!/usr/bin/env python3
"""
简化的启动脚本，用于测试兼容性
"""

import sys
import os

def main():
    """主函数"""
    print("🚀 简化启动测试")
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    
    try:
        # 设置环境变量
        os.environ.setdefault('APP_ENV', 'production')
        
        # 导入应用
        print("📦 导入应用...")
        from backend.app.main import app
        print("✅ 应用导入成功")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"📍 发现 {len(routes)} 个路由")
        
        # 检查新路由
        bins_routes = [r for r in routes if 'bins' in r]
        items_routes = [r for r in routes if 'items' in r]
        
        print(f"🏠 Bins 路由: {len(bins_routes)} 个")
        print(f"📦 Items 路由: {len(items_routes)} 个")
        
        print("🎉 启动测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
