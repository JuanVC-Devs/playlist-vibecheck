# 🎧 playlist-vibecheck

**Key detection, vibe analysis and DJ-style reordering for any public Spotify playlist — no API keys, no login, no setup.**

[![CI](https://github.com/JuanVC-Devs/playlist-vibecheck/actions/workflows/ci.yml/badge.svg)](https://github.com/JuanVC-Devs/playlist-vibecheck/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![No API keys](https://img.shields.io/badge/Spotify%20credentials-not%20needed-1db954.svg)](#how-it-works)

Paste a playlist URL and get:

- 🎯 **What is this playlist for?** — scored against 20 activity profiles (party & keeping it awake, going to bed, running late for a meeting, brewing coffee, gym, heartbreak…), each a target profile over energy, valence, danceability, tempo and loudness. You get a verdict ("Best for: 💪 Gym, 83% fit") and the limiting signal for every theme.
- 🎸 **Estimated styles** — every track classified (dance, house, hip-hop, latin, rock, pop, soul, acoustic, ambient, dnb) from its audio signals, with the playlist's style distribution.
- 🎹 **The key of every track** — musical notation (`C major`, `A minor`) *and* [Camelot wheel](https://mixedinkey.com/harmonic-mixing-guide/) codes (`8B`, `8A`) for harmonic mixing.
- 🎯 **Vibe match** — which tracks belong and which ones break the playlist's vibe (and *why*: "sadder than the playlist", "slower", "less danceable").
- 🗺️ **A vibe map** — every track plotted on a valence/energy chart with the outliers labeled, plus a real example track in each corner (party / chill / intense / moody).
- 🎚️ **Set Mode** — reorder the playlist like a DJ set: party arc (warm-up → peak → cooldown), ramp, or smooth flow with harmonic transitions. See your current pace vs. the proposed one, with a 🟢🟡🟠🔴 quality marker per transition (Camelot compatibility + BPM jump).

## Try it in 30 seconds

```bash
git clone https://github.com/JuanVC-Devs/playlist-vibecheck.git
cd playlist-vibecheck
pip install .
vibecheck --demo          # instant demo with bundled data, no network needed
```

Then the real thing — web UI:

```bash
vibecheck --web           # dashboard at http://127.0.0.1:8899
```

or terminal:

```bash
vibecheck https://open.spotify.com/playlist/YOUR_PUBLIC_PLAYLIST
```

```
Playlist: "Dancing through the 2000s" — 100 tracks
Playlist vibe: euphoric / party (energy 0.80, valence 0.53)

     Track                        Artist            Key       Camelot Dist
---------------------------------------------------------------------------
ok   Red Lights                   Tiësto            A# major  6B      0.02
ok   Beautiful Now                Zedd, Jon Bellion B minor   10A     0.03
!!   Faded                        Alan Walker       F# major  2B      0.28   sadder than the playlist
```

## How it works

Spotify deprecated its audio-features API and locked playlist reads for new developer apps (2024–2025). vibecheck routes around all of it:

1. **Track list** — read from Spotify's public embed page (the same data any anonymous visitor gets). No API app, no OAuth.
2. **Audio features** — key, mode, energy, valence, danceability, tempo and loudness from the free [ReccoBeats](https://reccobeats.com/) API, which recreates the deprecated Spotify features with ML models.
3. **The math** — transparent and tweakable ([analysis.py](src/vibecheck/analysis.py)):
   - **Vibe** = centroid of all tracks in a weighted 5-signal space: energy `.30`, danceability `.25`, valence `.20`, tempo `.15`, loudness `.10` (weights validated against party-anthem vs. ballad ground truth).
   - **Vibe breakers** = tracks whose weighted distance to the centroid exceeds the threshold (default `0.20`).
   - **Party score** = weighted blend of the same signals, per track.
   - **Set Mode transitions** = vibe distance + Camelot penalty + BPM-jump penalty, greedy nearest-neighbor for smooth flow.

## Limitations (honest ones)

- **Public playlists only** — private/unlisted playlists don't expose their data. You'll get a clear error, not a mystery.
- **First ~100 tracks** — that's what Spotify embeds in the page.
- **Feature accuracy** — ReccoBeats estimates are very good but occasionally match a different version of a song (e.g. a slower remix).

## Roadmap

- [ ] Write the reordered set back to Spotify (optional login)
- [ ] Compare multiple playlists on one vibe map
- [ ] Export set order as M3U / CSV
- [ ] PyPI package (`pip install playlist-vibecheck`)

PRs welcome — see the issues labeled [`good first issue`](https://github.com/JuanVC-Devs/playlist-vibecheck/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Tests run fully offline: `pip install -e ".[dev]" && pytest`. By participating you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
