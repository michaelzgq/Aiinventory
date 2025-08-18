# Hybrid Vercel Handler - 混合版本
# 提供基础功能的同时保持美观界面

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # 主页 - 返回美观的 HTML 界面
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 使用本地项目的界面样式
            html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory AI - 智能库存管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #333;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card .icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        .stat-card .value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-card .label {
            color: #666;
            font-size: 1rem;
        }
        .stat-card.orders { border-top: 4px solid #3b82f6; }
        .stat-card.orders .icon { color: #3b82f6; }
        .stat-card.snapshots { border-top: 4px solid #14b8a6; }
        .stat-card.snapshots .icon { color: #14b8a6; }
        .stat-card.anomalies { border-top: 4px solid #f59e0b; }
        .stat-card.anomalies .icon { color: #f59e0b; }
        .stat-card.bins { border-top: 4px solid #10b981; }
        .stat-card.bins .icon { color: #10b981; }
        .action-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .action-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .action-btn {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: all 0.3s;
        }
        .action-btn:hover {
            transform: scale(1.05);
            color: white;
        }
        .action-btn.scan { background: linear-gradient(45deg, #3b82f6, #2563eb); }
        .action-btn.upload { background: linear-gradient(45deg, #14b8a6, #0d9488); }
        .action-btn.reconcile { background: linear-gradient(45deg, #f59e0b, #d97706); }
        .action-btn.report { background: linear-gradient(45deg, #10b981, #059669); }
        .info-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .api-endpoints {
            background: #f3f4f6;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .api-endpoints h4 {
            color: #333;
            margin-bottom: 15px;
        }
        .endpoint {
            background: white;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            font-family: monospace;
            border-left: 3px solid #3b82f6;
        }
        .status-badge {
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1><i class="fas fa-boxes"></i> Inventory AI</h1>
            <p class="subtitle">智能库存管理系统 <span class="status-badge">运行中</span></p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card orders">
                <div class="icon"><i class="fas fa-shopping-cart"></i></div>
                <div class="value">2</div>
                <div class="label">今日订单</div>
            </div>
            <div class="stat-card snapshots">
                <div class="icon"><i class="fas fa-camera"></i></div>
                <div class="value">0</div>
                <div class="label">快照记录</div>
            </div>
            <div class="stat-card anomalies">
                <div class="icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="value">0</div>
                <div class="label">异常项目</div>
            </div>
            <div class="stat-card bins">
                <div class="icon"><i class="fas fa-qrcode"></i></div>
                <div class="value">0</div>
                <div class="label">扫描货位</div>
            </div>
        </div>
        
        <div class="action-section">
            <h3><i class="fas fa-rocket"></i> 快速操作</h3>
            <div class="action-grid">
                <a href="/scan" class="action-btn scan">
                    <i class="fas fa-camera"></i> 开始扫描
                </a>
                <a href="/upload-orders" class="action-btn upload">
                    <i class="fas fa-upload"></i> 上传订单
                </a>
                <a href="/reconcile" class="action-btn reconcile">
                    <i class="fas fa-sync"></i> 每日对账
                </a>
                <a href="/api/reports/download" class="action-btn report">
                    <i class="fas fa-download"></i> 下载报告
                </a>
            </div>
        </div>
        
        <div class="info-section">
            <h3><i class="fas fa-info-circle"></i> 系统信息</h3>
            <p><strong>平台：</strong>Vercel Serverless</p>
            <p><strong>版本：</strong>2.0.0</p>
            <p><strong>环境：</strong>生产环境</p>
            
            <div class="api-endpoints">
                <h4><i class="fas fa-code"></i> API 端点</h4>
                <div class="endpoint">GET /health - 健康检查</div>
                <div class="endpoint">GET /api/status - 系统状态</div>
                <div class="endpoint">GET /api/bins - 货位列表</div>
                <div class="endpoint">GET /api/inventory - 库存查询</div>
                <div class="endpoint">POST /api/nlq/query - 自然语言查询</div>
            </div>
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode())
            return
            
        # API 路由处理
        # 设置默认响应头
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # API 端点
        if path == '/health':
            response = {
                "status": "healthy",
                "platform": "vercel",
                "timestamp": datetime.now().isoformat()
            }
        elif path == '/api/status':
            response = {
                "message": "🏭 Inventory AI - Vercel Hybrid",
                "status": "running",
                "version": "2.0.0",
                "features": ["Dashboard", "Basic API", "Health Check"]
            }
        elif path == '/api/bins':
            response = {
                "bins": [
                    {"id": "A51", "zone": "Zone-A", "items": 0},
                    {"id": "A52", "zone": "Zone-A", "items": 0},
                    {"id": "A53", "zone": "Zone-A", "items": 0},
                    {"id": "A54", "zone": "Zone-A", "items": 0}
                ],
                "total": 4
            }
        elif path == '/api/inventory':
            response = {
                "items": [],
                "total": 0,
                "message": "库存数据需要连接数据库"
            }
        else:
            self.send_response(404)
            response = {"error": "Not Found", "path": path}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode())
    
    def do_POST(self):
        # 处理 POST 请求
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "POST endpoints require database connection",
            "status": "limited"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
