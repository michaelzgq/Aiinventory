# 🚀 切换到 Render 部署指南

## 为什么选择 Render？

✅ **完整功能支持** - 可以运行完整的 FastAPI 应用
✅ **免费层够用** - 750 小时/月，对演示足够
✅ **支持数据库** - 免费 PostgreSQL
✅ **文件存储** - 支持上传和持久化
✅ **简单部署** - 连接 GitHub 即可

## 🎯 5分钟部署步骤

### 1. 访问 Render
https://render.com

### 2. 注册/登录
使用 GitHub 账号登录最方便

### 3. 创建新的 Web Service
- 点击 "New +" → "Web Service"
- 连接 GitHub 账户
- 选择仓库：`michaelzgq/Aiinventory`

### 4. 配置服务
- **Name**: `inventory-ai`
- **Environment**: `Docker`
- **Branch**: `main`

### 5. 环境变量
点击 "Advanced" 添加：
```
APP_ENV=production
API_KEY=render-secure-key-2025
DB_URL=<会自动设置>
APP_TIMEZONE=America/Los_Angeles
USE_PADDLE_OCR=false
STAGING_BINS=S-01,S-02,S-03,S-04
STAGING_THRESHOLD_HOURS=12
STORAGE_BACKEND=local
STORAGE_LOCAL_DIR=/app/storage
```

### 6. 选择免费套餐
- Instance Type: **Free**

### 7. 部署！
点击 "Create Web Service"

## ⏰ 预期结果

- 部署时间：5-10 分钟（首次）
- 访问地址：`https://inventory-ai.onrender.com`
- 所有功能都可用！

## 📊 功能对比

| 功能 | Vercel | Render |
|------|--------|--------|
| 完整界面 | ❌ | ✅ |
| 扫描功能 | ❌ | ✅ |
| 数据上传 | ❌ | ✅ |
| 数据库 | ❌ | ✅ |
| 文件存储 | ❌ | ✅ |
| API 完整性 | ❌ | ✅ |
| 部署难度 | 困难 | 简单 |

## 🎉 额外好处

1. **自动 HTTPS**
2. **自动部署** - Git push 后自动更新
3. **查看日志** - 实时查看应用日志
4. **数据库管理** - 内置 PostgreSQL

## 💡 小贴士

- 免费层会在 15 分钟无活动后休眠
- 首次访问可能需要 30 秒启动
- 可以升级到付费版获得更好性能

## 🔗 相关文件

- `render.yaml` - 已配置好
- `docker/Dockerfile` - 已准备好
- 所有代码都兼容！

---

**立即开始**: https://render.com 🚀
