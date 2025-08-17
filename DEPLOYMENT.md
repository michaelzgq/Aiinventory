# 🚀 Inventory AI 部署指南

## 📋 部署选项

### 1. Railway 部署 (推荐)

**步骤：**
1. 访问 [Railway](https://railway.app)
2. 连接GitHub账户
3. 选择 `michaelzgq/inventoryCheck` 仓库
4. Railway会自动检测Dockerfile并构建

**环境变量设置：**
```
APP_ENV=production
API_KEY=your-secure-api-key-here
DB_URL=postgresql://postgres:password@postgresql.railway.internal:5432/railway
TZ=America/Los_Angeles
USE_PADDLE_OCR=false
STAGING_BINS=S-01,S-02,S-03,S-04
STAGING_THRESHOLD_HOURS=12
STORAGE_BACKEND=local
STORAGE_LOCAL_DIR=/app/storage
```

**数据库配置：**
- 添加PostgreSQL服务
- 使用Railway提供的DATABASE_URL

### 2. Vercel 部署

**步骤：**
1. 访问 [Vercel](https://vercel.com)
2. 导入GitHub仓库
3. Vercel会自动检测并部署

**注意：** Vercel适合前端和轻量API，数据库需要外部服务

### 3. Render 部署

**步骤：**
1. 访问 [Render](https://render.com)
2. 连接GitHub仓库
3. 选择Docker部署模式

### 4. Heroku 部署

**步骤：**
1. 安装Heroku CLI
2. 创建应用：`heroku create inventory-ai-app`
3. 推送代码：`git push heroku main`

### 5. Digital Ocean App Platform

**步骤：**
1. 访问Digital Ocean App Platform
2. 从GitHub导入仓库
3. 配置环境变量

## 🔧 生产环境配置

### 必须更改的配置：
```env
# 生产环境必须修改
API_KEY=your-super-secure-random-key-here
APP_ENV=production

# 数据库 (推荐PostgreSQL)
DB_URL=postgresql://user:password@host:port/database

# 存储 (可选用S3)
STORAGE_BACKEND=s3
S3_ENDPOINT=https://your-region.amazonaws.com
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
```

### 安全检查清单：
- [ ] 更改默认API密钥
- [ ] 启用HTTPS
- [ ] 配置CORS策略
- [ ] 设置防火墙规则
- [ ] 启用日志监控
- [ ] 配置备份策略

## 📊 部署后测试

### 1. 健康检查
```bash
curl https://your-app.railway.app/health
```

### 2. API文档
访问：`https://your-app.railway.app/docs`

### 3. 功能测试
1. 上传示例数据
2. 测试自然语言查询
3. 运行对账功能
4. 下载报告

### 4. 性能监控
- 访问速度测试
- API响应时间
- 内存使用情况
- 并发处理能力

## 🎯 快速部署命令

### Railway (使用CLI)
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录并部署
railway login
railway link
railway up
```

### Docker本地测试
```bash
# 构建镜像
docker build -t inventory-ai -f docker/Dockerfile .

# 运行容器
docker run -p 8000:8000 inventory-ai
```

## 🔍 故障排除

### 常见问题：
1. **端口配置** - 确保使用 `$PORT` 环境变量
2. **依赖安装** - 检查requirements.txt
3. **数据库连接** - 验证DATABASE_URL
4. **静态文件** - 检查静态文件路径
5. **环境变量** - 确认所有必需变量已设置

### 调试命令：
```bash
# 查看日志
railway logs

# 连接数据库
railway connect postgresql

# 运行命令
railway run python backend/app/main.py
```

## 📈 扩展建议

### 生产优化：
- 使用Redis缓存
- 配置CDN加速
- 启用数据库读写分离
- 实现负载均衡
- 添加监控告警

### 功能扩展：
- 用户认证系统
- 多租户支持
- 移动APP接口
- 数据分析dashboard
- AI预测功能

## 🌐 访问地址

部署成功后，应用将在以下地址可用：
- **Railway**: `https://inventorycheck-production.up.railway.app`
- **Vercel**: `https://inventory-check.vercel.app`
- **Render**: `https://inventory-ai.onrender.com`

记得保存这些地址并分享给团队使用！