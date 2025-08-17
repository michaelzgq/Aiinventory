#!/bin/bash

echo "🔍 Vercel 部署前检查..."
echo ""

# 检查必需文件
echo "📁 检查必需文件..."
required_files=(
    "vercel.json"
    "api/index.py"
    "requirements-vercel.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 缺失"
        exit 1
    fi
done

# 检查 Python 版本
echo ""
echo "🐍 检查 Python 版本..."
python_version=$(python3 --version 2>&1)
echo "当前版本: $python_version"

# 检查依赖
echo ""
echo "📦 检查依赖..."
if [ -f "requirements-vercel.txt" ]; then
    echo "依赖文件内容:"
    head -10 requirements-vercel.txt
else
    echo "⚠️  警告: requirements-vercel.txt 不存在"
fi

# 检查环境变量模板
echo ""
echo "🔐 环境变量模板:"
cat << EOF
请在 Vercel Dashboard 中设置以下环境变量:

API_KEY=<生成一个安全的密钥>
APP_ENV=production
USE_PADDLE_OCR=false
STAGING_BINS=S-01,S-02,S-03,S-04
STAGING_THRESHOLD_HOURS=12
TZ=America/Los_Angeles
STORAGE_BACKEND=local
STORAGE_LOCAL_DIR=/tmp/storage
DB_URL=sqlite:////tmp/inventory.db
EOF

echo ""
echo "✨ 检查完成！"
echo ""
echo "📌 部署步骤:"
echo "1. 登录 Vercel: https://vercel.com"
echo "2. 导入项目: Import Git Repository"
echo "3. 选择: michaelzgq/inventoryCheck"
echo "4. 设置上述环境变量"
echo "5. 点击 Deploy"
echo ""
echo "🚀 准备就绪！"
