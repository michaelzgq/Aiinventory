#!/bin/bash

echo "🚀 修复 Render 部署问题..."

# 1. 删除可能有问题的 Dockerfile
echo "📁 清理旧的 Dockerfile..."
rm -f docker/Dockerfile
rm -f docker/Dockerfile.simple

# 2. 确保使用超简化版本
echo "✅ 使用超简化 Dockerfile.render..."

# 3. 创建 .dockerignore 避免构建问题
echo "📝 创建 .dockerignore..."
cat > .dockerignore << 'EOF'
# 忽略不必要的文件
.git
.gitignore
README.md
*.md
.env
.env.local
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
EOF

# 4. 检查 requirements.txt 是否有问题包
echo "🔍 检查 requirements.txt..."
if grep -q "opencv\|paddle\|cv2" requirements.txt; then
    echo "⚠️  发现可能有问题的包，创建简化版本..."
    cat > requirements-render.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiofiles==23.2.1
EOF
    echo "✅ 创建了 requirements-render.txt"
else
    echo "✅ requirements.txt 看起来没问题"
fi

# 5. 更新 render.yaml 使用简化依赖
if [ -f "requirements-render.txt" ]; then
    echo "📝 更新 render.yaml 使用简化依赖..."
    sed -i '' 's/requirements.txt/requirements-render.txt/g' render.yaml
fi

echo "🎉 修复完成！"
echo ""
echo "📋 下一步操作："
echo "1. git add ."
echo "2. git commit -m '彻底修复 Render 部署问题'"
echo "3. git push origin main"
echo "4. 在 Render 中重新部署"
echo ""
echo "🔧 如果还有问题，请检查："
echo "- Render 构建日志"
echo "- 确认使用了 Dockerfile.render"
echo "- 环境变量配置"
