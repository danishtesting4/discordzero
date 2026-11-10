# DiscordZero

A performance-focused Valenced-based Discord fork.

## Discord APK downloader

DiscordZero includes a standalone downloader for the original Discord APK splits used as inputs to later patching and unbloating steps.

The latest stable Android version checked for this setup is **352.17**. The version is configurable when manually starting the GitHub Actions workflow.

The mirror order matches the current Valenced Manager source:
1. `https://proxy.vd.ushie.dev` (default mirror)
2. `https://tracker.vendetta.rocks` (fallback mirror)

Valenced Manager lets users choose their preferred mirror and tries the other mirror if the selected one fails. DiscordZero supports the same preference with `--mirror`. A redirect from the proxy's website root does not establish whether a specific `/tracker/download/...` route works, so the downloader validates the actual response rather than trusting the hostname.

### GitHub Actions download

Open **Actions → Download Discord APK inputs → Run workflow**.

Inputs:
- Discord version (defaults to `352.17`)
- Preferred mirror (defaults to `ushie-proxy`)
- Native-library ABI: `arm64_v8a`, `armeabi_v7a`, `x86_64`, `x86`, or `all` (defaults to `arm64_v8a`)

Choose one ABI for a device-specific input set, or choose **`all`** to download all four native-library splits. The workflow downloads and validates `base`, `config.en`, `config.xxhdpi`, and the selected `config.<abi>` split(s). With `all`, that means all four ABI splits are included in the same artifact. This is a collection of split APK inputs, not a prebuilt universal APK.

It then creates an input manifest containing each file's size and SHA-256 digest, and uploads the files as a downloadable Actions artifact for seven days. It does not commit APKs to the repository or publish anything into `release/`.

### Run the downloader locally

Requires Python 3.10 or newer and no third-party packages.

```sh
python3 scripts/download_base_apk.py --version 352.17
```

By default, this saves `build/base-352.17.apk`. Choose the other mirror first with `--mirror vendetta-tracker`. Use `--output` to choose another path, `--sha256` to check a trusted checksum, and `--timeout` to change the per-mirror timeout.

### Download other splits manually

```sh
python3 scripts/download_base_apk.py --version 352.17 --split config.en
python3 scripts/download_base_apk.py --version 352.17 --split config.arm64_v8a
python3 scripts/download_base_apk.py --version 352.17 --split config.xxhdpi
```

Use the ABI that matches the target device. Valenced Manager derives its split name from the device's first supported ABI, replacing `-v` with `_v` (for example, `arm64-v8a` becomes `arm64_v8a`).

The downloader validates that each response is an APK archive containing `AndroidManifest.xml`, rejects non-HTTPS redirects, and only moves a file into its final path after validation. It prints the SHA-256 digest for reproducibility.

The tool only retrieves and validates APK splits. It does not patch, modify, install, or publish them. Downloaded files stay in the ignored local `build/` directory rather than being committed to this repository.

Reference implementation: [Valenced Manager](https://github.com/Valenced/valenced-manager), especially its [mirror preference](https://github.com/Valenced/valenced-manager/blob/main/app/src/main/java/app/valenced/manager/domain/manager/PreferenceManager.kt) and [download-step fallback logic](https://github.com/Valenced/valenced-manager/blob/main/app/src/main/java/app/valenced/manager/installer/step/download/base/DownloadStep.kt).

## Tracker watcher

GitHub Actions checks the public Vendetta tracker index every five minutes and can also be started manually from the Actions tab. When the response changes, the latest raw response is saved to `data/tracker-index.json` in a commit.

The watcher intentionally compares the response bytes without assuming a particular JSON schema. If the endpoint is unavailable or returns an empty response, the run fails and preserves the last known snapshot.
