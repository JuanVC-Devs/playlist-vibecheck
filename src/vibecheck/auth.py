import base64
import hashlib
import http.server
import json
import os
import pathlib
import secrets
import time
import urllib.parse
import webbrowser

import requests

REDIRECT_URI = "http://127.0.0.1:8888/callback"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CACHE_FILE = pathlib.Path.home() / ".vibecheck-token.json"
CONFIG_FILE = pathlib.Path.home() / ".vibecheck-config.json"


def _client_id():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    if not client_id and CONFIG_FILE.exists():
        client_id = json.loads(CONFIG_FILE.read_text()).get("client_id")
    if not client_id:
        raise SystemExit(f"Set SPOTIFY_CLIENT_ID, or save it once in {CONFIG_FILE} as {{\"client_id\": \"...\"}} (see README).")
    return client_id


def _save(tokens):
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600) - 60
    CACHE_FILE.write_text(json.dumps(tokens))


def _refresh(client_id, refresh_token):
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": client_id},
        timeout=15,
    )
    if r.status_code != 200:
        return None
    tokens = r.json()
    tokens.setdefault("refresh_token", refresh_token)
    _save(tokens)
    return tokens["access_token"]


def user_token():
    client_id = _client_id()
    if CACHE_FILE.exists():
        cached = json.loads(CACHE_FILE.read_text())
        if cached.get("expires_at", 0) > time.time():
            return cached["access_token"]
        if cached.get("refresh_token"):
            fresh = _refresh(client_id, cached["refresh_token"])
            if fresh:
                return fresh

    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result["code"] = query.get("code", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>vibecheck: login OK &mdash; you can close this tab.</h2>")

        def log_message(self, *args):
            pass

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "scope": "playlist-read-private playlist-read-collaborative",
    }
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    server = http.server.HTTPServer(("127.0.0.1", 8888), Handler)
    print("Opening your browser for Spotify login (waiting for you to approve)...")
    webbrowser.open(url)
    server.handle_request()
    server.server_close()

    if not result.get("code"):
        raise SystemExit("Spotify login failed or was cancelled.")
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": result["code"],
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "code_verifier": verifier,
        },
        timeout=15,
    )
    r.raise_for_status()
    tokens = r.json()
    _save(tokens)
    return tokens["access_token"]
