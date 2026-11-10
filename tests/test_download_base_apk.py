import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

import scripts.download_base_apk as downloader


class DownloaderTests(unittest.TestCase):
    def test_mirror_order_and_duplicate_removal(self):
        urls = list(downloader.build_mirror_urls("352006"))
        self.assertEqual(
            [name for name, _ in urls],
            ["tracker", "vendetta-proxy", "k6", "nexpid"],
        )
        self.assertEqual(len({url for _, url in urls}), 4)
        self.assertTrue(urls[0][1].endswith("/tracker/download/352006/base"))

    def test_rejects_path_injection_in_version(self):
        for value in ("../latest", "352006?x=1", "352006/base", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    downloader.validate_version(value)

    def test_accepts_version_with_dot(self):
        self.assertEqual(downloader.validate_version("352.6"), "352.6")

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

            with patch.object(downloader, "download_from_url", side_effect=fake_download):
                mirror, digest, size = downloader.download_base("352006", output)

            self.assertEqual(mirror, "vendetta-proxy")
            self.assertEqual(len(calls), 2)
            self.assertTrue(output.is_file())
            self.assertEqual(size, output.stat().st_size)
            self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
