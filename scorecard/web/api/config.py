import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _logic  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        _logic.send_json(self, 200, _logic.get_config())

    def log_message(self, *args):
        pass
