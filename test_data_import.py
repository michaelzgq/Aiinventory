#!/usr/bin/env python3
"""
测试数据导入脚本
用于在 Render 上快速导入所有测试数据，测试系统功能
"""

import os
import sys
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def load_csv_data(file_path: str) -> List[Dict[str, Any]]:
    """加载 CSV 文件数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f"❌ 加载 {file_path} 失败: {e}")
        return []

def create_test_images():
    """创建测试用的图片文件"""
    try:
        # 创建存储目录
        os.makedirs('storage/photos', exist_ok=True)
        os.makedirs('storage/reports', exist_ok=True)
        os.makedirs('storage/temp', exist_ok=True)
        
        # 创建一些测试图片文件（空文件，用于测试）
        test_images = [
            'storage/photos/photo_a54_001.jpg',
            'storage/photos/photo_b51_001.jpg',
            'storage/photos/photo_c51_001.jpg',
            'storage/photos/photo_s01_001.jpg',
            'storage/photos/photo_r01_001.jpg',
            'storage/photos/photo_q01_001.jpg'
        ]
        
        for img_path in test_images:
            with open(img_path, 'w') as f:
                f.write(f"# Test image: {img_path}\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n")
        
        print(f"✅ 创建了 {len(test_images)} 个测试图片文件")
        
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}")

def generate_test_data_summary():
    """生成测试数据摘要"""
    print("\n" + "="*60)
    print("📊 测试数据摘要")
    print("="*60)
    
    # 统计各文件数据量
    data_files = {
        'orders.csv': '订单数据',
        'bins.csv': '库位数据', 
        'allocations.csv': '分配数据',
        'snapshots.csv': '快照数据'
    }
    
    total_items = 0
    for filename, description in data_files.items():
        file_path = f"sample_data/{filename}"
        if os.path.exists(file_path):
            data = load_csv_data(file_path)
            count = len(data)
            total_items += count
            print(f"📁 {description}: {count} 条记录")
        else:
            print(f"❌ {description}: 文件不存在")
    
    print(f"\n📈 总计: {total_items} 条测试数据")
    
    # 显示数据分布
    print("\n🗂️ 数据分布:")
    print("  • 订单: 30 个 (包含 5 种状态)")
    print("  • 库位: 70 个 (A/B/C/D 区 + 出库/收货/质检区)")
    print("  • 分配: 100 个商品分配到不同库位")
    print("  • 快照: 50 个库存快照记录")
    
    print("\n🏷️ 测试场景覆盖:")
    print("  • QR码扫描和识别")
    print("  • 库位 OCR 识别")
    print("  • 库存对账和异常检测")
    print("  • 自然语言查询")
    print("  • 报告生成和导出")
    print("  • 标签打印和管理")
    print("  • API 接口测试")

def create_import_instructions():
    """创建数据导入说明"""
    instructions = """
# 🚀 Render 测试数据导入指南

## 📋 前置条件
1. 确保系统已在 Render 上成功部署
2. 获取系统的 API 密钥
3. 确保数据库连接正常

## 🔑 获取 API 密钥
在 Render 环境变量中查看 `API_KEY` 值

## 📥 数据导入步骤

### 1. 导入库位数据
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/bins" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@sample_data/bins.csv"
```

### 2. 导入订单数据
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/orders" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@sample_data/orders.csv"
```

### 3. 导入分配数据
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/allocations" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@sample_data/allocations.csv"
```

### 4. 导入快照数据（可选）
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/snapshots" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@sample_data/snapshots.csv"
```

## 🧪 功能测试清单

### ✅ 基础功能测试
- [ ] 系统健康检查: `/health`
- [ ] 数据库连接: `/health/detailed`
- [ ] API 文档: `/docs`

### ✅ 数据管理测试
- [ ] 库位数据查询: `/api/bins`
- [ ] 订单数据查询: `/api/orders`
- [ ] 分配数据查询: `/api/allocations`

### ✅ 智能功能测试
- [ ] 快照上传: `/api/snapshots/upload`
- [ ] 自然语言查询: `/api/nlq/query`
- [ ] 库存对账: `/api/reconcile/run`

### ✅ 报告功能测试
- [ ] 库存报告: `/api/reports/inventory`
- [ ] 异常报告: `/api/reconcile/reports/generate`
- [ ] 标签生成: `/api/labels/generate`

## 🔍 测试数据说明

### 订单数据 (30条)
- 包含多种 SKU: SKU-5566, SKU-8899, SKU-7777, SKU-9999 等
- 状态: pending, shipped
- 日期范围: 2025-08-17 到 2025-08-29

### 库位数据 (70个)
- A区: A51-A60 (10个)
- B区: B51-B60 (10个)  
- C区: C51-C60 (10个)
- D区: D51-D60 (10个)
- 出库区: S-01 到 S-10 (10个)
- 收货区: R-01 到 R-10 (10个)
- 质检区: Q-01 到 Q-10 (10个)

### 分配数据 (100条)
- 商品: PALT-0001 到 PALT-0100
- 状态: allocated, staged, received, quality_check
- 覆盖所有库位区域

### 快照数据 (50条)
- 时间范围: 2025-08-18 09:00-21:15
- 置信度: 0.87-0.95
- 包含照片引用和备注

## 🚨 注意事项

1. **API 密钥**: 所有请求都需要有效的 API 密钥
2. **文件格式**: 确保 CSV 文件编码为 UTF-8
3. **数据顺序**: 建议按库位→订单→分配→快照的顺序导入
4. **测试环境**: 建议在测试环境先验证，再导入生产环境

## 📞 技术支持

如遇到问题，请检查:
1. API 密钥是否正确
2. 网络连接是否正常
3. 系统日志中的错误信息
4. 数据库连接状态

"""
    
    with open('RENDER_TEST_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ 已创建 Render 测试指南: RENDER_TEST_GUIDE.md")

def main():
    """主函数"""
    print("🚀 开始生成测试数据...")
    
    # 检查数据文件
    sample_dir = "sample_data"
    if not os.path.exists(sample_dir):
        print(f"❌ 样本数据目录不存在: {sample_dir}")
        return
    
    # 创建测试图片
    create_test_images()
    
    # 生成数据摘要
    generate_test_data_summary()
    
    # 创建导入指南
    create_import_instructions()
    
    print("\n🎉 测试数据准备完成！")
    print("📖 请查看 RENDER_TEST_GUIDE.md 了解如何在 Render 上导入数据")

if __name__ == "__main__":
    main()
