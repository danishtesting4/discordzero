# DiscordZero

A performance-focused Valenced-based Discord fork.

## Tracker watcher

GitHub Actions checks the public Vendetta tracker index every five minutes and can also be started manually from the Actions tab. When the response changes, the latest raw response is saved to `data/tracker-index.json` in a commit.

The watcher intentionally compares the response bytes without assuming a particular JSON schema. If the endpoint is unavailable or returns an empty response, the run fails and preserves the last known snapshot.
