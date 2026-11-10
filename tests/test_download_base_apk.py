import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

import scripts.download_base_apk as downloader


class DownloaderTests(unittest.TestCase):
    def test_display_version_is_converted_to_tracker_version_code(self):
        self.assertEqual(downloader.normalize_tracker_version("352.17"), "352017")
        self.assertEqual(downloader.normalize_tracker_version("352.6"), "352006")
        self.assertEqual(downloader.normalize_tracker_version("352017"), "352017")

    def test_current_valenced_mirror_order(self):
        urls = list(downloader.build_mirror_urls("352.17"))
        self.assertEqual(
            [name for name, _ in urls],
            ["ushie-proxy", "vendetta-tracker"],
        )
        self.assertEqual(len({url for _, url in urls}), 2)
        self.assertTrue(urls[0][1].startswith("https://proxy.vd.ushie.dev/"))
        self.assertTrue(urls[1][1].startswith("https://tracker.vendetta.rocks/"))
        self.assertTrue(urls[0][1].endswith("/tracker/download/352017/base"))

    def test_can_prefer_vendetta_tracker(self):
        urls = list(
            downloader.build_mirror_urls(
                "352.17", preferred_mirror="vendetta-tracker"
            )
        )
        self.assertEqual(
            [name for name, _ in urls],
            ["vendetta-tracker", "ushie-proxy"],
        )

    def test_builds_split_url(self):
        urls = list(downloader.build_mirror_urls("352.17", "config.arm64_v8a"))
        self.assertTrue(
            urls[0][1].endswith("/tracker/download/352017/config.arm64_v8a")
        )

    def test_rejects_path_injection(self):
        for version, split in (
            ("../latest", "base"),
            ("352017?x=1", "base"),
            ("352006", "../base"),
            ("352006", "base?x=1"),
            ("", "base"),
        ):
            with self.subTest(version=version, split=split):
                with self.assertRaises(ValueError):
                    list(downloader.build_mirror_urls(version, split))

    def test_validates_apk_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            apk_path = Path(directory) / "base.apk"
            with zipfile.ZipFile(apk_path, "w") as apk:
                apk.writestr("AndroidManifest.xml", b"manifest")
                apk.writestr("classes.dex", b"dex")
            downloader.validate_apk(apk_path)

    def test_rejects_zip_without_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            apk_path = Path(directory) / "not-an-apk.zip"
            with zipfile.ZipFile(apk_path, "w") as archive:
                archive.writestr("readme.txt", b"not an apk")
            with self.assertRaises(ValueError):
                downloader.validate_apk(apk_path)

    def test_rejects_non_zip_response(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "bad.apk"
            file_path.write_bytes(b"<html>rate limited</html>")
            with self.assertRaises(ValueError):
                downloader.validate_apk(file_path)

    def test_cycles_to_next_mirror_after_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "base.apk"
            calls = []

            def fake_download(url, destination, timeout):
                calls.append(url)
                if len(calls) == 1:
                    raise urllib.error.URLError("simulated timeout")
                with zipfile.ZipFile(destination, "w") as apk:
                    apk.writestr("AndroidManifest.xml", b"manifest")

            with patch.object(
                downloader, "download_from_url", side_effect=fake_download
            ):
                mirror, digest, size = downloader.download_split(
                    "352.17", "base", output
                )

            self.assertEqual(mirror, "vendetta-tracker")
            self.assertEqual(len(calls), 2)
            self.assertTrue(output.is_file())
            self.assertEqual(size, output.stat().st_size)
            self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
