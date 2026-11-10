#!/usr/bin/env python3
"""Trim unused Discord locale caches while preserving Android resource IDs.

The output is an unsigned APK. Align and sign it after this script runs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

CACHE_PREFIX = "res/raw/cache_intl_"
CACHE_SUFFIX = "compiledmessages.jsona"
LOCALE_PATTERN = re.compile(r"_([A-Za-z0-9]+?)messages")
DEFAULT_KEEP_LOCALES = frozenset({"engb", "id"})
SIGNATURE_SUFFIXES = (".SF", ".RSA", ".DSA", ".EC")


def normalize_locale(locale: str) -> str:
    """Normalize locale tags such as en-GB or en_GB to the APK's enGB form."""
    return re.sub(r"[-_]", "", locale).lower()


def locale_from_cache_name(filename: str) -> str:
    """Extract the locale token immediately before 'messages' in a cache name."""
    matches = LOCALE_PATTERN.findall(Path(filename).name)
    if not matches:
        raise ValueError(f"Cannot identify locale in cache resource: {filename}")
    return matches[-1].lower()


def is_locale_cache(filename: str) -> bool:
    return (
        filename.startswith(CACHE_PREFIX)
        and filename.endswith(CACHE_SUFFIX)
    )


def is_v1_signature(filename: str) -> bool:
    if not filename.upper().startswith("META-INF/"):
        return False
    basename = filename.rsplit("/", 1)[-1].upper()
    return (
        basename == "MANIFEST.MF"
        or basename.endswith(SIGNATURE_SUFFIXES)
        or basename.startswith("SIG-")
    )


def trim_apk(
    input_path: str | Path,
    output_path: str | Path,
    keep_locales: Iterable[str] = DEFAULT_KEEP_LOCALES,
) -> dict[str, object]:
    """Replace non-kept locale message caches with {}, keeping their resource IDs."""
    source_path = Path(input_path)
    destination_path = Path(output_path)
    keep = {normalize_locale(locale) for locale in keep_locales}

    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if source_path.resolve() == destination_path.resolve():
        raise ValueError("Input and output APK paths must be different")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    replaced_names: set[str] = set()
    replaced_by_locale: dict[str, int] = {}
    original_compressed_bytes = 0
    cache_count = 0
    signature_files_removed: list[str] = []
    expected_entry_count = 0
    manifest_hash: bytes | None = None
    resources_hash: bytes | None = None

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        dir=destination_path.parent,
    )
    os.close(fd)
    temporary_path = Path(temporary_name)

    try:
        with zipfile.ZipFile(source_path, "r") as source:
            source_infos = source.infolist()
            names = {info.filename for info in source_infos}
            expected_entry_count = sum(not is_v1_signature(info.filename) for info in source_infos)
            if "AndroidManifest.xml" not in names or "resources.arsc" not in names:
                raise ValueError("Input is not a complete Android APK")

            manifest_hash = hashlib.sha256(
                source.read("AndroidManifest.xml")
            ).digest()
            resources_hash = hashlib.sha256(
                source.read("resources.arsc")
            ).digest()

            with zipfile.ZipFile(
                temporary_path, "w", allowZip64=True
            ) as destination:
                destination.comment = source.comment

                for info in source.infolist():
                    filename = info.filename
                    if is_v1_signature(filename):
                        signature_files_removed.append(filename)
                        continue

                    data = source.read(info)
                    if is_locale_cache(filename):
                        cache_count += 1
                        try:
                            parsed = json.loads(data.decode("utf-8"))
                        except (UnicodeDecodeError, json.JSONDecodeError) as error:
                            raise ValueError(
                                f"Invalid JSON locale cache: {filename}"
                            ) from error

                        if not isinstance(parsed, dict):
                            raise ValueError(
                                f"Locale cache is not a JSON object: {filename}"
                            )

                        locale = locale_from_cache_name(filename)
                        if locale not in keep and data != b"{}":
                            original_compressed_bytes += info.compress_size
                            replaced_names.add(filename)
                            replaced_by_locale[locale] = (
                                replaced_by_locale.get(locale, 0) + 1
                            )
                            data = b"{}"

                    cloned_info = copy.copy(info)
                    destination.writestr(cloned_info, data)

        if cache_count == 0:
            raise ValueError("No compiled locale cache resources found")

        with zipfile.ZipFile(temporary_path, "r") as result:
            if len(result.infolist()) != expected_entry_count:
                raise ValueError("ZIP entry count changed unexpectedly")

            for filename in replaced_names:
                if result.read(filename) != b"{}":
                    raise ValueError(f"Locale cache replacement failed: {filename}")

            if hashlib.sha256(
                result.read("AndroidManifest.xml")
            ).digest() != manifest_hash:
                raise ValueError("AndroidManifest.xml changed unexpectedly")
            if __import__("hashlib").sha256(
                result.read("resources.arsc")
            ).digest() != resources_hash:
                raise ValueError("resources.arsc changed unexpectedly")

            new_compressed_bytes = sum(
                info.compress_size
                for info in result.infolist()
                if info.filename in replaced_names
            )

        os.replace(temporary_path, destination_path)

        return {
            "input": str(source_path),
            "output": str(destination_path),
            "kept_locales": sorted(keep),
            "locale_cache_entries": cache_count,
            "replaced_entries": len(replaced_names),
            "replaced_by_locale": dict(sorted(replaced_by_locale.items())),
            "signature_files_removed": signature_files_removed,
            "original_compressed_bytes": original_compressed_bytes,
            "new_compressed_bytes": new_compressed_bytes,
            "compressed_bytes_saved": original_compressed_bytes - new_compressed_bytes,
            "output_is_unsigned": True,
        }
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input APK")
    parser.add_argument("--output", required=True, help="Output unsigned APK")
    parser.add_argument(
        "--keep-locales",
        default="enGB,id",
        help="Comma-separated locale tags to preserve (default: enGB,id)",
    )
    parser.add_argument(
        "--summary",
        help="Optional path for a JSON summary report",
    )
    args = parser.parse_args()

    keep = [value.strip() for value in args.keep_locales.split(",") if value.strip()]
    if not keep:
        parser.error("--keep-locales must contain at least one locale")

    summary = trim_apk(args.input, args.output, keep)
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.summary:
        summary_path = Path(args.summary)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
