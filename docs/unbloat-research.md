# DiscordZero unbloat research

## Inspected build

- Discord Android: 352.17
- Hermes bytecode: HBC 98, modern layout
- Hermes functions: 163,874
- Hermes strings: 349,546
- APK base commit: Discord bundle manifest reported commit `a295fd2ccb8cbe76e19e2c651ee2f9a3be48237f`
- Reference run: https://github.com/danishtesting4/discordzero/actions/runs/42808897409

Function IDs below are from this exact 352.17 bundle. They are investigation leads, not approved patch targets. Re-check names, signatures, bodies, and uniqueness before adding a patch.

## Candidate behaviour targets

| Area | Function IDs and names | What to verify |
| --- | --- | --- |
| GIF/media autoplay | `54776 useAutoPlay` | Whether this is the central autoplay decision and what settings it respects |
| Reduced motion | `71773 setPrefersReducedMotion` | Whether this updates a global preference or only reports a setting |
| Nitro file-upload announcement | `80867/80868 useNitroFileUploadAnnouncementEligible` | Whether returning false only suppresses promotional UI |
| Nitro file-upload upsell | `80869/80870 useNitroFileUploadUpsellEligible` | Whether returning false only suppresses the upsell |
| Nitro upsell button | `53877/53878 NitroUpsellButton` | Component boundaries and callers |
| Nitro upsell surface | `68204/68205 NitroUpsell` | Component boundaries and callers |
| Premium upsell alert | `52970/52971 PremiumUpsellAlert` | Whether this is promotional-only |
| File-upload promo sheet | `80858/80859 NitroFileUploadUpsellPromoSheet` | Whether this can be suppressed without affecting upload errors |
| Trial offer | `76221/76222 PremiumTrialOfferActionSheetContent` | Offer-only UI and call sites |
| Discount offer | `80833/80834 PremiumDiscountOfferActionSheetContent` | Offer-only UI and call sites |
| Profile banner | `48469/48470 UserProfileBanner` | Animated banner rendering and autoplay gates |
| Banner preload | `48251 preloadUserBannerImage` | Whether preloading can be skipped when off-screen |
| Avatar decoration | `48142/48143 useUserAvatarDecoration`, `25773/25774 avatarDecoration`, `25837 getAvatarDecorationURL` | Static display vs animation; preserve profile editing |
| Avatar rendering | `48497/48498 HeaderAvatar`, `66894/66895 UserAvatar`, `70989/70990 Avatar` | Decoration and animation props passed through |
| Discovery | `64670/64671 ApplicationCommandDiscovery`, `84048 getGlobalDiscoveryServersBannerTitle`, `84053 fromDiscoverableGuildServer` | Whether these belong to the user-facing discovery surfaces |

## Decompiled behaviour confirmed

- `setPrefersReducedMotion` dispatches Discord's accessibility action. When reduced motion becomes enabled, it applies settings overrides: `gifAutoPlay=false`, `animateEmoji=false`, and `animateStickers=ANIMATE_ON_INTERACTION`.
- `UserProfileBanner` reads the GIF autoplay setting and uses it to choose whether the banner URL may animate. It also has a manual animation toggle, so the still-by-default behaviour can preserve manual playback.
- `getAvatarDecorationURL` explicitly chooses `STATIC` or `ANIMATED` assets from its `canAnimate` argument. Forcing that argument to false keeps the decoration's static art instead of removing the decoration.
- `preloadUserBannerImage` uses the same GIF autoplay setting when selecting banner URLs. With reduced motion enabled, it can preload the static banner.
- `useNitroFileUploadUpsellEligible` calls both premium-subscription and marketing-eligibility hooks, then returns the marketing result. The patch changes the final result only, preserving hook calls.
- `useNitroFileUploadAnnouncementEligible` similarly calls its hooks before returning its eligibility result; the patch changes only the final result.
- `useAutoPlay` is a generic animation/carousel control hook, not the global GIF autoplay setting. Leave it untouched.
- `ApplicationCommandDiscovery` is slash-command discovery, not the server-discovery screen. Do not patch it as a substitute for removing server discovery.

## Storage audit

