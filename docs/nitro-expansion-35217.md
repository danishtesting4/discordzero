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
- Extended inspect decompile targets for candidate module factories/related functions: `18456`, `17093`, `18435`, `17092`, `18434`, `18461`, `5065`, `68181/68182`, `80861/80862`.
- Added xref queries for generic upsell/component tracing: `NitroUpsell`, `NitroUpsellButton`, `PremiumUpsellAlert`, `NitroUpsell.tsx`, `NitroUpsellButton.tsx`, `PremiumUpsellAlert.tsx`, `useNitroFileUploadAnnouncement`, `useNitroFileUploadUpsell`.
- Inspect runs: `42825621961` (success) — https://github.com/danishtesting4/discordzero/actions/runs/42825621961; `42826462840` (success) — https://github.com/danishtesting4/discordzero/actions/runs/42826462840; `42829316421` (success, eligibility/experiment/generic-target decompiles) — https://github.com/danishtesting4/discordzero/actions/runs/42829316421. (A redundant workflow_dispatch run `42829335278` was also triggered: https://github.com/danishtesting4/discordzero/actions/runs/42829335278.)

## Evidence from inspect runs 42825621961 / 42826462840 / 42829316421
- `xref-getNitroFileUploadRolloutCopy.txt` (42825621961): 7 refs — `5065`, `68181/68182` FractionalNitroPreview, `76221/76222`, `80833/80834`.
- `xref-NitroFileUploadUpsellPromoSheet.txt`: **1 ref** → function `18456` (LoadConstStringLongIndex @ 0x0115). Decomp (42826462840) confirms unique 7-param Metro module factory `modules/premium/file_upload/native/NitroFileUploadUpsellPromoSheet.tsx` exporting `default` component (React Compiler/fallback pair `F80858`/`F80859`, component bodies `80858/80859` in prior decomp). Promo sheet navigates to Premium settings on CTA and tracks dismiss/take-action; not upload enforcement logic.
- `xref-PremiumTrialOfferActionSheetContent.txt`: **1 ref** → function `17093` (content module factory `modules/premium/native/trials/PremiumTrialOfferActionSheetContent.tsx`, memoized default from `F76221`/`F76222`). Not patched directly.
- `xref-PremiumDiscountOfferActionSheetContent.txt`: **1 ref** → function `18435` (content module factory `modules/premium/native/discounts/PremiumDiscountOfferActionSheetContent.tsx`, memoized default from `F80833`/`F80834`). Not patched directly.
- `xref-PremiumTrialOfferActionSheet.txt`: refs in `17092/17093/18461`, `80861/80862` (`useMainViewTooltipActionSheetMap`), `129085/129086` press handlers. Decomp of `17092` confirms module factory `modules/premium/native/trials/PremiumTrialOfferActionSheet.tsx` exporting `default` wrapper action sheet (`F76220`, body `76220` renders BottomSheet with trial offer content); `18461` is kill-switch experiment module (`PremiumTrialOfferActionSheetKillSwitchExperiment`), referenced by 80861/80862.
- `xref-PremiumDiscountOfferActionSheet.txt`: refs in `18434/18435`. Decomp of `18434` confirms module factory `modules/premium/native/discounts/PremiumDiscountOfferActionSheet.tsx` exporting `default` wrapper action sheet (`F80832`).
- **File-upload experiments module (42829316421):** `5065` is 7-param module factory `modules/premium/experiments/NitroFileUploadExperiments.tsx` (`fileFinishedImporting` present). Exports: `getNitroFileUploadLimitBytes` (F33548) → returns 1GB tier-2 limit if rollout config enabled else standard tier-2 limit (**affects actual upload limits**), `getNitroFileUploadRolloutConfig` (F33543), `getNitroFileUploadRolloutCopy` (F33549), `useNitroFileUploadRolloutEnabled` (F33544/F33545, compiler/fallback), `useNonNitroFileUploadMarketingEnabled` (F33546/F33547). Experiments: `2026-09-nitro-file-upload-rollout` and `2026-09-non-nitro-file-upload-marketing` (default disabled). **Must not be patched to disable rollout/limits.**
- **Eligibility hooks (42829316421):** `80867` and `80868` (alt) both decompile to identical `useNitroFileUploadAnnouncementEligible(arg0)` logic: premium subscriber && `useNitroFileUploadRolloutEnabled(arg0)` (announcement eligibility, rollout-gated for premium). `80869` and `80870` (alt) both decompile to identical `useNitroFileUploadUpsellEligible(arg0)` logic: `useNonNitroFileUploadMarketingEnabled(arg0) && !premiumSubscriber` (non-premium marketing upsell). Hook names not found as xref string hits in extracted reports despite queries; only function bodies decompiled. **Owning module factories, embedded source paths, exports, and all callers/contexts not identified.** Cannot confirm these hooks are used exclusively for promotional visibility (vs any required upload/error UX) without caller trace.
- **Generic Nitro upsell components:** `NitroUpsell` (68204/68205), `NitroUpsellButton` (53877/53878), `PremiumUpsellAlert` (52970/52971) component bodies decompiled, but **module factories/source paths/exports not found** in current decomp set; inspect "module" targets 68203/53876/52969 decompiled to unrelated functions (OrbsPriceTag, getStickerDiscoverableGuild, UploadUpsell with extra-compression UI) — labels misleading. No complete caller/context proof of exclusively promotional usage. Not patched.

