#!/bin/bash

echo "🔧 修复 psycopg2 问题..."

# 1. 确保 requirements-render.txt 存在
echo "📝 检查 requirements-render.txt..."
if [ ! -f "requirements-render.txt" ]; then
    echo "❌ requirements-render.txt 不存在"
    exit 1
fi

# 2. 检查是否包含 psycopg2-binary
if grep -q "psycopg2" requirements-render.txt; then
    echo "✅ psycopg2-binary 已包含"
else
    echo "❌ psycopg2-binary 缺失"
    exit 1
fi

# 3. 检查 render.yaml 配置
echo "🔍 检查 render.yaml..."
if grep -q "requirements-render.txt" render.yaml; then
    echo "✅ render.yaml 配置正确"
else
    echo "❌ render.yaml 配置错误"
    exit 1
fi

# 4. 检查 Dockerfile.render
echo "🐳 检查 Dockerfile.render..."
if grep -q "requirements-render.txt" docker/Dockerfile.render; then
    echo "✅ Dockerfile.render 配置正确"
else
    echo "❌ Dockerfile.render 配置错误"
    exit 1
fi

echo "🎉 所有配置检查通过！"
echo ""
echo "📋 下一步操作："
echo "1. git add ."
echo "2. git commit -m '修复 psycopg2 依赖问题'"
echo "3. git push origin main"
echo "4. 在 Render 中重新部署"
echo ""
echo "💡 这次应该能成功启动应用了！"
