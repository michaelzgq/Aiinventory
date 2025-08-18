# 🚨 Vercel 部署终极修复方案

## 🔍 当前情况

持续出现 500 错误，即使使用了标准格式。

## 💡 极简化方案

### 1. 清理所有文件
已删除：
- ❌ api/handler.py
- ❌ api/main.py
- ❌ api/simple.py
- ❌ api/app.py

只保留：
- ✅ api/index.py
- ✅ api/requirements.txt (空文件)
- ✅ api/test.py (测试用)

### 2. 使用最标准的格式
```python
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 处理请求
```

### 3. 更新 .vercelignore
```
# 忽略所有文件
*
# 只允许 api 文件夹
!api/
!api/index.py
!api/requirements.txt
!vercel.json
```

## 🧪 调试步骤

如果还是失败，请尝试：

### 1. 访问测试端点
```
https://aiinventory.vercel.app/api/test
```

### 2. 查看 Vercel 日志
1. 登录 Vercel Dashboard
2. 选择项目
3. 点击 "Functions" 标签
4. 查看错误日志

### 3. 创建新项目测试
```bash
# 创建最小测试
mkdir vercel-test
cd vercel-test
echo 'from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello World")
        return' > api/index.py

# 部署测试
vercel
```

## 🎯 备选方案

### 使用 Netlify Functions
```bash
# netlify.toml
[build]
  functions = "functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### 使用 Render
- 完整功能支持
- 更稳定的环境
- 支持数据库

## 📝 关键检查点

1. **Python 版本兼容性**
2. **没有外部依赖**
3. **正确的函数签名**
4. **文件编码 UTF-8**

## 🆘 如果还是不行

可能需要：
1. 联系 Vercel 支持
2. 检查账户限制
3. 尝试不同区域部署
4. 使用其他平台