## Changes implemented (this pass)
Reseam patches added in `patches/apps/discord/patch/src/main/kotlin/app/discordzero/patches/discord/DiscordZero.kt` using existing `Features.hideExport` (strict 7-param module-factory match, embedded source path, exact `default` export suppression):

| Patch | Module factory (ID, source path) | Export | Component(s) | Evidence / safety notes |
|---|---|---|---|---|
| `removeNitroOfferSheets` | `17092` `modules/premium/native/trials/PremiumTrialOfferActionSheet.tsx` | `default` | wrapper `F76220` (76220) presenting trial offer content `F76221/76222` | Unique single-site component-name/content wiring via 17093; trial refs in action-sheet map/kill-switch/press handlers indicate promo offer sheet. Promotional trial offer UI; does not target subscription management, purchases, account features, or entitlement checks. **Runtime validation required** (offer display/removal, subscription/account flows). |
| `removeNitroOfferSheets` | `18434` `modules/premium/native/discounts/PremiumDiscountOfferActionSheet.tsx` | `default` | wrapper `F80832` (80832) presenting discount offer content `F80833/80834` | Unique xref to 18435 content module; discount offer promo sheet. Same constraints as trial. **Runtime validation required.** |
| `removeNitroFileUploadPromo` | `18456` `modules/premium/file_upload/native/NitroFileUploadUpsellPromoSheet.tsx` | `default` | `F80858`/`F80859` (80858/80859) | Single xref to module; decomp shows Nitro upsell promo CTA to Premium settings (not upload-size enforcement/error handling). **Promo-only removal intended; must not affect actual file upload/limits.** **Runtime validation required** (normal/large/over-limit uploads, absence of promo sheet). |

**Not patched:** content modules `17093`/`18435` (wrapper suppression preferred/clearer), hook-based eligibility `80867-80870` (module/export/caller proof incomplete).

