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
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Inventory AI Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .status { color: #22c55e; font-weight: bold; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
                    .api-link { display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 4px; margin: 4px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏭 Inventory AI Dashboard</h1>
                        <p>Running on Vercel Serverless</p>
                    </div>
                    
                    <div class="card">
                        <h3>📊 System Status</h3>
                        <p class="status">✅ System Online</p>
                        <p><strong>Platform:</strong> Vercel Serverless</p>
                        <p><strong>Environment:</strong> Production</p>
                    </div>
                    
                    <div class="card">
                        <h3>🚀 Quick Actions</h3>
                        <a href="/api/bins" class="api-link">📦 View Bins</a>
                        <a href="/api/inventory" class="api-link">📋 Inventory</a>
                        <a href="/health" class="api-link">❤️ Health</a>
                    </div>
                    
                    <div class="card">
                        <h3>🔗 Available Endpoints</h3>
                        <ul>
                            <li>GET / - Main status</li>
                            <li>GET /health - Health check</li>
                            <li>GET /api/bins - List bins</li>
                            <li>GET /api/inventory - List inventory</li>
                            <li>GET /dashboard - This dashboard</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
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