import requests

API = "https://api.reccobeats.com/v1/audio-features"
BATCH = 40


def spotify_id_from_href(href):
    return href.rstrip("/").rsplit("/", 1)[-1]


def get_audio_features(track_ids):
    features = {}
    for i in range(0, len(track_ids), BATCH):
        batch = track_ids[i : i + BATCH]
        r = requests.get(API, params={"ids": ",".join(batch)}, timeout=30)
        r.raise_for_status()
        for item in r.json().get("content", []):
            features[spotify_id_from_href(item["href"])] = item
    return features
