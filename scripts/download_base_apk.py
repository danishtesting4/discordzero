#!/usr/bin/env python3
"""Download a Discord base APK using Valenced Manager's mirror order.

The script intentionally downloads only the base split. It does not patch,
modify, install, or publish the APK.
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

MIRRORS = (
    ("tracker", "https://tracker.vendetta.rocks"),
    ("vendetta-proxy", "https://proxy.vendetta.rocks"),
    ("k6", "https://vd.k6.tf"),
    ("nexpid", "https://tracker.vd.nexpid.xyz"),
)
USER_AGENT = "DiscordZero-BaseDownloader/1.0"
CHUNK_SIZE = 1024 * 1024
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DownloadError(Exception):
    """Raised when no mirror produces a valid APK."""


def validate_version(version: str) -> str:
    if not VERSION_RE.fullmatch(version):
        raise ValueError(
            "Invalid Discord version. Use only letters, numbers, dots, "
            "underscores, and hyphens."
        )
    return version


def build_mirror_urls(version: str, mirrors: Iterable[tuple[str, str]] = MIRRORS):
    version = validate_version(version)
    path = f"/tracker/download/{urllib.parse.quote(version, safe='')}/base"
    seen: set[str] = set()
    for name, base_url in mirrors:
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
        final_url = response.geturl()
        if not final_url.startswith("https://"):
            raise DownloadError("Refusing a non-HTTPS redirect.")

        with destination.open("wb") as output:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                output.write(chunk)


def download_base(
    version: str,
    output: Path,
    expected_sha256: str | None = None,
    timeout: int = 60,
) -> tuple[str, str, int]:
    version = validate_version(version)
    output.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".part", dir=output.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    failures: list[str] = []

    try:
        for mirror_name, url in build_mirror_urls(version):
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

        raise DownloadError(
            "All mirrors failed. " + " | ".join(failures)
        )
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and validate a Discord base APK from Valenced tracker mirrors."
    )
    parser.add_argument("--version", required=True, help="Discord version listed by the tracker")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output APK path (default: build/base-VERSION.apk)",
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

    output = args.output or Path("build") / f"base-{args.version}.apk"

    try:
        mirror, digest, size = download_base(
            args.version, output, args.sha256, args.timeout
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
