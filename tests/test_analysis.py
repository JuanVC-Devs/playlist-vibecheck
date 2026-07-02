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
        {"energy": 0.8, "valence": 0.6, "danceability": 0.7},
        {"energy": 0.6, "valence": 0.8, "danceability": 0.5},
    ]
    c = analysis.centroid(fs)
    assert c == {"energy": 0.7, "valence": 0.7, "danceability": 0.6}
    assert analysis.vibe_distance(c, c) == 0
    assert analysis.vibe_distance(fs[0], c) > 0


def test_vibe_labels():
    assert analysis.vibe_label({"energy": 0.9, "valence": 0.9}) == "euphoric / party"
    assert analysis.vibe_label({"energy": 0.9, "valence": 0.2}) == "intense / dark energy"
    assert analysis.vibe_label({"energy": 0.2, "valence": 0.9}) == "chill / feel-good"
    assert analysis.vibe_label({"energy": 0.2, "valence": 0.2}) == "melancholic / moody"


def test_parse_playlist_id():
    assert spotify.parse_playlist_id("37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"
    assert spotify.parse_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc") == "37i9dQZF1DXcBWIGoYBM5M"
    assert spotify.parse_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"


def test_spotify_id_from_href():
    assert reccobeats.spotify_id_from_href("https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8") == "4PTG3Z6ehGkBFwjybzWkR8"


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
