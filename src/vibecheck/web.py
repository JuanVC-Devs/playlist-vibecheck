import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from . import analysis, reccobeats, spotify, themes

PORT = 8899


def analyze(playlist, threshold=0.20):
    name, tracks = spotify.get_playlist(spotify.parse_playlist_id(playlist))
    features = reccobeats.get_audio_features([t["id"] for t in tracks])
    analyzed = [{**t, "f": features[t["id"]]} for t in tracks if t["id"] in features]
    if not analyzed:
        raise ValueError("No tracks could be analyzed for this playlist.")

    center = analysis.centroid([t["f"] for t in analyzed])
    for i, t in enumerate(analyzed):
        t["pos"] = i
    out = []
    for t in sorted(analyzed, key=lambda t: analysis.vibe_distance(t["f"], center)):
        f = t["f"]
        dist = analysis.vibe_distance(f, center)
        match = dist <= threshold
        out.append({
            "pos": t["pos"],
            "name": t["name"],
            "artist": t["artist"],
            "key": analysis.key_name(f["key"], f["mode"]),
            "camelot": analysis.camelot(f["key"], f["mode"]),
            "energy": f["energy"],
            "valence": f["valence"],
            "danceability": f["danceability"],
            "tempo": round(f["tempo"]) if f.get("tempo") else None,
            "style": themes.classify_style(f),
            "party": round(analysis.party_score(f), 3),
            "dist": round(dist, 3),
            "match": match,
            "reason": None if match else analysis.deviation_reason(f, center),
        })
    matches = sum(t["match"] for t in out)
    features_list = [t["f"] for t in analyzed]
    return {
        "themes": themes.theme_scores(features_list),
        "styles": themes.style_distribution(features_list),
        "spread": analysis.spread(features_list),
        "playlist": name,
        "total": len(tracks),
        "analyzed": len(analyzed),
        "vibe": analysis.vibe_label(center),
        "center": {k: round(v, 3) for k, v in center.items()},
        "match_pct": round(100 * matches / len(analyzed)),
        "matches": matches,
        "dominant_camelot": analysis.dominant_camelot([t["f"] for t in analyzed]),
        "party": round(sum(analysis.party_score(t["f"]) for t in analyzed) / len(analyzed), 3),
        "threshold": threshold,
        "tracks": out,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = resources.files("vibecheck").joinpath("index.html").read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path == "/api/demo":
            body = resources.files("vibecheck").joinpath("demo.json").read_bytes()
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"not found")

    def do_POST(self):
        if self.path != "/api/analyze":
            return self._send(404, "text/plain", b"not found")
        length = int(self.headers.get("Content-Length", 0))
        try:
            req = json.loads(self.rfile.read(length) or b"{}")
            result = analyze(req["playlist"], float(req.get("threshold", 0.20)))
            self._send(200, "application/json", json.dumps(result).encode())
        except SystemExit as e:
            self._send(400, "application/json", json.dumps({"error": str(e)}).encode())
        except Exception as e:
            self._send(500, "application/json", json.dumps({"error": f"{type(e).__name__}: {e}"}).encode())

    def _send(self, status, ctype, body):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"vibecheck web UI running on {url}  (Ctrl+C to stop)")
    threading.Timer(0.5, webbrowser.open, args=[url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
