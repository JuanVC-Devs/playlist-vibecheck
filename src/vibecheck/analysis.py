KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot wheel: harmonic-mixing notation used by DJs (adjacent numbers mix well)
MAJOR_CAMELOT = {0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B", 6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B"}
MINOR_CAMELOT = {0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A", 6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A"}

VIBE_AXES = ("energy", "valence", "danceability")


def key_name(key, mode):
    if key is None or key < 0:
        return "?"
    return f"{KEY_NAMES[key]} {'major' if mode == 1 else 'minor'}"


def camelot(key, mode):
    if key is None or key < 0:
        return "?"
    return (MAJOR_CAMELOT if mode == 1 else MINOR_CAMELOT)[key]


def centroid(features_list):
    return {a: sum(f[a] for f in features_list) / len(features_list) for a in VIBE_AXES}


def vibe_distance(features, center):
    return (sum((features[a] - center[a]) ** 2 for a in VIBE_AXES) / len(VIBE_AXES)) ** 0.5


def vibe_label(center):
    e, v = center["energy"], center["valence"]
    if e >= 0.5 and v >= 0.5:
        return "euphoric / party"
    if e >= 0.5:
        return "intense / dark energy"
    if v >= 0.5:
        return "chill / feel-good"
    return "melancholic / moody"
