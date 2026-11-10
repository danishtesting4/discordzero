# Nitro expansion — Discord 352.17 / Hermes bytecode 98

## Baseline
- Discord Android: **352.17** (arm64 analysis baseline from source run `42805321472`, inspect run `42817891856`).
- Hermes bytecode: **HBC 98** (Modern).
- Branch: `nitro-expansion-35217` (from `3376bf9`, 2026-11-10).
- Pipeline: Reseam Hermes patching (`app.reseam.workspace` 0.39.1) → locale-cache trim (`scripts/trim_locale_caches.py`) → zipalign/sign/apksigner verify via `.github/workflows/test-unbloat.yml`.
- Constraint: CI/build/signature success is not runtime correctness. Priority 1 runtime checks and Nitro runtime checks remain release gates.

## Existing Nitro coverage (already implemented)
`patches/apps/discord/patch/src/main/kotlin/app/discordzero/patches/discord/DiscordZero.kt` — `removeNitroPromotions` (strict 7-param Metro module-factory match by embedded source path; hide exact exports via `Features.hideExport`):
- `modules/premium/roadblocks/native/views/PremiumFeatureUpsell.tsx` → `default`
- `modules/premium/roadblocks/native/views/PremiumExpressionPickerFeatureUpsell.tsx` → `default`
- `modules/premium/roadblocks/native/views/PremiumExpressionPickerSearchUpsell.tsx` → `default`
- `modules/emoji_picker/native/components/EmojiPickerPremiumSearchUpsell.tsx` → `PremiumSearchUpsell`
- `modules/stickers/native/StickerPickerPremiumSearchUpsell.tsx` → `default`

Prior validation (per `docs/unbloat-research.md`): `removeNitroPromotions` applied in successful arm64 test builds (e.g. 42813479215, 42815156797, 42815357405). No device/runtime proof of absence/regression recorded.

## Priority 2 candidates investigated

### 1) File-upload Nitro announcement/upsell hooks
- **80867 `useNitroFileUploadAnnouncementEligible`** (decomp `function-80867-nitro_file_upload_announcement_eligible.js`, inspect 42817891856): calls `useIsPremiumSubscriber(TIER_2)` and, if subscriber, `useNitroFileUploadRolloutEnabled(arg0)`; returns that gated result. Hook-preserving final-result change is plausible but depends on all call contexts.
- **80869 `useNitroFileUploadUpsellEligible`** (decomp `function-80869-nitro_file_upload_upsell_eligible.js`): calls `useIsPremiumSubscriber(TIER_2)` and `useNonNitroFileUploadMarketingEnabled(arg0)`; returns `marketingEnabled && !isPremiumSubscriber`.
- **80868 / 80870:** React Compiler/fallback counterparts not individually traced to unique module-factory/export anchors in current artifact; pair/ownership must be proven before patching.
- **Owning module factory / export / embedded source path:** **not yet identified** in available inspect artifacts (no `fileFinishedImporting`/module path evidence for these hooks in decompiled targets). Component/function IDs alone are insufficient for the repo’s module-export patching convention.
- **Callers/contexts:** not fully enumerated from current artifacts (xref query files for hook names not present in downloaded 42817891856 extract; hook xrefs not conclusively mapped). File-upload promo/rollout copy is referenced by offer sheets (76221/22, 80833/34 use `getNitroFileUploadRolloutCopy`), indicating file-upload Nitro messaging is integrated into multiple surfaces.
- **Risk:** altering eligibility could suppress announcements/upsells but may also affect upload-limit messaging or marketing-gated UI in ways not yet proven safe. Must preserve hook execution and must not change actual upload enforcement.
- **Status:** **Investigated, deliberately not patched.** Requires unique module-factory/export evidence, caller/context trace, and runtime validation.

### 2) File-upload Nitro upsell promo sheet
- **80858 / 80859 `NitroFileUploadUpsellPromoSheet`** (decomp `function-80858-nitro_file_upload_upsell_promo_sheet.js`, `function-80859-nitro_file_upload_upsell_sheet_80859.js`): promo/action-sheet UI that tracks dismiss/take-action reasons, can navigate to Premium settings (`openUserSettings` screen `PREMIUM`) on CTA, renders file-upload spot illustration and Nitro/premium upsell copy.
- **80857 label:** inspect target `nitro_file_upload_upsell_module` decompiles to `FileUploadSpotIllustration` / upload-upsell-related UI fragment in current artifact naming, not a confirmed module factory with embedded path.
- **Owning module factory / export / embedded source path:** **not identified** in available artifacts.
- **Callers/contexts:** not fully enumerated. Promo nature is likely, but triggering context (normal upload, large file, over-limit, announcement flow) must be proven to ensure suppression does not remove required error/limit UX.
- **Status:** **Investigated, deliberately not patched.** Blocked on module-factory/path/export/caller proof and upload-flow safety validation.

