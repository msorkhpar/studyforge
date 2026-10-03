"""A stand-in API host: answers every request with who it is. Port 443, plain HTTP."""

import http.server
import os


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # A stand-in for an API that refuses an unknown key: it NEVER repeats what it was sent, and
        # it logs only whether a key header arrived and how long it was.
        sent = self.headers.get("x-api-key")
        print("x-api-key present:", sent is not None, "length:", len(sent or ""), flush=True)
        if sent is not None:
            body = b'{"type":"error","error":{"message":"invalid x-api-key"}}'
            self.send_response(401)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = os.environ.get("WHO", "STANDIN").encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


http.server.ThreadingHTTPServer(("0.0.0.0", 443), Handler).serve_forever()