From the arm64 352.17 APK:

- Translation cache entries under `res/raw/cache_intl_*`: 7,359,824 compressed bytes across all locales.
- Keeping the English (UK) cache and the tiny Indonesian entry would leave 216,596 compressed bytes; the theoretical difference is 7,143,228 bytes (~6.81 MiB).
- Resource paths containing premium, upsell, Nitro, decoration, banner, and related terms total about 5,538,691 compressed bytes. This is only a name-based candidate set, not a safe deletion list.
- The Hermes bundle is about 67.14 MiB and is stored uncompressed. Do not remove or recompress it without a tested loader change.
- Voice/audio native libraries and media assets remain protected until their references are understood.

No resources have been deleted. Resource-table references and locale fallback must be validated before storage trimming is enabled.

## Implementation direction

Use Reseam's native Hermes hooks for JavaScript behaviour changes. This edits the bundled Hermes bytecode directly and avoids adding a runtime Xposed module solely for these features. Keep patch targets exact and fail the build if a target is missing or ambiguous.

Planned build flow:

`Download splits → Merge ABI → Reseam patch → Align/sign → Verify → Upload`

Do not publish stock or partially patched APKs as DiscordZero releases.

## Patch validation notes

- The Reseam bundle builds successfully with engine/plugin 0.39.1 and generated Hermes extension bindings.
- The `createMessageContent` target resolves in Discord 352.17. The test run reached the later Nitro patch and reported no failure for the chat-media patch; it is therefore the first validated code target.
- The chat-media extension copies the message props and sets `options.gifAutoPlay=false` and `options.animateEmoji=false`, leaving the original props unmodified.
- The initial `setPrefersReducedMotion` target did not resolve in Reseam's function matcher, so it was removed rather than shipping an unverified hook.
- `PremiumFeatureUpsellPill` has two same-named React Compiler/fallback functions in this bundle. Reseam's `function` query requires exactly one match, so this target cannot be patched with the current broad selector. Inspect the parent picker surfaces or a shared helper instead.
- No partially patched APK has been published. The test workflow is intentionally strict: if a selected patch fails, it produces no APK.

## First successful arm64 test build

- Run: `42813479215`; artifact: `discordzero-352.17-arm64-unbloat-test` (expires 2026-11-17).
- Reseam logged both `staticChatMedia` and `removeNitroPromotions` as `patch applied`.
- The APK passed the workflow's package, alignment, signature and APK verification steps.
- The module-export approach avoids the duplicate React Compiler/fallback function match: patch the seven-argument Metro module factory by its embedded source path, then replace the relevant export on `param(5)` (the module exports object).
- Original arm64 APK: 201,231,604 bytes. Patched test APK: 200,986,267 bytes. This small difference is signing/packaging overhead, **not meaningful storage trimming**.
- The Hermes bundle grew from 70,404,633 to 71,062,701 bytes because the patch extension is embedded. Resource and locale trimming has not been implemented yet.

## Locale trimming validation

- The Python checks pass for `scripts/trim_locale_caches.py`.
- The script parses each `res/raw/cache_intl_*` compiled-message cache as JSON, keeps `enGB` and `id`, and replaces non-kept non-empty locale objects with `{}`. It preserves resource names/IDs, `resources.arsc`, and `AndroidManifest.xml`; the APK is re-aligned and re-signed afterward.
- On Discord 352.17 arm64, it processed 2,097 cache entries and replaced 1,187 non-empty entries across 29 non-kept locales.
- Compressed locale resources fell from 7,141,550 bytes to 4,498 bytes, saving 7,137,052 bytes.
- Successful integrated test: run `42815156797`, artifact `discordzero-352.17-arm64-unbloat-test` (expires 2026-11-17).
- Final test APK size: 194,735,426 bytes, versus 201,231,604 bytes for the original arm64 APK — 6,496,178 bytes smaller overall after patching, ZIP rewriting, alignment and signing.
- The build log confirms `staticChatMedia`, `staticProfileMedia`, and `removeNitroPromotions` all applied successfully.
- Locale tradeoff: English US remains the app's base fallback, English UK and Indonesian caches are retained; other languages fall back to English.
