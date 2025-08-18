from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Inventory AI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }
        h1 { color: #333; text-align: center; }
        .status { text-align: center; color: #10b981; margin: 20px 0; }
        .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 30px 0; }
        .stat { background: #f9fafb; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #3b82f6; }
        .links { text-align: center; margin-top: 30px; }
        .link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Inventory AI</h1>
        <p class="status">✅ System Running on Vercel</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">2</div>
                <div>Orders Today</div>
            </div>
            <div class="stat">
                <div class="stat-value">4</div>
                <div>Total Bins</div>
            </div>
        </div>
        <div class="links">
            <a href="/health" class="link">Health Check</a>
            <a href="/api/status" class="link">API Status</a>
        </div>
    </div>
</body>
</html>
'''
            self.wfile.write(html.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "running", "platform": "vercel"}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
        return