# DiscordZero

A performance-focused Valenced-based Discord fork.

## Base APK downloader

DiscordZero includes a standalone downloader for the original Discord base APK used as the input to later patching and unbloating steps.

The downloader:
- Requests `/tracker/download/<version>/base` from the primary Vendetta tracker.
- Falls back in order to the Vendetta proxy, K6, and NEXPID mirrors.
- Tries each unique mirror once (the Valenced Manager source lists the Vendetta proxy twice under separate enum names).
- Rejects non-HTTPS redirects, invalid ZIP/APK responses, and files without `AndroidManifest.xml`.
- Optionally checks a trusted SHA-256 value.
- Writes to the final output path only after validation succeeds.

### Usage

Requires Python 3.10 or newer and no third-party packages.

```sh
python3 scripts/download_base_apk.py --version 352006
```

By default, the APK is saved as `build/base-352006.apk`. Choose a different output path with `--output`, and optionally provide a trusted checksum with `--sha256`.

The downloader only retrieves and validates the base APK. It does not patch, modify, install, or publish it. The APK is kept as a local build input rather than committed to this repository.

## Tracker watcher

GitHub Actions checks the public Vendetta tracker index every five minutes and can also be started manually from the Actions tab. When the response changes, the latest raw response is saved to `data/tracker-index.json` in a commit.

The watcher intentionally compares the response bytes without assuming a particular JSON schema. If the endpoint is unavailable or returns an empty response, the run fails and preserves the last known snapshot.
