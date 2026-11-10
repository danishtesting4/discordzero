import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.trim_locale_caches import (
    is_locale_cache,
    locale_from_cache_name,
    normalize_locale,
    trim_apk,
)


class TrimLocaleCachesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "input.apk"
        self.output = self.root / "output.apk"

        with zipfile.ZipFile(self.source, "w", zipfile.ZIP_DEFLATED) as apk:
            apk.writestr("AndroidManifest.xml", b"manifest")
            apk.writestr("resources.arsc", b"resource-table")
            apk.writestr(
                "res/raw/cache_intl_aw50ba_enGBmessages123compiledmessages.jsona",
                json.dumps({"hello": ["Hello"]}).encode(),
            )
            apk.writestr(
                "res/raw/cache_intl_bw9kdwxlcw_frmessages456compiledmessages.jsona",
                json.dumps({"hello": ["Bonjour"]}).encode(),
            )
            apk.writestr(
                "res/raw/cache_intl_zgvzawdu_idmessages789compiledmessages.jsona",
                b"{}",
            )
            apk.writestr("assets/index.android.bundle", b"bundle")
            apk.writestr("META-INF/MANIFEST.MF", b"old-signature")
            apk.writestr("META-INF/androidx.core_core.version", b"1.0")

    def tearDown(self):
        self.temp.cleanup()

    def test_locale_name_parsing(self):
        self.assertEqual(
            locale_from_cache_name(
                "res/raw/cache_intl_bw9kdwxlcw_enGBmessagesabccompiledmessages.jsona"
            ),
            "engb",
        )
        self.assertEqual(normalize_locale("en-GB"), "engb")
        self.assertTrue(
            is_locale_cache(
                "res/raw/cache_intl_aw50ba_frmessagesabccompiledmessages.jsona"
            )
        )

    def test_replaces_non_kept_caches_and_preserves_resource_ids(self):
        summary = trim_apk(self.source, self.output, {"enGB", "id"})

        with zipfile.ZipFile(self.source) as original, zipfile.ZipFile(self.output) as trimmed:
            self.assertEqual(
                trimmed.read("res/raw/cache_intl_aw50ba_enGBmessages123compiledmessages.jsona"),
                original.read("res/raw/cache_intl_aw50ba_enGBmessages123compiledmessages.jsona"),
            )
            self.assertEqual(
                trimmed.read("res/raw/cache_intl_zgvzawdu_idmessages789compiledmessages.jsona"),
                b"{}",
            )
            self.assertEqual(
                trimmed.read("res/raw/cache_intl_bw9kdwxlcw_frmessages456compiledmessages.jsona"),
                b"{}",
            )
            self.assertEqual(trimmed.read("AndroidManifest.xml"), b"manifest")
            self.assertEqual(trimmed.read("resources.arsc"), b"resource-table")
            self.assertEqual(trimmed.read("assets/index.android.bundle"), b"bundle")
            self.assertNotIn("META-INF/MANIFEST.MF", trimmed.namelist())
            self.assertIn("META-INF/androidx.core_core.version", trimmed.namelist())

        self.assertEqual(summary["locale_cache_entries"], 3)
        self.assertEqual(summary["replaced_entries"], 1)
        self.assertEqual(summary["replaced_by_locale"], {"fr": 1})
        self.assertTrue(summary["output_is_unsigned"])

    def test_invalid_json_cache_fails_without_output(self):
        with zipfile.ZipFile(self.source, "a", zipfile.ZIP_DEFLATED) as apk:
            apk.writestr(
                "res/raw/cache_intl_aw50ba_deMessagesbadcompiledmessages.jsona",
                b"not-json",
            )

        with self.assertRaisesRegex(ValueError, "Invalid JSON locale cache"):
            trim_apk(self.source, self.output, {"enGB", "id"})
        self.assertFalse(self.output.exists())

    def test_unrecognized_locale_name_fails(self):
        with zipfile.ZipFile(self.source, "a", zipfile.ZIP_DEFLATED) as apk:
            apk.writestr(
                "res/raw/cache_intl_aw50ba_messagesbadcompiledmessages.jsona",
                b"{}",
            )

        with self.assertRaisesRegex(ValueError, "Cannot identify locale"):
            trim_apk(self.source, self.output, {"enGB", "id"})
        self.assertFalse(self.output.exists())

    def test_requires_an_apk_with_locale_caches(self):
        empty = self.root / "empty.apk"
        with zipfile.ZipFile(empty, "w") as apk:
            apk.writestr("AndroidManifest.xml", b"manifest")
            apk.writestr("resources.arsc", b"resource-table")

        with self.assertRaisesRegex(ValueError, "No compiled locale cache"):
            trim_apk(empty, self.output, {"enGB", "id"})


if __name__ == "__main__":
    unittest.main()
