#!/usr/bin/env python3
"""
🏋️ GymBro Platform - Simple Web Dashboard with API Proxy
========================================================

Simple HTTP server with API proxy to avoid CORS issues.
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import webbrowser
import os
import sys
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

# Service URLs
USER_MANAGEMENT_URL = 'http://localhost:8001'
ANALYTICS_URL = 'http://localhost:8003'

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler with API proxy functionality"""
    
    def do_GET(self):
        if self.path.startswith('/api/proxy/'):
            self.handle_api_proxy()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/proxy/'):
            self.handle_api_proxy()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def handle_api_proxy(self):
        """Proxy API calls to avoid CORS"""
        try:
            # Parse the proxy path
            # /api/proxy/user-management/health -> http://localhost:8001/health
            # /api/proxy/analytics/enhanced-dashboard -> http://localhost:8003/enhanced-dashboard
            
            parts = self.path.split('/')
            if len(parts) < 4:
                self.send_error(400, "Invalid proxy path")
                return
                
            service = parts[3]  # user-management or analytics
            endpoint = '/'.join(parts[4:])  # remaining path
            
            if service == 'user-management':
                target_url = f"{USER_MANAGEMENT_URL}/{endpoint}"
            elif service == 'analytics':
                target_url = f"{ANALYTICS_URL}/{endpoint}"
            else:
                self.send_error(400, f"Unknown service: {service}")
                return
            
            # Add query parameters
            if '?' in self.path:
                query = self.path.split('?', 1)[1]
                target_url += f"?{query}"
            
            print(f"[PROXY] {self.command} {self.path} -> {target_url}")
            
            # Prepare request
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else None
                
                req = urllib.request.Request(
                    target_url, 
                    data=post_data,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                req = urllib.request.Request(target_url)
            
            # Make request
            with urllib.request.urlopen(req, timeout=10) as response:
                # Send response
                self.send_response(response.status)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                data = response.read()
                self.wfile.write(data)
                
        except urllib.error.HTTPError as e:
            print(f"[PROXY ERROR] HTTP {e.code}: {e.reason}")
            self.send_response(e.code)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = json.dumps({
                "error": f"HTTP {e.code}",
                "message": str(e.reason)
            }).encode()
            self.wfile.write(error_response)
            
        except Exception as e:
            print(f"[PROXY ERROR] {e}")
            self.send_response(500)
            self.send_cors_headers()  
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = json.dumps({
                "error": "Proxy Error", 
                "message": str(e)
            }).encode()
            self.wfile.write(error_response)

def main():
    # Change to dashboard directory
    os.chdir(DIRECTORY)
    
    print("🏋️ GymBro Test Dashboard with API Proxy Starting...")
    print(f"📁 Serving from: {DIRECTORY}")
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print(f"🔧 API Proxy: /api/proxy/user-management/* -> {USER_MANAGEMENT_URL}/*")
    print(f"🔧 API Proxy: /api/proxy/analytics/* -> {ANALYTICS_URL}/*")
    print()
    print("🔥 Features:")
    print("   - Add test fitness data")
    print("   - View analytics results") 
    print("   - Generate mock data")
    print("   - Simple charts")
    print("   - No CORS issues!")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            # Try to open browser
            try:
                webbrowser.open(f'http://localhost:{PORT}')
            except Exception:
                pass
                
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print(f"💡 Try: lsof -ti:{PORT} | xargs kill")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
