# playlist-vibecheck

[![CI](https://github.com/JuanVC-Devs/playlist-vibecheck/actions/workflows/ci.yml/badge.svg)](https://github.com/JuanVC-Devs/playlist-vibecheck/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A small CLI that analyzes any **public Spotify playlist**: it tells you the **key (tonality)** of every track — in musical notation and DJ [Camelot wheel](https://mixedinkey.com/harmonic-mixing-guide/) notation — and whether each track **matches the overall vibe** of the playlist or breaks it.

> **How it works:** Spotify deprecated its audio-features endpoint for new apps (Nov 2024), so this tool uses the Spotify Web API only to list the playlist tracks, and the free [ReccoBeats API](https://reccobeats.com/) to get key, mode, energy, valence, and danceability per track. The "vibe" is the centroid of the playlist in (energy, valence, danceability) space; tracks too far from the centroid are flagged as vibe-breakers.

## Requirements

- Python ≥ 3.10
- A (free) Spotify developer app for API credentials: create one at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), no special settings needed.

## Installation

```bash
git clone https://github.com/JuanVC-Devs/playlist-vibecheck.git
cd playlist-vibecheck
pip install .
```

## Quick start

Save your client ID once (or set the `SPOTIFY_CLIENT_ID` env var):

```bash
echo '{"client_id": "your_client_id"}' > ~/.vibecheck-config.json
```

### Web UI (recommended)

```bash
vibecheck --web
```

Opens a local dashboard at `http://127.0.0.1:8899`: paste a playlist URL and get the vibe summary, a valence/energy map with vibe-breakers highlighted, and the full track table with keys, Camelot badges, BPM, and per-track party score.

It also includes **Set Mode**: reorder the playlist like a DJ set (party arc, ramp, or smooth flow), with a party-score curve comparing your current order vs the proposed one and a quality marker per transition (harmonic compatibility on the Camelot wheel + BPM jump).

The vibe model is a weighted blend of five signals — energy (30%), danceability (25%), valence (20%), tempo (15%), loudness (10%) — validated against party-anthem vs ballad ground truth, so two tracks with similar energy/valence but different rhythm rank differently, as they should.

### Terminal

```bash
vibecheck --login https://open.spotify.com/playlist/YOUR_PLAYLIST_ID
```

The first analysis opens your browser once to authorize with your Spotify account (OAuth PKCE — no client secret needed); the token is cached and refreshed automatically at `~/.vibecheck-token.json`. Your Spotify app must have `http://127.0.0.1:8888/callback` registered as a Redirect URI.

**Why `--login` is required:** Spotify apps created after late 2024 run in "development mode" and cannot read playlist contents with app-only credentials (`403` on every playlist, including your own). With a user token the tracks are returned inside the playlist object under a renamed `items` field, which this tool handles transparently. App-only mode (`SPOTIFY_CLIENT_SECRET` + no `--login`) still works for apps created before the restriction.

Expected output:

```
Playlist: "Today's Top Hits" — 50 tracks
Playlist vibe: euphoric / party (energy 0.68, valence 0.55)

     Track                            Artist               Key       Camelot Dist
------------------------------------------------------------------------------
ok   Song A                           Artist A             C major   8B      0.04
ok   Song B                           Artist B             A minor   8A      0.11
!!   Sad Outlier                      Artist C             F minor   4A      0.38

48/50 tracks match the playlist vibe (96%). Tracks marked '!!' break the vibe.
```

Tune the strictness with `--threshold` (default `0.25`; lower = stricter).

## What the columns mean

- **Key** — the musical tonality (e.g. `C major`, `A minor`), from ReccoBeats' `key`/`mode`.
- **Camelot** — the same key in Camelot wheel notation: tracks whose numbers are equal or adjacent (e.g. `8A`/`8B`/`9A`) mix harmonically.
- **Dist** — how far the track sits from the playlist's vibe centroid (0 = perfectly on-vibe).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
