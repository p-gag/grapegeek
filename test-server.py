#!/usr/bin/env python3
"""
Local test server to simulate GitHub Pages deployment structure.
Serves the family-trees React app at the /family-trees/ sub-path.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from pathlib import Path

class TestHandler(SimpleHTTPRequestHandler):
    """Handler that simulates GitHub Pages structure with sub-path routing."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from (built site folder)
        super().__init__(*args, directory='site', **kwargs)
    
    def do_GET(self):
        """Handle GET requests with sub-path routing."""
        # Parse the requested path
        path = unquote(self.path)
        
        print(f"🔍 Request: {path}")
        
        # Handle family-trees sub-path
        if path.startswith('/family-trees'):
            # Remove /family-trees prefix and handle routing
            subpath = path[len('/family-trees'):].lstrip('/')
            
            if not subpath or subpath == '/':
                # Root of family-trees - serve index.html
                self.path = '/family-trees/index.html'
                print(f"   → Serving: {self.path}")
            elif subpath.startswith('assets/'):
                # Static assets
                self.path = f'/family-trees/{subpath}'
                print(f"   → Serving asset: {self.path}")
            elif subpath == 'tree-data.json':
                # Tree data file
                self.path = '/family-trees/tree-data.json'
                print(f"   → Serving data: {self.path}")
            else:
                # SPA routing - serve index.html for any other path
                self.path = '/family-trees/index.html'
                print(f"   → SPA route, serving index: {self.path}")
        
        elif False:  # Disable custom landing page - serve MkDocs site instead
            # Root - show simple page with link to family trees
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head><title>Grape Geek - Local Test</title></head>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>🍇 Grape Geek - Local Test Server</h1>
                <p>This simulates the production GitHub Pages deployment.</p>
                <p><a href="/family-trees/" style="color: #007bff; font-size: 18px;">
                    → Go to Family Trees Viewer
                </a></p>
                <p style="color: #666; margin-top: 40px; font-size: 14px;">
                    The family tree viewer is deployed as an independent React app<br>
                    at the <code>/family-trees/</code> sub-path.
                </p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            return
        
        # Handle the request normally
        super().do_GET()
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging."""
        pass  # We're doing custom logging above

def main():
    """Start the test server."""
    port = 8000
    
    # Check if site directory exists
    site_path = Path('site')
    if not site_path.exists():
        print("❌ site/ directory not found")
        print("   Run: mkdocs build")
        sys.exit(1)
    
    # Check if family-trees build exists
    family_trees_path = site_path / 'family-trees'
    if not family_trees_path.exists():
        print("❌ site/family-trees/ directory not found")
        print("   Run: cd grape-tree-react && npm run build")
        sys.exit(1)
    
    print(f"🌐 Starting test server on http://localhost:{port}")
    print(f"📁 Serving from: {site_path.absolute()}")
    print("🍇 Family trees at: http://localhost:8000/family-trees/")
    print("\n💡 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        with HTTPServer(('', port), TestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")

if __name__ == '__main__':
    main()