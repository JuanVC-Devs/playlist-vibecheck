import argparse

from . import analysis, reccobeats, spotify


def main():
    p = argparse.ArgumentParser(prog="vibecheck", description="Key (tonality) + vibe-match analysis for public Spotify playlists.")
    p.add_argument("playlist", help="Spotify playlist URL or ID")
    p.add_argument("--threshold", type=float, default=0.25, help="max vibe distance to count as matching (default: 0.25)")
    args = p.parse_args()

    playlist_id = spotify.parse_playlist_id(args.playlist)
    token = spotify.get_token()
    name, tracks = spotify.get_playlist(playlist_id, token)
    print(f'\nPlaylist: "{name}" — {len(tracks)} tracks')

    features = reccobeats.get_audio_features([t["id"] for t in tracks])
    analyzed = [{**t, "f": features[t["id"]]} for t in tracks if t["id"] in features]
    missing = len(tracks) - len(analyzed)
    if missing:
        print(f"(no audio features available for {missing} track(s) — skipped)")
    if not analyzed:
        raise SystemExit("No tracks could be analyzed.")

    center = analysis.centroid([t["f"] for t in analyzed])
    print(f"Playlist vibe: {analysis.vibe_label(center)} (energy {center['energy']:.2f}, valence {center['valence']:.2f})\n")

    header = f"{'':4} {'Track':32} {'Artist':20} {'Key':9} {'Camelot':7} {'Dist':4}"
    print(header)
    print("-" * len(header))
    matches = 0
    for t in sorted(analyzed, key=lambda t: analysis.vibe_distance(t["f"], center)):
        f = t["f"]
        dist = analysis.vibe_distance(f, center)
        ok = dist <= args.threshold
        matches += ok
        mark = "ok" if ok else "!!"
        print(f"{mark:4} {t['name'][:32]:32} {t['artist'][:20]:20} {analysis.key_name(f['key'], f['mode']):9} "
              f"{analysis.camelot(f['key'], f['mode']):7} {dist:.2f}")

    pct = 100 * matches / len(analyzed)
    print(f"\n{matches}/{len(analyzed)} tracks match the playlist vibe ({pct:.0f}%). Tracks marked '!!' break the vibe.")


if __name__ == "__main__":
    main()
