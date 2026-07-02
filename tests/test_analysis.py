from vibecheck import analysis, reccobeats, spotify


def test_key_names():
    assert analysis.key_name(0, 1) == "C major"
    assert analysis.key_name(9, 0) == "A minor"
    assert analysis.key_name(8, 1) == "G# major"
    assert analysis.key_name(None, 1) == "?"
    assert analysis.key_name(-1, 0) == "?"


def test_camelot_wheel():
    assert analysis.camelot(0, 1) == "8B"   # C major
    assert analysis.camelot(9, 0) == "8A"   # A minor (relative of C major, same number)
    assert analysis.camelot(7, 1) == "9B"   # G major (adjacent to C major)
    assert analysis.camelot(8, 1) == "4B"   # Ab major
    assert analysis.camelot(-1, 0) == "?"


def test_relative_keys_share_camelot_number():
    # every major key and its relative minor (key - 3 semitones) share a number
    for key in range(12):
        major = analysis.camelot(key, 1)
        rel_minor = analysis.camelot((key + 9) % 12, 0)
        assert major[:-1] == rel_minor[:-1]


def test_centroid_and_distance():
    fs = [
        {"energy": 0.8, "valence": 0.6, "danceability": 0.7, "tempo": 120, "loudness": -6},
        {"energy": 0.6, "valence": 0.8, "danceability": 0.5, "tempo": 120, "loudness": -6},
    ]
    c = analysis.centroid(fs)
    assert round(c["energy"], 6) == 0.7
    assert round(c["valence"], 6) == 0.7
    assert round(c["tempo_n"], 6) == 0.5
    assert analysis.vibe_distance({"energy": 0.7, "valence": 0.7, "danceability": 0.6, "tempo": 120, "loudness": -6}, c) < 1e-9
    assert analysis.vibe_distance(fs[0], c) > 0


def test_normalize_clamps_and_defaults():
    n = analysis.normalize({"energy": 0.5, "valence": 0.5, "danceability": 0.5, "tempo": 300, "loudness": -60})
    assert n["tempo_n"] == 1.0
    assert n["loudness_n"] == 0.0
    n = analysis.normalize({"energy": 0.5, "valence": 0.5, "danceability": 0.5})
    assert 0 <= n["tempo_n"] <= 1 and 0 <= n["loudness_n"] <= 1


def test_party_score_separates_anthems_from_ballads():
    anthem = {"energy": 0.85, "valence": 0.6, "danceability": 0.75, "tempo": 128, "loudness": -5}
    ballad = {"energy": 0.25, "valence": 0.2, "danceability": 0.4, "tempo": 80, "loudness": -12}
    assert analysis.party_score(anthem) > analysis.party_score(ballad) + 0.2


def test_vibe_labels():
    assert analysis.vibe_label({"energy": 0.9, "valence": 0.9}) == "euphoric / party"
    assert analysis.vibe_label({"energy": 0.9, "valence": 0.2}) == "intense / dark energy"
    assert analysis.vibe_label({"energy": 0.2, "valence": 0.9}) == "chill / feel-good"
    assert analysis.vibe_label({"energy": 0.2, "valence": 0.2}) == "melancholic / moody"


def test_deviation_reason():
    base = {"energy": 0.8, "valence": 0.5, "danceability": 0.6, "tempo": 120, "loudness": -6}
    center = analysis.centroid([base])
    sad = dict(base, valence=0.1)
    assert analysis.deviation_reason(sad, center) == "sadder than the playlist"
    mellow = dict(base, energy=0.3)
    assert analysis.deviation_reason(mellow, center) == "more mellow than the playlist"
    slow = dict(base, tempo=65)
    assert analysis.deviation_reason(slow, center) == "slower than the playlist"


def test_dominant_camelot():
    fs = [{"key": 0, "mode": 1}, {"key": 0, "mode": 1}, {"key": 9, "mode": 0}, {"key": None, "mode": 0}]
    assert analysis.dominant_camelot(fs) == "8B"
    assert analysis.dominant_camelot([{"key": None, "mode": 1}]) == "?"


def test_parse_playlist_id():
    assert spotify.parse_playlist_id("37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"
    assert spotify.parse_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc") == "37i9dQZF1DXcBWIGoYBM5M"
    assert spotify.parse_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"


def test_spotify_id_from_href():
    assert reccobeats.spotify_id_from_href("https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8") == "4PTG3Z6ehGkBFwjybzWkR8"


def test_get_playlist_parses_embed_page(monkeypatch):
    import json

    payload = {"props": {"pageProps": {"state": {"data": {"entity": {
        "name": "Test Mix",
        "trackList": [
            {"uri": "spotify:track:abc123", "title": "Song A", "subtitle": "Artist One"},
            {"uri": "spotify:episode:xyz", "title": "Podcast", "subtitle": "skip me"},
            {"uri": "spotify:track:def456", "title": "Song B", "subtitle": "Artist Two"},
        ],
    }}}}}}

    class FakeResponse:
        text = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script></html>'

        def raise_for_status(self):
            pass

    monkeypatch.setattr(spotify.requests, "get", lambda *a, **k: FakeResponse())
    name, tracks = spotify.get_playlist("whatever")
    assert name == "Test Mix"
    assert [t["id"] for t in tracks] == ["abc123", "def456"]
    assert tracks[0]["artist"] == "Artist One"


def test_get_audio_features_maps_by_spotify_id(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"href": "https://open.spotify.com/track/abc123", "key": 0, "mode": 1,
                                 "energy": 0.5, "valence": 0.5, "danceability": 0.5}]}

    monkeypatch.setattr(reccobeats.requests, "get", lambda *a, **k: FakeResponse())
    features = reccobeats.get_audio_features(["abc123"])
    assert features["abc123"]["key"] == 0
