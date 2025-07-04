# project_chimera/internal_flag_server.py

from http.server import BaseHTTPRequestHandler, HTTPServer

# This is a simple, non-Flask server designed to run on an internal port.
# Its only purpose is to serve the final flag when accessed.

HOST = 'localhost'
PORT = 8080 # A common internal port

class FlagServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # This is the final flag, the "Ascension Override" code.
        final_flag = "flag{ASCENSION_OVERRIDE_CODE_737351}"
        self.wfile.write(final_flag.encode('utf-8'))

def run_flag_server():
    try:
        server = HTTPServer((HOST, PORT), FlagServerHandler)
        print(f"Internal flag server running on http://{HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Could not start internal flag server: {e}")

if __name__ == '__main__':
    run_flag_server()
