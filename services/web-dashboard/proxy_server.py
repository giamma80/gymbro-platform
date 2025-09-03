#!/usr/bin/env python3
"""
Proxy server per la dashboard web GymBro
Serve i file statici e gestisce le richieste API per evitare problemi CORS
"""
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
from urllib.error import HTTPError

class GymBroProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            # Serve file statici
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "Not found")
    
    def handle_api_request(self):
        try:
            print(f"DEBUG: Original path: {self.path}")
            # Rimuovi /api/proxy/ dal path
            api_path = self.path.replace('/api/proxy/', '/')
            print(f"DEBUG: API path after removing /api/proxy/: {api_path}")
            
            # Determina il servizio target
            if api_path.startswith('/user-management/'):
                target_url = f"http://localhost:8001{api_path.replace('/user-management', '', 1)}"
                print(f"DEBUG: User Management target URL: {target_url}")
            elif api_path.startswith('/analytics/'):
                target_url = f"http://localhost:8003{api_path.replace('/analytics', '', 1)}"
                print(f"DEBUG: Analytics target URL: {target_url}")
            else:
                print(f"DEBUG: Service not found for path: {api_path}")
                self.send_error(404, "Service not found")
                return
            
            # Leggi il corpo della richiesta per POST
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # Crea la richiesta
            req = urllib.request.Request(target_url, data=post_data, method=self.command)
            
            # Copia headers importanti
            if 'Content-Type' in self.headers:
                req.add_header('Content-Type', self.headers['Content-Type'])
            if 'Authorization' in self.headers:
                req.add_header('Authorization', self.headers['Authorization'])
            
            # Esegui la richiesta
            with urllib.request.urlopen(req) as response:
                # Invia headers di risposta
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['server', 'date', 'content-encoding']:
                        self.send_header(header, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                
                # Invia il corpo della risposta
                self.wfile.write(response.read())
        
        except HTTPError as e:
            self.send_response(e.code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"detail": e.reason}).encode()
            self.wfile.write(error_response)
        
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(500, f"Proxy error: {str(e)}")
    
    def do_OPTIONS(self):
        # Gestisce preflight CORS requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

def main():
    PORT = 3000
    os.chdir('/Users/giamma/workspace/gymbro-platform/services/web-dashboard')
    
    with socketserver.TCPServer(("", PORT), GymBroProxyHandler) as httpd:
        print(f"🚀 GymBro Dashboard proxy server running on http://localhost:{PORT}")
        print(f"📁 Serving files from: {os.getcwd()}")
        print(f"🔗 API proxy: /api/proxy/user-management/* -> http://localhost:8001/*")
        print(f"🔗 API proxy: /api/proxy/analytics/* -> http://localhost:8003/*")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
