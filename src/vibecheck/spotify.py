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
    r = requests.get(f"{API}/playlists/{playlist_id}", headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    # classic apps get the track list under "tracks"; post-2024 dev-mode apps get it
    # under "items" (and only with a user token), with each entry as "item" not "track"
    paging = _paging_object(data)
    if not isinstance(paging, dict) or "items" not in paging:
        raise SystemExit("Spotify hides playlist tracks from app-only credentials. Re-run with --login to authorize with your Spotify account.")

    tracks = []
    while True:
        for entry in paging["items"]:
            t = entry.get("track") or entry.get("item")
            if t and t.get("id") and t.get("name"):
                tracks.append({"id": t["id"], "name": t["name"], "artist": ", ".join(a["name"] for a in t.get("artists", []))})
        url = paging.get("next")
        if not url:
            break
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 403:
            print(f"(Spotify blocks paging beyond the first {len(tracks)} tracks for this app)")
            break
        r.raise_for_status()
        paging = _paging_object(r.json())
    return data["name"], tracks


def _paging_object(data):
    # a paging object is a dict whose "items" is the list of entries; it may be the
    # response itself or nested under "tracks" (classic) or "items" (new dev-mode apps)
    for key in ("tracks", "items"):
        nested = data.get(key)
        if isinstance(nested, dict) and isinstance(nested.get("items"), list):
            return nested
    return data
