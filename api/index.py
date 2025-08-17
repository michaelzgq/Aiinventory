from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route handling
        if path == '/':
            response = {
                "message": "🏭 Inventory AI - Running on Vercel",
                "status": "running",
                "platform": "vercel",
                "version": "2.0.0",
                "features": ["REST API", "Health Check", "Basic Inventory", "Dashboard"]
            }
        elif path == '/health':
            response = {
                "status": "healthy",
                "platform": "vercel", 
                "database": "in-memory",
                "timestamp": "2024-01-01"
            }
        elif path == '/api/bins':
            bins = [
                {"id": "A01", "location": "Aisle A, Level 1", "capacity": 100},
                {"id": "A02", "location": "Aisle A, Level 2", "capacity": 100},
                {"id": "B01", "location": "Aisle B, Level 1", "capacity": 150},
                {"id": "S-01", "location": "Staging Area 1", "capacity": 200}
            ]
            response = {"bins": bins, "count": len(bins)}
        elif path == '/api/inventory':
            response = {"items": [], "count": 0, "message": "No items in inventory"}
        elif path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory AI Dashboard</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .header h1 { 
            color: #333; 
            margin: 0 0 10px 0; 
            font-size: 2.5em;
            font-weight: 700;
        }
        .header p { 
            color: #666; 
            margin: 0;
            font-size: 1.2em;
        }
        .cards { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 25px; 
        }
        .card { 
            border: none;
            padding: 25px; 
            margin: 0;
            border-radius: 15px; 
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .card h3 { 
            margin-top: 0; 
            color: #333; 
            font-size: 1.3em;
            margin-bottom: 15px;
        }
        .status { 
            color: #28a745; 
            font-weight: bold; 
            font-size: 1.1em;
        }
        .api-link { 
            display: inline-block; 
            padding: 12px 20px; 
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white; 
            text-decoration: none; 
            border-radius: 8px; 
            margin: 8px; 
            font-weight: 500;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,123,255,0.3);
        }
        .api-link:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,123,255,0.4);
        }
        .endpoint-list {
            list-style: none;
            padding: 0;
        }
        .endpoint-list li {
            background: #e9ecef;
            margin: 8px 0;
            padding: 12px;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
            border-left: 3px solid #6c757d;
        }
        .badge {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Inventory AI Dashboard</h1>
            <p>Advanced Inventory Management System <span class="badge">LIVE</span></p>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>📊 System Status</h3>
                <p class="status">✅ System Online</p>
                <p><strong>Platform:</strong> Vercel Serverless</p>
                <p><strong>Environment:</strong> Production</p>
                <p><strong>Runtime:</strong> Python 3.12</p>
            </div>
            
            <div class="card">
                <h3>🚀 Quick Actions</h3>
                <a href="/api/bins" class="api-link">📦 View Bins</a>
                <a href="/api/inventory" class="api-link">📋 Inventory</a>
                <a href="/health" class="api-link">❤️ Health Check</a>
            </div>
            
            <div class="card">
                <h3>🔗 API Endpoints</h3>
                <ul class="endpoint-list">
                    <li>GET / - System status</li>
                    <li>GET /health - Health check</li>
                    <li>GET /api/bins - List all bins</li>
                    <li>GET /api/inventory - View inventory</li>
                    <li>GET /dashboard - This dashboard</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>📈 Features</h3>
                <ul>
                    <li>✅ REST API</li>
                    <li>✅ Bin Management</li>
                    <li>✅ Inventory Tracking</li>
                    <li>✅ Real-time Status</li>
                    <li>✅ Cross-Origin Support</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode())
            return
        else:
            response = {"error": "Not Found", "path": path, "message": "Endpoint not available"}
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        
        # Send JSON response
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()