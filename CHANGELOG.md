# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/), versioning: [SemVer](https://semver.org/).

## [0.1.0] - 2026-07-02

### Changed
- No Spotify credentials of any kind needed anymore: playlist data is read from Spotify's public share page. Works for public playlists (first ~100 tracks); private playlists are not supported. The earlier OAuth `--login` flow and token caching were removed before any release.

### Added
- Initial version: `vibecheck` CLI that analyzes a public Spotify playlist — key/tonality per track (musical + Camelot notation) and vibe-match detection against the playlist centroid.
- `--demo` flag and "Try demo" button: instant analysis of a bundled 80-track dataset, no network or playlist needed.
- One-page dashboard layout: vibe map and Set Mode pace curves side by side, track tables as tabs.
- Vibe label explained with real numbers (centroid vs. the 0.50 boundaries) plus a quadrant-composition bar (% party / intense / chill / moody).
- Vibe map shows a real example track in each corner and labels the top vibe-breakers directly on the chart.
- UI in English.
- `--web` flag: local web UI at `127.0.0.1:8899` — vibe summary cards, valence/energy scatter map with vibe-breakers highlighted, Camelot-colored key badges, and a ranked track table. Zero extra dependencies (stdlib server + vanilla JS).
- Per-track explanation of why a song breaks the vibe (e.g. "sadder than the playlist") and dominant Camelot key for the playlist.
- Weighted 5-signal vibe matrix (energy 30%, danceability 25%, valence 20%, tempo 15%, loudness 10%), validated against anthem-vs-ballad ground truth — fixes tracks that share energy/valence but differ in "party-ness". Default threshold recalibrated to 0.20.
- Per-track **party score** shown in the table and used across the UI.
- **Set Mode** in the web UI: reorder the playlist as a DJ set with three shapes (party arc, ramp, smooth flow via greedy nearest-neighbor on transition cost), party-score curve of current vs proposed order, and per-transition quality markers (Camelot harmonic compatibility + BPM jump).

### Fixed
- Support the renamed playlist payload (`items`/`item` instead of `tracks`/`track`) that Spotify returns to post-2024 dev-mode apps, including pagination across both shapes.
- UTF-8 output on Windows consoles (track names with emoji no longer crash the CLI).
