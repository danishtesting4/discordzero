import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.download_base_apk import (
    MIRRORS,
    build_mirror_urls,
    validate_apk,
    validate_version,
)


class DownloaderTests(unittest.TestCase):
    def test_mirror_order_and_duplicate_removal(self):
        urls = list(build_mirror_urls("352006"))
        self.assertEqual([name for name, _ in urls], ["tracker", "vendetta-proxy", "k6", "nexpid"])
        self.assertEqual(len({url for _, url in urls}), 4)
        self.assertTrue(urls[0][1].endswith("/tracker/download/352006/base"))

    def test_rejects_path_injection_in_version(self):
        for value in ("../latest", "352006?x=1", "352006/base", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_version(value)

    def test_accepts_version_with_dot(self):
        self.assertEqual(validate_version("352.6"), "352.6")

    def test_validates_apk_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            apk_path = Path(directory) / "base.apk"
            with zipfile.ZipFile(apk_path, "w") as apk:
                apk.writestr("AndroidManifest.xml", b"manifest")
                apk.writestr("classes.dex", b"dex")
            validate_apk(apk_path)

    def test_rejects_zip_without_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            apk_path = Path(directory) / "not-an-apk.zip"
            with zipfile.ZipFile(apk_path, "w") as archive:
                archive.writestr("readme.txt", b"not an apk")
            with self.assertRaises(ValueError):
                validate_apk(apk_path)

    def test_rejects_non_zip_response(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "bad.apk"
            file_path.write_bytes(b"<html>rate limited</html>")
            with self.assertRaises(ValueError):
                validate_apk(file_path)


if __name__ == "__main__":
    unittest.main()
