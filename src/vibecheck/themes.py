import math

# Each theme is a target profile: (mean, tolerance) per signal.
# Score per track = Gaussian kernel over normalized deviations -> explainable and continuous,
# instead of binary quadrant cuts.
DEFAULT_TOL = {"energy": 0.18, "valence": 0.22, "danceability": 0.18, "tempo": 18, "loudness": 4}

THEMES = [
    {"name": "Going to bed", "emoji": "😴", "target": {"energy": 0.13, "valence": 0.35, "danceability": 0.30, "tempo": 72, "loudness": -14}, "styles": ["acoustic", "ambient", "lofi", "soul"], "anti": ["dance", "house", "dnb"]},
    {"name": "Yoga / meditation", "emoji": "🧘", "target": {"energy": 0.12, "valence": 0.45, "danceability": 0.25, "tempo": 68, "loudness": -16}, "styles": ["ambient", "acoustic"], "anti": ["dance", "hiphop", "rock"]},
    {"name": "Deep focus / study", "emoji": "📚", "target": {"energy": 0.25, "valence": 0.40, "danceability": 0.35, "tempo": 95, "loudness": -13}, "styles": ["lofi", "ambient", "acoustic"], "anti": ["hiphop", "dance"]},
    {"name": "Brewing coffee", "emoji": "☕", "target": {"energy": 0.35, "valence": 0.62, "danceability": 0.50, "tempo": 98, "loudness": -11}, "styles": ["lofi", "acoustic", "soul", "pop"], "anti": ["dnb"]},
    {"name": "Sunday morning chill", "emoji": "🌅", "target": {"energy": 0.32, "valence": 0.68, "danceability": 0.48, "tempo": 92, "loudness": -11}, "styles": ["lofi", "acoustic", "pop", "soul"], "anti": ["dnb", "house"]},
    {"name": "Heartbreak", "emoji": "💔", "target": {"energy": 0.28, "valence": 0.15, "danceability": 0.35, "tempo": 82, "loudness": -10}, "styles": ["acoustic", "soul"], "anti": ["dance", "latin"]},
    {"name": "Dinner party", "emoji": "🍷", "target": {"energy": 0.42, "valence": 0.60, "danceability": 0.55, "tempo": 105, "loudness": -10}, "styles": ["soul", "pop", "latin"], "anti": ["dnb", "rage"]},
    {"name": "Date night", "emoji": "❤️", "target": {"energy": 0.42, "valence": 0.55, "danceability": 0.55, "tempo": 100, "loudness": -10}, "styles": ["soul", "pop"], "anti": ["dnb", "rage"]},
    {"name": "Late-night drive", "emoji": "🌃", "target": {"energy": 0.50, "valence": 0.30, "danceability": 0.55, "tempo": 100, "loudness": -9}, "styles": ["hiphop", "soul"], "anti": ["acoustic"]},
    {"name": "Beach / terrace", "emoji": "🏖️", "target": {"energy": 0.58, "valence": 0.75, "danceability": 0.70, "tempo": 105, "loudness": -8}, "styles": ["latin", "pop", "house"], "anti": ["ambient"]},
    {"name": "Road trip", "emoji": "🚗", "target": {"energy": 0.65, "valence": 0.70, "danceability": 0.60, "tempo": 122, "loudness": -7}, "styles": ["rock", "pop"], "anti": ["ambient"]},
    {"name": "Cleaning the house", "emoji": "🧹", "target": {"energy": 0.70, "valence": 0.75, "danceability": 0.75, "tempo": 118, "loudness": -6}, "styles": ["pop", "dance", "latin"], "anti": ["ambient", "acoustic"]},
    {"name": "Pre-party warm-up", "emoji": "🍸", "target": {"energy": 0.68, "valence": 0.65, "danceability": 0.72, "tempo": 116, "loudness": -7}, "styles": ["house", "pop", "latin", "dance"], "anti": ["ambient", "acoustic"]},
    {"name": "Party & keeping it awake", "emoji": "🎉", "target": {"energy": 0.85, "valence": 0.68, "danceability": 0.80, "tempo": 125, "loudness": -5}, "styles": ["dance", "house", "dnb", "latin", "hiphop"], "anti": ["ambient", "acoustic", "lofi", "soul"]},
    {"name": "Afters / sunrise set", "emoji": "🌇", "target": {"energy": 0.62, "valence": 0.35, "danceability": 0.75, "tempo": 122, "loudness": -8}, "styles": ["house", "dance"], "anti": ["acoustic", "rock"]},
    {"name": "Gaming", "emoji": "🎮", "target": {"energy": 0.80, "valence": 0.40, "danceability": 0.58, "tempo": 132, "loudness": -6}, "styles": ["dance", "house", "dnb", "rock"], "anti": ["acoustic", "lofi"]},
    {"name": "Running / cardio", "emoji": "🏃", "target": {"energy": 0.85, "valence": 0.55, "danceability": 0.65, "tempo": 163, "loudness": -5}, "tol": {"tempo": 26}, "styles": ["dance", "dnb", "rock"], "anti": ["ambient", "acoustic"]},
    {"name": "Late for a meeting", "emoji": "🏃‍♂️💼", "target": {"energy": 0.82, "valence": 0.50, "danceability": 0.65, "tempo": 152, "loudness": -6}, "tol": {"tempo": 16}, "styles": ["dance", "dnb", "rock", "hiphop"], "anti": ["ambient", "lofi", "acoustic", "soul"]},
    {"name": "Gym / lifting", "emoji": "💪", "target": {"energy": 0.90, "valence": 0.45, "danceability": 0.60, "tempo": 140, "loudness": -4}, "tol": {"tempo": 26}, "styles": ["hiphop", "rock", "dance"], "anti": ["ambient", "acoustic"]},
    {"name": "Rage / venting", "emoji": "😤", "target": {"energy": 0.95, "valence": 0.20, "danceability": 0.50, "tempo": 150, "loudness": -4}, "tol": {"tempo": 25}, "styles": ["rock", "dnb"], "anti": ["acoustic", "ambient", "soul"]},
]

