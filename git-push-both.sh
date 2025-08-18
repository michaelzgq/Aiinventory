#!/bin/bash
# 推送到两个 GitHub 仓库的脚本

echo "🚀 推送到多个 GitHub 仓库..."
echo ""

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo "⚠️  检测到未提交的更改："
    git status -s
    echo ""
    read -p "是否要先提交这些更改？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入提交信息: " commit_msg
        git add .
        git commit -m "$commit_msg"
    fi
fi

echo ""
echo "📤 开始推送..."

# 推送到原仓库
echo "1️⃣ 推送到 inventoryCheck..."
git push origin main
if [ $? -eq 0 ]; then
    echo "✅ inventoryCheck 推送成功"
else
    echo "❌ inventoryCheck 推送失败"
fi

echo ""

# 推送到新仓库
echo "2️⃣ 推送到 Aiinventory..."
git push aiinventory main
if [ $? -eq 0 ]; then
    echo "✅ Aiinventory 推送成功"
else
    echo "❌ Aiinventory 推送失败"
fi

echo ""
echo "🎉 推送完成！"
echo ""
echo "📍 仓库地址："
echo "  - inventoryCheck: https://github.com/michaelzgq/inventoryCheck"
echo "  - Aiinventory: https://github.com/michaelzgq/Aiinventory"
