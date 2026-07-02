import json
import re

import requests


def parse_playlist_id(url_or_id):
    m = re.search(r"playlist[/:]([A-Za-z0-9]+)", url_or_id)
    return m.group(1) if m else url_or_id


def get_playlist(playlist_id):
    # Spotify's public embed page ships the playlist and its first ~100 tracks
    # as JSON inside __NEXT_DATA__ — no credentials required.
    r = requests.get(
        f"https://open.spotify.com/embed/playlist/{playlist_id}",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15,
    )
    r.raise_for_status()

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', r.text, re.DOTALL)
    if not m:
        raise SystemExit(f"Could not read the Spotify page for playlist {playlist_id}.")
    data = json.loads(m.group(1))

    try:
        entity = data["props"]["pageProps"]["state"]["data"]["entity"]
    except (KeyError, TypeError):
        raise SystemExit(
            f"Spotify does not expose playlist {playlist_id} publicly. "
            "Make sure the playlist is public (and added to your profile) and try again."
        )

    name = entity.get("name") or entity.get("title") or "Playlist"
    tracks = []
    for item in entity.get("trackList", []):
        uri = item.get("uri", "")
        if uri.startswith("spotify:track:"):
            tracks.append({
                "id": uri.rsplit(":", 1)[-1],
                "name": item.get("title", "?"),
                "artist": (item.get("subtitle") or "").replace("\xa0", " "),
            })

    if not tracks:
        raise SystemExit(f"No tracks found in playlist {playlist_id}.")
    return name, tracks
