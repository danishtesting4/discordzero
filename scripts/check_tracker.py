#!/usr/bin/env python3
"""Fetch the public Vendetta tracker index and report whether its bytes changed."""

import hashlib
import os
import pathlib
import sys
import urllib.error
import urllib.request

URL = os.environ.get(
    "TRACKER_INDEX_URL",
    "https://tracker.vendetta.rocks/tracker/index",
)
SNAPSHOT = pathlib.Path("data/tracker-index.json")


def main() -> int:
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "DiscordZero-TrackerWatcher/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"Tracker returned HTTP {response.status}")
            body = response.read()
    except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        print(f"::error::Could not fetch tracker index: {exc}")
        return 1

    if not body.strip():
        print("::error::Tracker returned an empty response; keeping last known snapshot.")
        return 1

    old_body = SNAPSHOT.read_bytes() if SNAPSHOT.exists() else None
    old_hash = hashlib.sha256(old_body).hexdigest() if old_body is not None else None
    new_hash = hashlib.sha256(body).hexdigest()

    if old_hash == new_hash:
        print(f"Tracker index unchanged (sha256: {new_hash}).")
        print("changed=false", file=open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8"))
        return 0

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_bytes(body)
    print(f"Tracker index changed: {old_hash or 'no previous snapshot'} -> {new_hash}")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("changed=true\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
