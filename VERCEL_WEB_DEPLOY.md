# 🌐 Vercel 网页部署步骤（最简单）

## 1️⃣ 访问 Vercel
打开浏览器访问：https://vercel.com

## 2️⃣ 登录/注册
- 推荐使用 GitHub 账号登录
- 这样可以直接导入您的项目

## 3️⃣ 导入项目
1. 点击右上角 "Add New..." → "Project"
2. 在 "Import Git Repository" 部分
3. 搜索或选择：`michaelzgq/inventoryCheck`
4. 点击 "Import"

## 4️⃣ 配置环境变量
在 "Configure Project" 页面，展开 "Environment Variables" 部分，添加以下变量：

| Key | Value |
|-----|-------|
| API_KEY | `5b35ccc45997eadabdf54f5e42d1eca6d5f6bc806765340c49b952281d2bc67c` |
| APP_ENV | `production` |
| USE_PADDLE_OCR | `false` |
| STAGING_BINS | `S-01,S-02,S-03,S-04` |
| STAGING_THRESHOLD_HOURS | `12` |
| TZ | `America/Los_Angeles` |
| STORAGE_BACKEND | `local` |
| STORAGE_LOCAL_DIR | `/tmp/storage` |
| DB_URL | `sqlite:////tmp/inventory.db` |

## 5️⃣ 部署设置
保持默认设置：
- **Framework Preset**: Other
- **Root Directory**: ./
- **Build Command**: （留空）
- **Output Directory**: （留空）

## 6️⃣ 点击 Deploy
- 点击 "Deploy" 按钮
- 等待 2-3 分钟
- 部署完成！

## 🎉 部署成功后
您会看到：
- ✅ 部署成功的绿色勾
- 🔗 您的应用链接（类似 inventory-check-xxx.vercel.app）
- 📊 可以查看部署日志和函数执行情况

## 🧪 测试您的应用
```bash
# 替换为您的实际部署地址
curl https://inventory-check-xxx.vercel.app/health
curl https://inventory-check-xxx.vercel.app/api/status
```

## 💡 提示
- 首次部署可能需要 3-5 分钟
- 后续更新会自动部署（当您推送到 GitHub）
- 可以在 Vercel Dashboard 查看所有部署历史
