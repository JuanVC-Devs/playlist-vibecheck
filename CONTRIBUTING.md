# Contributing to playlist-vibecheck

Thanks for your interest in contributing!

## Ways to contribute

- **Report bugs** — open an issue with steps to reproduce, expected vs. actual behavior, and your environment.
- **Suggest features** — open an issue first so we can discuss fit before you invest time in code.
- **Improve documentation** — always welcome, no prior discussion needed.

## Development setup

```bash
git clone https://github.com/JuanVC-Devs/playlist-vibecheck.git
cd playlist-vibecheck
pip install -e ".[dev]"
pytest
```

Tests run fully offline — no Spotify credentials needed.

## Submitting a pull request

1. For non-trivial changes, open an issue first.
2. Fork and branch from `main`.
3. Requirements for merge: tests for new behavior, docs updated in the same PR, CI green (`ruff check src tests` + `pytest`).
4. Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`...).
5. Sign off your commits (`git commit -s`) — we use the [Developer Certificate of Origin](https://developercertificate.org/).

## Licensing of contributions

By contributing, you agree your contributions are licensed under the project's [MIT license](LICENSE). Only submit code you have the right to submit.
