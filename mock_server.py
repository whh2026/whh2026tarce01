#!/usr/bin/env python3
"""
Mock HTTP Server for Testing
"""
import json
import socketserver
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockRequestHandler(BaseHTTPRequestHandler):
    """Mock HTTP Request Handler"""
    
    def log_request(self, code='-', size='-'):
        """Log request details to a file"""
        # Get current timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepare log entry
        log_entry = f"{timestamp} | {self.command} {self.path} | Status: {code}\n"
        
        # Write to log file
        with open('server.log', 'a') as f:
            f.write(log_entry)
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "Mock GET request handled",
            "path": self.path
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse JSON data with error handling
        try:
            received_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "status": "error",
                "message": "Invalid JSON data received",
                "error": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return
        
        # Import time module
        import time
        
        # Log POST request data
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} | {self.command} {self.path} | Data: {json.dumps(received_data)}\n"
        with open('server.log', 'a') as f:
            f.write(log_entry)
        
        # Check if any parameter value is less than or equal to 5
        value_less_or_equal_5 = False
        if isinstance(received_data, dict):
            for key, value in received_data.items():
                if isinstance(value, (int, float)) and value <= 5:
                    value_less_or_equal_5 = True
                    break
        
        if value_less_or_equal_5:
            print(f"Found parameter value <= 5, waiting 10 seconds...")
            time.sleep(10)
        else:
            print(f"All parameter values are > 5, responding immediately...")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "Mock POST request handled",
            "received_data": received_data
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_PUT(self):
        """Handle PUT requests"""
        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "Mock PUT request handled",
            "received_data": json.loads(put_data.decode('utf-8'))
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "Mock DELETE request handled",
            "path": self.path
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_mock_server(host='localhost', port=8000):
    """Run the mock HTTP server with concurrency support"""
    # Use ThreadingMixIn to allow concurrent requests
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        pass
    
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, MockRequestHandler)
    print(f"Mock server running on http://{host}:{port} with concurrency support")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nMock server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    run_mock_server()