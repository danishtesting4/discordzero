#!/usr/bin/env python3
"""Download and validate Discord APK splits from Valenced Manager's mirrors.

This script retrieves original Discord APK inputs only. It does not patch,
modify, install, or publish the downloaded files.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable

# Current Valenced Manager mirror enum; the proxy is the default preference.
MIRRORS = (
    ("ushie-proxy", "https://proxy.vd.ushie.dev"),
    ("vendetta-tracker", "https://tracker.vendetta.rocks"),
)
DEFAULT_MIRROR = "ushie-proxy"
USER_AGENT = "DiscordZero-BaseDownloader/1.2"
CHUNK_SIZE = 1024 * 1024
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
DISPLAY_VERSION_RE = re.compile(r"^(\d+)\.(\d{1,3})$")
SPLIT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DownloadError(Exception):
    """Raised when no mirror produces a valid APK."""


def validate_component(value: str, label: str, pattern: re.Pattern[str]) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(
            f"Invalid {label}. Use only letters, numbers, dots, underscores, and hyphens."
        )
    return value


def normalize_tracker_version(version: str) -> str:
    """Convert display versions (352.17) to tracker codes (352017)."""
    version = validate_component(version, "Discord version", VERSION_RE)
    match = DISPLAY_VERSION_RE.fullmatch(version)
    if match:
        major, minor = match.groups()
        return f"{major}{minor.zfill(3)}"
    return version


def validate_version(version: str) -> str:
    return normalize_tracker_version(version)


def validate_split(split: str) -> str:
    return validate_component(split, "APK split name", SPLIT_RE)


def build_mirror_urls(
    version: str,
    split: str = "base",
    preferred_mirror: str = DEFAULT_MIRROR,
    mirrors: Iterable[tuple[str, str]] = MIRRORS,
):
    version = normalize_tracker_version(version)
    split = validate_split(split)
    mirror_list = list(mirrors)
    names = {name for name, _ in mirror_list}
    if preferred_mirror not in names:
        raise ValueError(f"Unknown mirror: {preferred_mirror}")
    mirror_list.sort(key=lambda item: item[0] != preferred_mirror)

    path = (
        f"/tracker/download/{urllib.parse.quote(version, safe='')}/"
        f"{urllib.parse.quote(split, safe='')}"
    )
    seen: set[str] = set()
    for name, base_url in mirror_list:
        url = base_url.rstrip("/") + path
        if url not in seen:
            seen.add(url)
            yield name, url


def validate_apk(path: Path) -> None:
    """Check that the file is a readable APK ZIP containing AndroidManifest.xml."""
    if not path.is_file() or path.stat().st_size < 4:
        raise ValueError("Downloaded file is empty or too small.")

    with path.open("rb") as stream:
        if stream.read(4)[:2] != b"PK":
            raise ValueError("Response is not a ZIP/APK file.")

    try:
        with zipfile.ZipFile(path) as apk:
            if "AndroidManifest.xml" not in apk.namelist():
                raise ValueError("ZIP file does not contain AndroidManifest.xml.")
            if not apk.read("AndroidManifest.xml"):
                raise ValueError("AndroidManifest.xml is empty.")
    except zipfile.BadZipFile as exc:
        raise ValueError("Downloaded file is not a valid APK archive.") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_from_url(url: str, destination: Path, timeout: int) -> None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.android.package-archive, application/octet-stream, */*",
        },
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise DownloadError(f"HTTP {response.status}")
        if not response.geturl().startswith("https://"):
            raise DownloadError("Refusing a non-HTTPS redirect.")

        with destination.open("wb") as output:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                output.write(chunk)


def download_split(
    version: str,
    split: str,
    output: Path,
    expected_sha256: str | None = None,
    timeout: int = 60,
    preferred_mirror: str = DEFAULT_MIRROR,
) -> tuple[str, str, int]:
    version = normalize_tracker_version(version)
    split = validate_split(split)
    output.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".part", dir=output.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    failures: list[str] = []

    try:
        for mirror_name, url in build_mirror_urls(version, split, preferred_mirror):
            try:
                print(f"Trying {mirror_name}: {url}", flush=True)
                download_from_url(url, temporary, timeout)
                validate_apk(temporary)
                digest = sha256_file(temporary)

                if expected_sha256 and digest.lower() != expected_sha256.lower():
                    raise ValueError(
                        f"SHA-256 mismatch (expected {expected_sha256}, got {digest})"
                    )

                size = temporary.stat().st_size
                temporary.replace(output)
                return mirror_name, digest, size
            except (
                urllib.error.URLError,
                TimeoutError,
                OSError,
                ValueError,
                DownloadError,
                zipfile.BadZipFile,
            ) as exc:
                message = f"{mirror_name}: {exc}"
                failures.append(message)
                print(f"Mirror failed: {message}", file=sys.stderr, flush=True)

        raise DownloadError("All mirrors failed. " + " | ".join(failures))
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and validate a Discord APK split from Valenced tracker mirrors."
    )
    parser.add_argument("--version", required=True, help="Discord version (for example 352.17 or tracker code 352017)")
    parser.add_argument(
        "--split",
        default="base",
        help="APK split to download (default: base; examples: config.en, config.arm64_v8a, config.xxhdpi)",
    )
    parser.add_argument(
        "--mirror",
        choices=[name for name, _ in MIRRORS],
        default=DEFAULT_MIRROR,
        help="Preferred mirror (default: ushie-proxy)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output APK path (default: build/SPLIT-VERSION.apk)",
    )
    parser.add_argument(
        "--sha256",
        help="Optional expected SHA-256 checksum from a trusted source",
    )
    parser.add_argument("--timeout", type=int, default=60, help="Per-mirror timeout in seconds")
    args = parser.parse_args()

    if args.timeout < 1:
        parser.error("--timeout must be at least 1 second")
    if args.sha256 and not re.fullmatch(r"[A-Fa-f0-9]{64}", args.sha256):
        parser.error("--sha256 must contain exactly 64 hexadecimal characters")

    try:
        validate_version(args.version)
        validate_split(args.split)
    except ValueError as exc:
        parser.error(str(exc))

    output = args.output or Path("build") / f"{args.split}-{args.version}.apk"

    try:
        mirror, digest, size = download_split(
            args.version,
            args.split,
            output,
            args.sha256,
            args.timeout,
            args.mirror,
        )
    except (ValueError, DownloadError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Downloaded from: {mirror}")
    print(f"Saved to: {output}")
    print(f"Size: {size:,} bytes")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