AXES = ("energy", "valence", "danceability", "tempo", "loudness")


def classify_style(f):
    # estimated from audio signals (ReccoBeats has no genre metadata) — one style per track
    t = f.get("tempo", 110)
    e, d = f["energy"], f["danceability"]
    sp = f.get("speechiness", 0.05)
    ac = f.get("acousticness", 0.2)
    ins = f.get("instrumentalness", 0.0)
    if ins >= 0.35 and e < 0.5 and d >= 0.4 and 60 <= t <= 100:
        return "lofi"
    if ins >= 0.5 and e < 0.55:
        return "ambient"
    if ac >= 0.6 and e < 0.55:
        return "acoustic"
    if t >= 158 and e >= 0.65:
        return "dnb"
    if sp >= 0.15 and d >= 0.55:
        return "hiphop"
    if 86 <= t <= 106 and d >= 0.70 and sp >= 0.05:
        return "latin"
    if d >= 0.62 and e >= 0.68 and ac < 0.25 and 114 <= t <= 134:
        return "house" if ins >= 0.10 else "dance"
    if e >= 0.68 and d < 0.58:
        return "rock"
    if e < 0.50 and f.get("valence", 0.5) < 0.55 and ac >= 0.25:
        return "soul"
    return "pop"


def _track_fit(f, theme):
    tol = {**DEFAULT_TOL, **theme.get("tol", {})}
    values = {**f, "tempo": f.get("tempo", 110), "loudness": f.get("loudness", -8)}
    z2 = sum(((values[a] - theme["target"][a]) / tol[a]) ** 2 for a in AXES) / len(AXES)
    fit = math.exp(-z2 / 2)
    style = classify_style(f)
    if style in theme["styles"]:
        fit = min(1.0, fit * 1.15)
    elif style in theme.get("anti", []):
        fit *= 0.80
    return fit


def _why(features_list, theme):
    tol = {**DEFAULT_TOL, **theme.get("tol", {})}
    words = {"energy": ("more intense", "calmer"), "valence": ("happier", "sadder"),
             "danceability": ("more danceable", "less danceable"),
             "tempo": ("faster", "slower"), "loudness": ("louder", "softer")}
    zs = {}
    for a in AXES:
        vals = [f.get(a) if f.get(a) is not None else (110 if a == "tempo" else -8) for f in features_list]
        zs[a] = (sum(vals) / len(vals) - theme["target"][a]) / tol[a]
    axis = max(zs, key=lambda a: abs(zs[a]))
    if abs(zs[axis]) < 0.8:
        return "solid fit across all signals"
    return f"playlist is {words[axis][0] if zs[axis] > 0 else words[axis][1]} than this calls for"


def theme_scores(features_list):
    results = []
    for theme in THEMES:
        fits = [_track_fit(f, theme) for f in features_list]
        score = round(100 * sum(fits) / len(fits))
        results.append({"name": theme["name"], "emoji": theme["emoji"], "score": score,
                        "why": _why(features_list, theme)})
    return sorted(results, key=lambda r: -r["score"])


def style_distribution(features_list):
    counts = {}
    for f in features_list:
        s = classify_style(f)
        counts[s] = counts.get(s, 0) + 1
    total = len(features_list)
    return sorted(({"style": s, "pct": round(100 * c / total)} for s, c in counts.items()),
                  key=lambda x: -x["pct"])
