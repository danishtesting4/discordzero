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
