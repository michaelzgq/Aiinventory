# 📚 GitHub 仓库管理指南

## ✅ 推送完成！

您的项目已成功推送到新仓库：
- 🆕 **新仓库**: https://github.com/michaelzgq/Aiinventory
- 📦 **原仓库**: https://github.com/michaelzgq/inventoryCheck

## 📍 当前远程仓库配置

```bash
# 查看所有远程仓库
git remote -v

# 结果：
aiinventory  https://github.com/michaelzgq/Aiinventory.git
origin       https://github.com/michaelzgq/inventoryCheck.git
```

## 🔄 如何使用两个仓库

### 推送到新仓库 (Aiinventory)
```bash
git push aiinventory main
```

### 推送到原仓库 (inventoryCheck)
```bash
git push origin main
```

### 同时推送到两个仓库
```bash
git push origin main && git push aiinventory main
```

## 🎯 设置默认仓库

如果您想将 Aiinventory 设为默认仓库：

### 方法 1：更改 origin 指向新仓库
```bash
# 删除旧的 origin
git remote remove origin

# 将 aiinventory 重命名为 origin
git remote rename aiinventory origin
```

### 方法 2：保留两个仓库，但设置默认推送
```bash
# 设置默认推送到 aiinventory
git push -u aiinventory main
```

## 🚀 Vercel 部署更新

如果您想在 Vercel 上使用新仓库：

1. **在 Vercel Dashboard**
   - 进入项目设置
   - 找到 "Git" 部分
   - 点击 "Disconnect from Git"
   - 重新连接，选择新仓库 `Aiinventory`

2. **或创建新的 Vercel 项目**
   - 保留原项目
   - 创建新项目，选择 `Aiinventory` 仓库
   - 复制环境变量设置

## 📝 日常工作流程

### 1. 做出更改后
```bash
git add .
git commit -m "您的提交信息"
```

### 2. 推送到新仓库
```bash
git push aiinventory main
```

### 3. 如需同步到原仓库
```bash
git push origin main
```

## 🔗 快速访问

- **新仓库 (Aiinventory)**: https://github.com/michaelzgq/Aiinventory
- **原仓库 (inventoryCheck)**: https://github.com/michaelzgq/inventoryCheck
- **Vercel 部署**: https://inventory-check-three.vercel.app/

## 💡 建议

- 如果 `Aiinventory` 是主要开发仓库，建议将其设为 `origin`
- 可以保留 `inventoryCheck` 作为备份或存档
- 记得更新 README 中的仓库链接
- 更新部署平台的 Git 连接
