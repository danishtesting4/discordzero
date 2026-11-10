import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_FILE = ROOT / "patches/apps/discord/patch/src/main/kotlin/app/discordzero/patches/discord/DiscordZero.kt"
FEATURES_FILE = ROOT / "patches/apps/discord/extensions/features/src/main/js/index.ts"
TRIM_SCRIPT = ROOT / "scripts/trim_locale_caches.py"
TEST_UNBLOAT = ROOT / ".github/workflows/test-unbloat.yml"
INSPECT_WORKFLOW = ROOT / ".github/workflows/inspect-discord-bundle.yml"
BUILD_ABI_WORKFLOW = ROOT / ".github/workflows/build-abi-apks.yml"


class PatchInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch_src = PATCH_FILE.read_text(encoding="utf-8")
        cls.features_src = FEATURES_FILE.read_text(encoding="utf-8")

    def test_expected_patch_functions_are_declared(self):
        expected = [
            "val staticChatMedia",
            "val staticProfileMedia",
            "val disableDiscoveryRoutes",
            "val disableServerDiscovery",
            "val removeNitroPromotions",
            "val removeNitroOfferSheets",
            "val removeNitroFileUploadPromo",
        ]
        for token in expected:
            with self.subTest(token=token):
                self.assertIn(token, self.patch_src)

    def test_module_factory_targets_are_strict_and_unique_by_path(self):
        # Every module factory target in this file uses a single embedded source path and paramCount(7)
        blocks = re.findall(
            r"private val \w+Module = function \{(.*?)\n\}",
            self.patch_src,
            re.S,
        )
        self.assertGreaterEqual(len(blocks), 10)
        paths = []
        for block in blocks:
            self.assertIn('paramCount(7)', block)
            path_matches = re.findall(r'strings\("([^"]+)"\)', block)
            self.assertEqual(len(path_matches), 1, block)
            paths.append(path_matches[0])
        self.assertEqual(len(paths), len(set(paths)), "module factory source paths must be unique")

    def test_known_promotional_targets_present(self):
        required_paths = {
            "modules/premium/roadblocks/native/views/PremiumFeatureUpsell.tsx",
            "modules/premium/roadblocks/native/views/PremiumExpressionPickerFeatureUpsell.tsx",
            "modules/premium/roadblocks/native/views/PremiumExpressionPickerSearchUpsell.tsx",
            "modules/emoji_picker/native/components/EmojiPickerPremiumSearchUpsell.tsx",
            "modules/stickers/native/StickerPickerPremiumSearchUpsell.tsx",
            "modules/premium/native/trials/PremiumTrialOfferActionSheet.tsx",
            "modules/premium/native/discounts/PremiumDiscountOfferActionSheet.tsx",
            "modules/premium/file_upload/native/NitroFileUploadUpsellPromoSheet.tsx",
            "modules/routing/RouteConstants.tsx",
            "modules/global_discovery_servers/GlobalDiscoveryServersFeaturedSearchManager.tsx",
            "utils/AvatarUtils.tsx",
        }
        for path in sorted(required_paths):
            with self.subTest(path=path):
                self.assertIn(path, self.patch_src)

    def test_hide_export_calls_match_expected_exports(self):
        self.assertIn('Features.hideExport(param(5), string("default"))', self.patch_src)
        self.assertIn('Features.hideExport(param(5), string("PremiumSearchUpsell"))', self.patch_src)
        # Emoji picker promo is the only non-default export suppression
        self.assertEqual(self.patch_src.count('string("PremiumSearchUpsell")'), 1)

    def test_protected_or_risky_targets_not_present(self):
        forbidden = [
            "modules/home_drawer/native/HomeDrawerAddServerRow.tsx",
            "GuildsBarCreateJoinButton",
            "INVITE",
            "GUILD_CREATE",
            "GUILD_DISCOVERY",
            "NitroFileUploadExperiments.tsx",
            "getNitroFileUploadLimitBytes",
            "useNitroFileUploadAnnouncementEligible",
            "useNitroFileUploadUpsellEligible",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, self.patch_src)

    def test_feature_helpers_export_expected_api(self):
        for name in [
            "export function withStaticChatMediaOptions",
            "export function hideExport",
            "export function forceStaticAvatarDecoration",
            "export function disableGifAutoPlay",
            "export function disableDiscoveryManager",
            "export function redirectDiscoveryRoutes",
        ]:
            with self.subTest(name=name):
                self.assertIn(name, self.features_src)

    def test_redirect_routes_preserves_invite_and_guild_create_paths(self):
        # Protected invite/guild-create route keys must not be hardcoded in the redirect helper allowlist
        self.assertNotIn('"INVITE"', self.features_src)
        self.assertNotIn('"INVITE_LOGIN"', self.features_src)
        self.assertNotIn('"INVITE_REGISTER"', self.features_src)
        self.assertNotIn('"INVITE_PROXY"', self.features_src)
        self.assertNotIn('"GUILD_CREATE"', self.features_src)
        self.assertIn('"GLOBAL_DISCOVERY_SERVERS"', self.features_src)
        self.assertIn('"APPLICATION_DIRECTORY"', self.features_src)

    def test_hide_export_failure_behavior_is_conservative(self):
        # hideExport should no-op on invalid inputs rather than throwing
        self.assertRegex(self.features_src, r"if \(exports == null \|\| typeof exports !== \"object\"\) \{\s*return exports;")

    def test_test_unbloat_pipeline_contains_required_steps(self):
        text = TEST_UNBLOAT.read_text(encoding="utf-8")
        required = [
            "reseam patch",
            "scripts/trim_locale_caches.py",
            "zipalign -f -p 4",
            "apksigner sign",
            "apksigner verify --verbose",
            "zipalign -c -p 4",
            "aapt dump badging",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_build_abi_workflow_has_integrity_and_signing_checks(self):
        text = BUILD_ABI_WORKFLOW.read_text(encoding="utf-8")
        required = [
            "a9cd40df818845456be6d696de6110c89edf4b0a0580cb83438ed6b25a366e67",
            "APKEditor-1.4.9.jar",
            "zipalign -f -p 4",
            "apksigner sign",
            "apksigner verify --verbose --print-certs",
            "arm64-v8a", "armeabi-v7a", "x86_64", "x86",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_inspect_workflow_uses_pinned_decompiler(self):
        text = INSPECT_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("hermes-decomp-v0.2.4-linux-x86_64.tar.gz", text)
        self.assertIn("6e070410432575698657b38d3497f66fd91c0c00f63880d6776703d81d99b5ac", text)


if __name__ == "__main__":
    unittest.main()