## Candidates deliberately left untouched (and why)
| Candidate | Reason |
|---|---|
| 80867/80868 `useNitroFileUploadAnnouncementEligible` (compiler/fallback) | **Bodies proven identical** (80867=80868): eligible for premium subscriber when rollout enabled. Rollout (`5065`/33548) controls **actual upload limit bytes** (1GB vs standard), so rollout/experiment hooks must not be suppressed. Announcement hooks may be promo-only, but **owning module factory, embedded source path, export name, and all callers/contexts are not identified** (no xref string hits, not exported from 5065/18456). Cannot prove suppression affects only promo visibility and not required upload/announcement UX; no unique safe Reseam target. |
| 80869/80870 `useNitroFileUploadUpsellEligible` (compiler/fallback) | **Bodies proven identical** (80869=80870): non-premium marketing upsell (`useNonNitroFileUploadMarketingEnabled && !premiumSubscriber`). Same **missing ownership/export/caller evidence**; cannot prove all uses are promotional-only or safely suppressible without affecting upload flows/required UX. |
| 5065 Nitro file-upload experiments module | `modules/premium/experiments/NitroFileUploadExperiments.tsx` exports limit/rollout config and experiment hooks; **directly affects upload limits/copy/experiments**. Not a promo-only removal target. |
| NitroUpsell (68204/68205), NitroUpsellButton (53877/53878), PremiumUpsellAlert (52970/52971) | Component bodies decompiled but **module factories/source paths/exports/callers not established**; inspect "module" target labels misleading (68203/53876/52969 mapped to unrelated functions). Cannot prove exclusively promotional or uniquely patchable. |
| 80857, 17093, 18435, 76220-76222/80832-80834 component/content IDs as alternate targets | Safer/clearer module-factory targets (`18456`, `17092`, `18434`) already patched or analyzed; no additional safe target warranted. |
| Profile/shop/group-DM/generic upsell surfaces and shared upsell infrastructure | Callers/contexts not fully traced; potential impact on legitimate purchase/profile/group-DM/entitlement flows; ambiguous targets. |

## Validation (CI, 352.17 arm64)
- **`test-unbloat.yml` run 42827307328 (success):** https://github.com/danishtesting4/discordzero/actions/runs/42827307328  
  - Commit: `2a9f21b` (`nitro-expansion-35217`)
  - Source APK artifact: `discordzero-352.17-arm64-v8a` from run `42805321472`
  - Reseam bundle build/list: OK (`discordzero.reseam`, 34,389 bytes in artifact)
  - **Patch application:** 7 patches applied, 0 failed/skipped/dependencies/unmountable (`patch application finished`, `applied=7 ... failed=0`). Explicitly applied: `staticChatMedia`, `staticProfileMedia`, `disableDiscoveryRoutes`, `disableServerDiscovery`, `removeNitroPromotions`, **`removeNitroOfferSheets`**, **`removeNitroFileUploadPromo`**.
  - **Locale trim:** `locale_cache_entries=2097`, `replaced_entries=1187`, `kept_locales=[enGB,id]`, `compressed_bytes_saved=7,137,052`, `new_compressed_bytes=4,498`, `output_is_unsigned=true` (same locale result as prior validated baseline).
  - **Packaging/signing:** zipalign, apksigner sign, apksigner verify, APK verification steps completed successfully (workflow green).
- **Local repository tests:** `tests/test_download_base_apk.py`, `tests/test_trim_locale_caches.py` **not run locally** (no `python`/`py` interpreter found in PATH in this environment). No changes were made to downloader/locale-trim scripts or their tests in this pass.
- **Patch match uniqueness:** enforced by Reseam/module-factory matching in workflow; no missing/non-unique match errors reported and all selected patches applied.

## APK size comparison (arm64, 352.17)
| Build | Size (bytes) | Notes |
|---|---:|---|
| Original source APK (build-abi artifact, run 42805321472 baseline) | 201,231,604 | From prior documented baseline (`docs/unbloat-research.md`) |
| Prior unbloat test APK (run 42815156797) | 194,735,426 | Included locale trim + earlier patches |
| This pass unbloat test APK (run 42827307328) | 194,743,618 | Artifact `discordzero-352.17-arm64-unbloat-test` (98,862,426 bytes compressed zip artifact; APK 194,743,618 bytes) |
| Delta vs prior unbloat test | +8,192 | **Not meaningful storage savings**; attributable to patch/bundle/packaging differences. No resource trimming beyond existing locale cache trim. |

## Remaining runtime validation requirements (release gates)
**Priority 1 (Discovery), still outstanding:** invite deep links/codes, create-server, redirected Discovery routes/back navigation, login/messaging/uploads/notifications/voice.
**Priority 2 (Nitro), when patches exist:** normal/large/over-limit file uploads; Nitro/subscription settings; gifts/perks/account flows; emoji/sticker behavior; core Discord functionality. CI success is not runtime proof.
