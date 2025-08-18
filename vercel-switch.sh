#!/bin/bash

echo "🔄 Vercel 版本切换工具"
echo ""
echo "选择要使用的版本："
echo "1) 简化版 API（当前）"
echo "2) 完整版应用（推荐）"
echo ""
read -p "请选择 (1/2): " choice

case $choice in
    1)
        echo "切换到简化版..."
        cat > vercel.json << 'EOF'
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
EOF
        echo "✅ 已切换到简化版 API"
        echo "📝 使用文件: api/index.py"
        ;;
    2)
        echo "切换到完整版..."
        cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/backend/app/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/main.py"
    }
  ],
  "env": {
    "PYTHONPATH": "/var/task:/var/task/backend"
  }
}
EOF
        echo "✅ 已切换到完整版应用"
        echo "📝 使用文件: backend/app/main.py (通过 api/main.py 适配)"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "下一步："
echo "1. git add vercel.json"
echo "2. git commit -m '切换 Vercel 版本'"
echo "3. git push"
echo ""
echo "Vercel 会自动重新部署 🚀"
