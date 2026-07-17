"""
Community Builders Network - Sierra Leone
Main HTTP server — pure Python standard library (no web framework).

Serves:
  - Static HTML/CSS/JS from the repo root (STATIC_ROOT).
  - JSON API under /api/*.
  - Simple admin UI at /admin.

Run:
    cd backend
    python server.py
"""

import http.server
import json
import mimetypes
import os
import socketserver
import sys
import threading
import urllib.parse
from http import HTTPStatus

import config
import db
from utils import hash_password
from api import GET_ROUTES, POST_ROUTES

# ------------------------------------------------------------------
# Static file settings
# ------------------------------------------------------------------
STATIC_ROOT = os.path.realpath(config.STATIC_ROOT)

# Pretty URL rewrites: /about -> about.html, /projects -> projects.html
PRETTY_ROUTES = {
    "":                "index.html",
    "/":               "index.html",
    "/home":           "index.html",
    "/about":          "about.html",
    "/projects":       "projects.html",
    "/get-involved":   "get-involved.html",
    "/news":           "news.html",
    "/contact":        "contact.html",
    "/admin":          "admin.html",
    "/admin/":         "admin.html",
    "/admin/login":    "admin-login.html",
}

# Extra MIME types not always in stdlib
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")


# ------------------------------------------------------------------
# Handler
# ------------------------------------------------------------------
class CBNHandler(http.server.BaseHTTPRequestHandler):
    server_version = "CBN-SL/1.0"

    # `api_admin_login` may set this to a Set-Cookie header value
    _set_cookie = None

    # ---------- Logging ----------
    def log_message(self, fmt, *args):
        if config.DEBUG:
            sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    # ---------- Router: GET ----------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API?
        if path.startswith("/api/"):
            return self._dispatch_api(path, GET_ROUTES,
                                      dict(urllib.parse.parse_qsl(parsed.query)))

        # Pretty routes
        if path in PRETTY_ROUTES:
            return self._serve_file(PRETTY_ROUTES[path])

        # Fall back to static file
        return self._serve_file(path.lstrip("/"))

    # ---------- Router: POST ----------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return self._send_json(404, {"ok": False, "error": "Not found"})
        data = self._read_json_body()
        return self._dispatch_api(parsed.path, POST_ROUTES, data)

    # ---------- CORS pre-flight ----------
    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors_headers()
        self.end_headers()

    # ---------- API dispatch ----------
    def _dispatch_api(self, path, routes, data):
        fn = routes.get(path)
        if not fn:
            return self._send_json(404, {"ok": False, "error": "Endpoint not found"})
        try:
            status, payload = fn(self, data or {})
        except Exception as exc:  # pylint: disable=broad-except
            if config.DEBUG:
                import traceback; traceback.print_exc()
            return self._send_json(500, {"ok": False, "error": "Server error", "detail": str(exc)})
        return self._send_json(status, payload)

    # ---------- Static file server ----------
    def _serve_file(self, rel_path):
        # Default file for a directory-style URL
        if rel_path.endswith("/") or rel_path == "":
            rel_path = os.path.join(rel_path, "index.html")

        # If no file extension, try adding .html (pretty URLs)
        if "." not in os.path.basename(rel_path):
            candidate = rel_path + ".html"
            if os.path.isfile(os.path.join(STATIC_ROOT, candidate)):
                rel_path = candidate

        abs_path = os.path.realpath(os.path.join(STATIC_ROOT, rel_path))

        # Prevent path traversal outside STATIC_ROOT
        if not abs_path.startswith(STATIC_ROOT):
            return self._send_error(403, "Forbidden")

        if not os.path.isfile(abs_path):
            # Serve a friendly 404 page if we have one
            fallback = os.path.join(STATIC_ROOT, "404.html")
            if os.path.isfile(fallback):
                return self._serve_raw(fallback, 404)
            return self._send_error(404, "Not found")

        return self._serve_raw(abs_path, 200)

    def _serve_raw(self, abs_path, status):
        ctype, _ = mimetypes.guess_type(abs_path)
        if ctype is None:
            ctype = "application/octet-stream"
        try:
            with open(abs_path, "rb") as f:
                body = f.read()
        except OSError:
            return self._send_error(500, "Could not read file")

        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # Cache static assets (but not HTML)
        if abs_path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".woff2")):
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-cache")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    # ---------- Helpers ----------
    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        # Support both JSON and urlencoded form posts
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        try:
            if ctype == "application/x-www-form-urlencoded":
                return dict(urllib.parse.parse_qsl(raw.decode("utf-8")))
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _send_json(self, status, payload):
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if self._set_cookie:
            self.send_header("Set-Cookie", self._set_cookie)
            self._set_cookie = None
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, msg):
        body = f"<h1>{status} {msg}</h1>".encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        # Same-origin by default; enable for local dev.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")


# ------------------------------------------------------------------
# Threaded server so multiple browser tabs don't block each other
# ------------------------------------------------------------------
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


# ------------------------------------------------------------------
# Bootstrap
# ------------------------------------------------------------------
def bootstrap_admin_user():
    """Auto-create default admin on first run if none exists."""
    try:
        if db.table_is_empty("admin_users"):
            db.execute(
                "INSERT INTO admin_users (username, password_hash, full_name) VALUES (%s, %s, %s)",
                (
                    config.BOOTSTRAP_ADMIN_USERNAME,
                    hash_password(config.BOOTSTRAP_ADMIN_PASSWORD),
                    "Site Administrator",
                ),
            )
            print(f"[bootstrap] Created default admin user "
                  f"'{config.BOOTSTRAP_ADMIN_USERNAME}' — CHANGE THE PASSWORD.")
    except Exception as exc:
        print(f"[bootstrap] Could not create admin user: {exc}")


def main():
    print(f"Community Builders Network — starting server")
    print(f"  Static root : {STATIC_ROOT}")
    print(f"  Database    : {config.DB_CONFIG['host']}:{config.DB_CONFIG['port']}"
          f"/{config.DB_CONFIG['database']}")

    # Init DB pool + healthcheck
    try:
        db.init_pool()
        if not db.healthcheck():
            raise RuntimeError("MySQL healthcheck failed.")
    except Exception as exc:
        print(f"[fatal] Could not connect to MySQL: {exc}")
        print("        Check backend/config.py or DB_* environment variables,")
        print("        and make sure you ran database/schema.sql first.")
        sys.exit(1)

    bootstrap_admin_user()

    httpd = ThreadedHTTPServer((config.HOST, config.PORT), CBNHandler)
    print(f"  Listening   : http://{config.HOST}:{config.PORT}")
    print(f"  Admin panel : http://{config.HOST}:{config.PORT}/admin\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()
