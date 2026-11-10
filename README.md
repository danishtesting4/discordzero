# DiscordZero

A performance-focused Valenced-based Discord fork.

## Discord APK downloader

DiscordZero includes a standalone downloader for the original Discord APK splits used as inputs to later patching and unbloating steps.

The mirror order matches the current Valenced Manager source:
1. `https://proxy.vd.ushie.dev` (default mirror)
2. `https://tracker.vendetta.rocks` (fallback mirror)

The manager lets users choose their preferred mirror and tries the other mirror if the selected one fails. The website root redirect does not establish whether a specific `/tracker/download/...` route works, so the downloader validates the actual response rather than trusting the hostname.

### Download the base APK

Requires Python 3.10 or newer and no third-party packages.

```sh
python3 scripts/download_base_apk.py --version 352006
```

By default, this saves `build/base-352006.apk`. Use `--output` to choose another path, `--sha256` to check a trusted checksum, and `--timeout` to change the per-mirror timeout.

### Download other splits

Valenced Manager's install pipeline also downloads the English language split, the device ABI's native-library split, and the xxhdpi resources split. The downloader can fetch each one:

```sh
python3 scripts/download_base_apk.py --version 352006 --split config.en
python3 scripts/download_base_apk.py --version 352006 --split config.arm64_v8a
python3 scripts/download_base_apk.py --version 352006 --split config.xxhdpi
```

Use the ABI that matches the target device. Valenced Manager derives its split name from the device's first supported ABI, replacing `-v` with `_v` (for example, `arm64-v8a` becomes `arm64_v8a`).

The downloader validates that each response is an APK archive containing `AndroidManifest.xml`, rejects non-HTTPS redirects, and only moves a file into its final path after validation. It prints the SHA-256 digest for reproducibility.

The tool only retrieves and validates APK splits. It does not patch, modify, install, or publish them. Downloaded files stay in the ignored local `build/` directory rather than being committed to this repository.

Reference implementation: [Valenced Manager](https://github.com/Valenced/valenced-manager), especially its mirror preference and download-step code.

## Tracker watcher

GitHub Actions checks the public Vendetta tracker index every five minutes and can also be started manually from the Actions tab. When the response changes, the latest raw response is saved to `data/tracker-index.json` in a commit.

The watcher intentionally compares the response bytes without assuming a particular JSON schema. If the endpoint is unavailable or returns an empty response, the run fails and preserves the last known snapshot.
