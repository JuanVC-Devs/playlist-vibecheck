KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot wheel: harmonic-mixing notation used by DJs (adjacent numbers mix well)
MAJOR_CAMELOT = {0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B", 6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B"}
MINOR_CAMELOT = {0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A", 6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A"}

# weights for the vibe space: rhythm and loudness matter for "party-ness",
# not just energy/valence (validated against anthem-vs-ballad ground truth)
AXIS_WEIGHTS = {"energy": 0.30, "danceability": 0.25, "valence": 0.20, "tempo_n": 0.15, "loudness_n": 0.10}


def normalize(features):
    n = {a: features[a] for a in ("energy", "valence", "danceability")}
    n["tempo_n"] = min(1.0, max(0.0, (features.get("tempo", 100) - 60) / 120))
    n["loudness_n"] = min(1.0, max(0.0, (features.get("loudness", -30) + 30) / 30))
    return n


def key_name(key, mode):
    if key is None or key < 0:
        return "?"
    return f"{KEY_NAMES[key]} {'major' if mode == 1 else 'minor'}"


def camelot(key, mode):
    if key is None or key < 0:
        return "?"
    return (MAJOR_CAMELOT if mode == 1 else MINOR_CAMELOT)[key]


def centroid(features_list):
    ns = [normalize(f) for f in features_list]
    return {a: sum(n[a] for n in ns) / len(ns) for a in AXIS_WEIGHTS}


def vibe_distance(features, center):
    n = normalize(features)
    return (sum(w * (n[a] - center[a]) ** 2 for a, w in AXIS_WEIGHTS.items())) ** 0.5


def spread(features_list):
    ns = [normalize(f) for f in features_list]
    out = {}
    for a in ("energy", "valence", "danceability"):
        mean = sum(n[a] for n in ns) / len(ns)
        out[a] = round((sum((n[a] - mean) ** 2 for n in ns) / len(ns)) ** 0.5, 3)
    return out


def party_score(features):
    n = normalize(features)
    return sum(w * n[a] for a, w in AXIS_WEIGHTS.items())


def deviation_reason(features, center):
    n = normalize(features)
    diffs = {a: n[a] - center[a] for a in AXIS_WEIGHTS}
    axis = max(diffs, key=lambda a: AXIS_WEIGHTS[a] * abs(diffs[a]))
    words = {
        ("energy", True): "more intense",
        ("energy", False): "more mellow",
        ("valence", True): "happier",
        ("valence", False): "sadder",
        ("danceability", True): "more danceable",
        ("danceability", False): "less danceable",
        ("tempo_n", True): "faster",
        ("tempo_n", False): "slower",
        ("loudness_n", True): "louder",
        ("loudness_n", False): "softer",
    }
    return f"{words[(axis, diffs[axis] > 0)]} than the playlist"


def dominant_camelot(features_list):
    counts = {}
    for f in features_list:
        c = camelot(f.get("key"), f.get("mode"))
        if c != "?":
            counts[c] = counts.get(c, 0) + 1
    return max(counts, key=counts.get) if counts else "?"


def vibe_label(center):
    e, v = center["energy"], center["valence"]
    if e >= 0.5 and v >= 0.5:
        return "euphoric / party"
    if e >= 0.5:
        return "intense / dark energy"
    if v >= 0.5:
        return "chill / feel-good"
    return "melancholic / moody"
