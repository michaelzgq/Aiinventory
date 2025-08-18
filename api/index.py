# Vercel Serverless Function - Ultra Simple
def handler(request):
    """Main handler for Vercel"""
    
    # Get path from request
    path = request.url if hasattr(request, 'url') else '/'
    if '?' in path:
        path = path.split('?')[0]
    
    # Home page
    if path == '/' or path == '':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f3f4f6;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #1f2937;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .card-value {
            font-size: 3em;
            font-weight: bold;
            color: #3b82f6;
            margin-bottom: 10px;
        }
        .card-label {
            color: #6b7280;
        }
        .actions {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .btn {
            display: inline-block;
            margin: 10px;
            padding: 12px 24px;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #2563eb;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📦 Inventory AI</h1>
            <p style="color: #6b7280; margin: 15px 0;">智能库存管理系统</p>
            <span class="status">运行正常</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-value">2</div>
                <div class="card-label">今日订单</div>
            </div>
            <div class="card">
                <div class="card-value">0</div>
                <div class="card-label">快照记录</div>
            </div>
            <div class="card">
                <div class="card-value">0</div>
                <div class="card-label">异常项目</div>
            </div>
            <div class="card">
                <div class="card-value">4</div>
                <div class="card-label">货位总数</div>
            </div>
        </div>
        
        <div class="actions">
            <h2 style="margin-bottom: 20px;">快速访问</h2>
            <a href="/health" class="btn">健康检查</a>
            <a href="/api/status" class="btn">API 状态</a>
            <a href="/api/bins" class="btn">货位列表</a>
            <p style="margin-top: 30px; color: #6b7280;">
                平台：Vercel | 版本：2.0.0 | 
                <a href="https://github.com/michaelzgq/Aiinventory" style="color: #3b82f6;">GitHub</a>
            </p>
        </div>
    </div>
</body>
</html>'''
        }
    
    # API endpoints
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    
    if path == '/health':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': '{"status": "healthy", "platform": "vercel"}'
        }
    
    elif path == '/api/status':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': '{"message": "Inventory AI - Running on Vercel", "status": "ok"}'
        }
    
    elif path == '/api/bins':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': '{"bins": [{"id": "A51"}, {"id": "A52"}, {"id": "A53"}, {"id": "A54"}], "total": 4}'
        }
    
    # 404 for other paths
    return {
        'statusCode': 404,
        'headers': headers,
        'body': '{"error": "Not Found"}'
    }