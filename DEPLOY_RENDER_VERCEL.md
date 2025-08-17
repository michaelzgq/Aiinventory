# 🚀 部署到 Render 和 Vercel 指南

## 📋 前置准备

确保您的代码已推送到 GitHub：
```bash
git add .
git commit -m "准备部署到 Render 和 Vercel"
git push origin main
```

## 🔵 Render 部署步骤

### 方法 1：使用 Docker（推荐）

1. **登录 Render**
   - 访问 https://render.com
   - 使用 GitHub 账户登录

2. **创建新的 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接您的 GitHub 仓库：`michaelzgq/inventoryCheck`
   - 选择 `main` 分支

3. **配置服务**
   - **Name**: `inventory-ai`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./docker/Dockerfile`
   - **Instance Type**: 选择 Free 或 Starter

4. **设置环境变量**
   点击 "Advanced" 添加以下环境变量：
   ```
   APP_ENV=production
   API_KEY=<点击 Generate 自动生成>
   TZ=America/Los_Angeles
   USE_PADDLE_OCR=false
   STAGING_BINS=S-01,S-02,S-03,S-04
   STAGING_THRESHOLD_HOURS=12
   STORAGE_BACKEND=local
   STORAGE_LOCAL_DIR=/app/storage
   ```

5. **添加数据库（可选）**
   - 点击 "New +" → "PostgreSQL"
   - 创建后复制 Connection String
   - 在 Web Service 中添加环境变量：
     `DB_URL=<PostgreSQL Connection String>`

6. **部署**
   - 点击 "Create Web Service"
   - 等待构建和部署完成（约 5-10 分钟）

### 方法 2：使用 Python 环境（备选）

如果 Docker 部署失败，可以使用 `render-simple.yaml`：

1. 在 Render Dashboard 中选择 "New +" → "Blueprint"
2. 连接您的 GitHub 仓库
3. 选择 `render-simple.yaml` 作为配置文件
4. 点击 "Apply"

### 访问您的应用

部署成功后，您的应用将在以下地址可用：
- **主页**: `https://inventory-ai.onrender.com`
- **API 文档**: `https://inventory-ai.onrender.com/docs`
- **健康检查**: `https://inventory-ai.onrender.com/health`

## 🟢 Vercel 部署步骤

### 方法 1：使用 Vercel Dashboard（推荐）

1. **登录 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账户登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择 GitHub 仓库：`michaelzgq/inventoryCheck`

3. **配置项目**
   - **Framework Preset**: 选择 "Other"
   - **Root Directory**: 留空（使用项目根目录）

4. **设置环境变量**
   在 "Environment Variables" 部分添加：
   ```
   API_KEY=<生成一个安全的密钥>
   APP_ENV=production
   USE_PADDLE_OCR=false
   STAGING_BINS=S-01,S-02,S-03,S-04
   STAGING_THRESHOLD_HOURS=12
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 2-3 分钟）

### 方法 2：使用 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### Vercel 部署说明

⚠️ **重要提示**：
- Vercel 是 Serverless 平台，适合轻量级 API
- 文件系统是只读的（除了 `/tmp` 目录）
- 函数执行时间限制：10 秒（免费版）
- 不支持持久化存储

### 访问您的应用

部署成功后：
- **简化版 API**: `https://inventory-check.vercel.app`
- **API 状态**: `https://inventory-check.vercel.app/api/status`
- **健康检查**: `https://inventory-check.vercel.app/health`

## 🔧 部署后配置

### 1. 设置自定义域名（可选）

**Render**:
- 在服务设置中点击 "Custom Domains"
- 添加您的域名并配置 DNS

**Vercel**:
- 在项目设置中点击 "Domains"
- 添加您的域名并按提示配置

### 2. 监控和日志

**Render**:
- 查看 "Logs" 标签页实时日志
- 设置 "Health Checks" 监控服务状态

**Vercel**:
- 查看 "Functions" 标签页的执行日志
- 使用 "Analytics" 监控性能

## 📊 功能对比

| 功能 | Render | Vercel |
|------|--------|--------|
| 完整 FastAPI | ✅ | ⚠️ (受限) |
| 持久化存储 | ✅ | ❌ |
| PostgreSQL | ✅ | ❌ (需外部) |
| 文件上传 | ✅ | ⚠️ (/tmp only) |
| WebSocket | ✅ | ❌ |
| 定时任务 | ✅ | ⚠️ (需 cron) |
| 免费额度 | 750小时/月 | 无限 |
| 冷启动 | 慢 | 快 |

## 🚨 故障排除

### Render 常见问题

1. **构建失败**
   - 检查 `requirements.txt` 是否完整
   - 确认 Python 版本兼容性
   - 查看构建日志定位错误

2. **服务无响应**
   - 检查环境变量是否正确
   - 确认端口绑定使用 `$PORT`
   - 查看运行日志

### Vercel 常见问题

1. **函数超时**
   - 优化代码减少执行时间
   - 考虑升级到 Pro 版（60秒限制）

2. **模块导入错误**
   - 检查 `requirements-vercel.txt`
   - 确保所有依赖都包含

3. **CORS 错误**
   - 已在代码中配置，如仍有问题检查 `vercel.json`

## 📞 需要帮助？

- **Render 文档**: https://render.com/docs
- **Vercel 文档**: https://vercel.com/docs
- **项目 Issues**: https://github.com/michaelzgq/inventoryCheck/issues

祝您部署顺利！🎉