### 3) Premium trial offer action sheet
- **76221 / 76222 `PremiumTrialOfferActionSheetContent`** (decomp `function-76221-premium_trial_offer_sheet.js`, `function-76222-premium_trial_offer_sheet_76222.js`): renders trial-offer marketing content (Nitro trial perks/CTA, `getNitroFileUploadRolloutCopy` for file-upload perk copy, `NitroWumpusFlightRight3dIllustration`, confirm/dismiss handlers). Explicitly offer-driven UI.
- **Owning module factory / export / embedded source path:** **not identified**.
- **Callers/contexts:** `usePremiumTrialOffer` / trial/discount data are consumed in broader premium upsell surfaces (e.g. decomp refs in `52244/52245/52256/52257`), but the specific module exporting/calling `PremiumTrialOfferActionSheetContent` (76221/22) is not uniquely traced here. May be offer-only sheet content, but shared plumbing risk must be ruled out.
- **Risk:** removing an offer sheet is likely promotional, but could affect legitimate trial redemption entry points if this component is the only path in a given flow (unproven).
- **Status:** **Investigated, deliberately not patched.** Pending module-factory/export/caller evidence.

### 4) Premium discount offer action sheet
- **80833 / 80834 `PremiumDiscountOfferActionSheetContent`** (decomp `function-80833-premium_discount_offer_sheet.js`, `function-80834-premium_discount_offer_sheet_80834.js`): renders discount-offer marketing content (percentage/CTA/perks, `getNitroFileUploadRolloutCopy`), analogous to trial sheet.
- **Owning module factory / export / embedded source path:** **not identified**.
- **Callers/contexts:** `usePremiumDiscountOffer` appears in broader upsell config/sheets (e.g. 52256 refs), but specific 80833/34 export/caller chain not uniquely traced.
- **Status:** **Investigated, deliberately not patched.** Pending module-factory/export/caller evidence.

### Other inspected (lower confidence / deferred)
- Generic/profile/shop/group-DM Nitro upsell modules/components present in artifact (`NitroUpsell*`, `NitroUpsellButton*`, `PremiumUpsellAlert*`, `72448/49`, `72580/81`, `72705/06`, `76739/40`, `79987/88`, `52256/57`, etc.) remain **not patched** in this pass: higher chance of shared/product-adjacent contexts (profile customization, shop, group-DM limits/features, subscription/account surfaces) and/or ambiguous targets. No caller-complete, promo-only proof established.

## Reproducibility / inspection workflow changes
- Extended `.github/workflows/inspect-discord-bundle.yml` xref queries for Nitro file-upload/offer tracing: `useNitroFileUploadRolloutEnabled`, `useNonNitroFileUploadMarketingEnabled`, `getNitroFileUploadRolloutCopy`, `NitroFileUploadUpsellPromoSheet`, `PremiumTrialOfferActionSheetContent`, `PremiumDiscountOfferActionSheetContent`, `PremiumTrialOfferActionSheet`, `PremiumDiscountOfferActionSheet`.
- **Inspect run triggered:** _TBD in final report (see workflow runs)._

## Changes implemented
- **None in this pass.** No new Reseam patches added to `DiscordZero.kt` / `Features` JS because no Priority 2 candidate met the required evidence bar (unique owning module factory + embedded source path + export + caller/context proof of promo-only safety, including upload/subscription/account non-regression).

## Candidates deliberately left untouched (and why)
| Candidate | Reason |
|---|---|
| 80867–80870 file-upload announcement/upsell eligibility hooks | Owning module factory/export/path and full caller contexts not uniquely proven; risk to upload/marketing-gated UX if mis-targeted. |
| 80857–80859 file-upload upsell promo sheet/illustration | No unique module-factory/source-path/export evidence; triggering contexts and upload-error non-regression unproven. |
| 76220–76222 premium trial offer sheet | No unique module-factory/source-path/export evidence; redemption/entry-point impact unproven despite promo content. |
| 80832–80834 premium discount offer sheet | No unique module-factory/source-path/export evidence; same as trial. |
| Profile/shop/group-DM/generic upsell surfaces and shared upsell infrastructure | Callers/contexts not fully traced; potential impact on legitimate purchase/profile/group-DM/entitlement flows; some targets known ambiguous. |

## Validation
- **Automated tests / `test-unbloat` / `python-checks`:** _TBD in final report._
- **Patch application logs (unique match/apply):** N/A (no new Nitro patches).
- **APK size comparison:** N/A (no new patched build produced by code change in this pass beyond any CI runs recorded below). Do not claim meaningful size savings without measurements.

## Remaining runtime validation requirements (release gates)
**Priority 1 (Discovery), still outstanding:** invite deep links/codes, create-server, redirected Discovery routes/back navigation, login/messaging/uploads/notifications/voice.
**Priority 2 (Nitro), when patches exist:** normal/large/over-limit file uploads; Nitro/subscription settings; gifts/perks/account flows; emoji/sticker behavior; core Discord functionality. CI success is not runtime proof.
