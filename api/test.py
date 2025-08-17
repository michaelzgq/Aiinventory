from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Test</title>
    <style>
        body { background: red; color: white; padding: 50px; font-size: 30px; }
    </style>
</head>
<body>
    <h1>HTML TEST PAGE</h1>
    <p>If you see this with red background, HTML works!</p>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))