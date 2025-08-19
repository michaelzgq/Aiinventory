
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
curl -X POST "https://your-app.onrender.com/api/ingest/bins"   -H "Authorization: Bearer YOUR_API_KEY"   -F "file=@sample_data/bins.csv"
```

### 2. 导入订单数据
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/orders"   -H "Authorization: Bearer YOUR_API_KEY"   -F "file=@sample_data/orders.csv"
```

### 3. 导入分配数据
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/allocations"   -H "Authorization: Bearer YOUR_API_KEY"   -F "file=@sample_data/allocations.csv"
```

### 4. 导入快照数据（可选）
```bash
curl -X POST "https://your-app.onrender.com/api/ingest/snapshots"   -H "Authorization: Bearer YOUR_API_KEY"   -F "file=@sample_data/snapshots.csv"
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

