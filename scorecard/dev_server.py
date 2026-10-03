#!/usr/bin/env python3
"""
Local stand-in for Vercel: serves web/ and routes /api/* to the same logic the
deployed functions use. For testing only. Run: python3 dev_server.py [port]
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
sys.path.insert(0, os.path.join(ROOT, "api"))
import _logic  # noqa: E402

TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json"}


class Dev(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/config":
            return _logic.send_json(self, 200, _logic.get_config())
        if path.startswith("/api/"):
            return _logic.send_json(self, 405, {"ok": False, "error": "POST only."})
        rel = "index.html" if path == "/" else path.lstrip("/")
        if "." not in os.path.basename(rel):
            rel += ".html"                      # cleanUrls
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT + os.sep) or "/api/" in full or not os.path.isfile(full):
            self.send_response(404); self.end_headers(); return
        data = open(full, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(os.path.splitext(full)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def do_POST(self):
        path = self.path.split("?")[0]
        fn = {"/api/audit": _logic.run_audit, "/api/lead": _logic.submit_lead}.get(path)
        if not fn:
            return _logic.send_json(self, 404, {"ok": False, "error": "Not found."})
        _logic.handle_post(self, fn)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"serving {ROOT} on http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Dev).serve_forever()
