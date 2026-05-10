import http.server
import socketserver
import os
import webbrowser

PORT = 8080
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Suppress GET requests in terminal for cleaner output
        pass

def run():
    print("=" * 60)
    print(" 🚀 JOHNS HOPKINS ANALYTICS WEB DASHBOARD LAUNCHING")
    print("=" * 60)
    print(f" Server running locally at:  http://localhost:{PORT}/dashboard/")
    print(" Press Ctrl+C to stop the dashboard server.")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        # Automatically open the browser
        webbrowser.open(f"http://localhost:{PORT}/dashboard/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Dashboard server stopped.")

if __name__ == '__main__':
    run()
