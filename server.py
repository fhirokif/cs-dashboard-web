import http.server
import json
import os
from urllib.request import urlopen, Request
from urllib.parse import urlencode, parse_qs, urlparse

GAS_API = "https://script.google.com/macros/s/AKfycbxiF1BFK1O8F4g8_BNZGxucobt6WJv03HO00Vs9WbZug8kIwS-3qT48VXp9LLlJqe7fFg/exec"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api":
            self._proxy_gas(parsed.query)
            return
        super().do_GET()

    def _proxy_gas(self, query_string):
        params = parse_qs(query_string)
        qs = urlencode({k: v[0] for k, v in params.items()})
        gas_url = GAS_API + "?" + qs if qs else GAS_API
        try:
            req = Request(gas_url, headers={"User-Agent": "CS-Dashboard-Proxy/1.0"})
            with urlopen(req, timeout=30) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


port = int(os.environ.get("PORT", 8080))
server = http.server.HTTPServer(("0.0.0.0", port), Handler)
print(f"Serving on port {port}")
server.serve_forever()
