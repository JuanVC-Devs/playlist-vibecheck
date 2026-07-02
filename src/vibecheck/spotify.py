import base64
import os
import re

import requests

API = "https://api.spotify.com/v1"


def parse_playlist_id(url_or_id):
    m = re.search(r"playlist[/:]([A-Za-z0-9]+)", url_or_id)
    return m.group(1) if m else url_or_id


def get_token():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not secret:
        raise SystemExit("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET (see README).")
    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {auth}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def get_playlist(playlist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/playlists/{playlist_id}", params={"fields": "name"}, headers=headers, timeout=15)
    r.raise_for_status()
    name = r.json()["name"]

    tracks = []
    url = f"{API}/playlists/{playlist_id}/tracks"
    params = {"fields": "items(track(id,name,artists(name))),next", "limit": 100}
    while url:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        for item in data["items"]:
            t = item.get("track")
            if t and t.get("id"):
                tracks.append({"id": t["id"], "name": t["name"], "artist": ", ".join(a["name"] for a in t["artists"])})
        url = data.get("next")
        params = None
    return name, tracks
