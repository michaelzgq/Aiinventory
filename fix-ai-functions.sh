#!/bin/bash

echo "🤖 修复 AI 功能问题..."

# 1. 检查 API Key 配置
echo "🔑 检查 API Key 配置..."
if grep -q "changeme-supersecret" backend/app/static/js/nlq.js; then
    echo "⚠️  发现硬编码的 API Key，需要修复"
else
    echo "✅ API Key 配置正确"
fi

# 2. 检查数据库连接
echo "🗄️  检查数据库配置..."
if grep -q "sqlite" backend/app/config.py; then
    echo "⚠️  使用 SQLite，Render 应该使用 PostgreSQL"
else
    echo "✅ 数据库配置正确"
fi

# 3. 检查前端 API 调用
echo "🌐 检查前端 API 调用..."
if grep -q "/api/nlq/query" backend/app/static/js/nlq.js; then
    echo "✅ NLQ API 端点配置正确"
else
    echo "❌ NLQ API 端点缺失"
fi

# 4. 检查环境变量
echo "⚙️  检查环境变量配置..."
if grep -q "API_KEY" backend/app/config.py; then
    echo "✅ API_KEY 环境变量已配置"
else
    echo "❌ API_KEY 环境变量缺失"
fi

echo ""
echo "📋 需要修复的问题："
echo "1. API Key 认证问题"
echo "2. 数据库连接问题"
echo "3. 前端数据加载问题"
echo ""
echo "🔧 修复步骤："
echo "1. 更新 API Key 获取方式"
echo "2. 确保数据库连接正常"
echo "3. 修复前端数据加载"
echo ""
echo "💡 这些问题在 Render 部署后应该能解决！"
