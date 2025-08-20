#!/usr/bin/env python3
"""
测试部署兼容性
"""

def test_imports():
    """测试所有必要的导入"""
    try:
        print("🔍 测试导入...")
        
        # 测试基础模块
        print("  📦 测试基础模块...")
        import fastapi
        import uvicorn
        import sqlalchemy
        print("    ✅ 基础模块导入成功")
        
        # 测试应用模块
        print("  🏗️ 测试应用模块...")
        from backend.app.config import settings
        from backend.app.database import get_db
        from backend.app.deps import verify_api_key
        print("    ✅ 应用模块导入成功")
        
        # 测试模型
        print("  🗃️ 测试数据模型...")
        from backend.app.models import Bin, Item, Order, Allocation, Snapshot
        print("    ✅ 数据模型导入成功")
        
        # 测试路由
        print("  🛣️ 测试路由...")
        from backend.app.routers import orders, allocations, snapshots, reconcile, queries, labels, health, ingest
        print("    ✅ 现有路由导入成功")
        
        # 测试新路由
        print("  🆕 测试新路由...")
        from backend.app.routers.bins import router as bins_router
        from backend.app.routers.items import router as items_router
        print("    ✅ 新路由导入成功")
        
        # 测试主应用
        print("  🚀 测试主应用...")
        from backend.app.main import app
        print("    ✅ 主应用导入成功")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_startup():
    """测试应用启动"""
    try:
        print("\n🔍 测试应用启动...")
        
        from backend.app.main import app
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"  📍 发现 {len(routes)} 个路由")
        
        # 检查特定路由
        bins_routes = [r for r in routes if 'bins' in r]
        items_routes = [r for r in routes if 'items' in r]
        
        print(f"  🏠 Bins 路由: {len(bins_routes)} 个")
        print(f"  📦 Items 路由: {len(items_routes)} 个")
        
        print("    ✅ 应用启动测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 应用启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 部署兼容性测试")
    print("=" * 50)
    
    # 运行测试
    imports_ok = test_imports()
    startup_ok = test_app_startup()
    
    if imports_ok and startup_ok:
        print("\n🎉 所有测试通过！代码应该可以正常部署。")
    else:
        print("\n❌ 测试失败，需要修复问题。")
