#!/usr/bin/env python3
"""
🏋️ GymBro Platform - Simple Web Dashboard Server
===============================================

Super simple HTTP server to serve the test dashboard.
Just serves static HTML - no Flask overhead needed.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Simple handler with CORS headers for API calls"""
    
    def end_headers(self):
        # Add CORS headers for all requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
        self.send_header('Access-Control-Max-Age', '86400')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()
        
    def log_message(self, format, *args):
        """Override to add timestamp and better formatting"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def main():
    # Change to dashboard directory
    os.chdir(DIRECTORY)
    
    print("🏋️ GymBro Test Dashboard Starting...")
    print(f"📁 Serving from: {DIRECTORY}")
    print(f"🌐 URL: http://localhost:{PORT}")
    print("🔥 Features:")
    print("   - Add test fitness data")
    print("   - View analytics results") 
    print("   - Generate mock data")
    print("   - Simple charts")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            # Try to open browser
            try:
                webbrowser.open(f'http://localhost:{PORT}')
            except:
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
