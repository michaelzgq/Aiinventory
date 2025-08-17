# 🚀 Vercel 快速部署指南

## 1️⃣ 登录 Vercel
访问 https://vercel.com 并使用 GitHub 账号登录

## 2️⃣ 导入项目
1. 点击 "Add New..." → "Project"
2. 选择 "Import Git Repository"
3. 找到并选择 `michaelzgq/inventoryCheck`

## 3️⃣ 配置环境变量
在 "Environment Variables" 部分添加：

```env
API_KEY=生成一个32位随机字符串
APP_ENV=production
USE_PADDLE_OCR=false
STAGING_BINS=S-01,S-02,S-03,S-04
STAGING_THRESHOLD_HOURS=12
TZ=America/Los_Angeles
STORAGE_BACKEND=local
STORAGE_LOCAL_DIR=/tmp/storage
DB_URL=sqlite:////tmp/inventory.db
```

### 🔐 生成安全的 API_KEY
```bash
# macOS/Linux:
openssl rand -hex 32

# 或使用 Python:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 4️⃣ 部署设置
- **Framework Preset**: Other
- **Root Directory**: 留空
- **Build Command**: 留空（使用默认）
- **Output Directory**: 留空（使用默认）

## 5️⃣ 点击 Deploy
等待 2-3 分钟完成部署

## 📍 部署后访问
- 主页: `https://your-project.vercel.app`
- API 状态: `https://your-project.vercel.app/api/status`
- 健康检查: `https://your-project.vercel.app/health`

## ⚠️ 注意事项
1. **文件存储**: Vercel 只支持 `/tmp` 临时存储
2. **执行时间**: 免费版限制 10 秒
3. **数据库**: 使用 SQLite 会在重启后丢失数据
4. **推荐**: 使用外部数据库服务（如 Supabase、PlanetScale）

## 🔧 故障排除
- **部署失败**: 检查 build logs
- **500 错误**: 查看 Functions 日志
- **模块找不到**: 确认 requirements-vercel.txt 完整

## 📞 需要帮助？
查看完整文档: `DEPLOY_RENDER_VERCEL.md`
