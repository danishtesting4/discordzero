# DiscordZero release-readiness audit — 352.17 (HBC 98)

**Branch:** `nitro-expansion-35217` (audit performed on commit `d51ea10` state + audit/test/doc improvements in this pass)  
**Baseline app:** Discord Android 352.17, Hermes bytecode 98 (arm64 analysis/source build `42805321472`)  
**Scope:** current Reseam unbloat patches, CI/packaging/trim/signing evidence, automated test gaps, and manual device-test checklist.  
**Constraint:** no speculative Nitro patches added. CI/build/signature success is **not** runtime correctness. **No device testing was performed.**

## 1. Patch and feature-helper review

### 1.1 Reseam patches (`patches/apps/discord/patch/src/main/kotlin/app/discordzero/patches/discord/DiscordZero.kt`)
All patches are strictly targeted (`compatibleWith("com.discord")`, 7-param Metro module factories matched by a single embedded source-path string, or a uniquely constrained function matcher). Failures/missing/non-unique matches are expected to fail the Reseam patch step.

| Patch | Target(s) | Hook | Export/behavior | Intent / safety notes |
|---|---|---|---|---|
| `staticChatMedia` | `createMessageContent` (name + strings `renderGiftCode`,`animatingStickerMessageId`,`createActivityInstanceEmbed`, `paramCount(1)`) | `before` | Reassigns `param(0)` via `Features.withStaticChatMediaOptions` | Forces chat media options `gifAutoPlay=false`, `animateEmoji=false` (immutable copy). Preserves other props/options. |
| `staticProfileMedia` | `GifAutoPlay`/`gifAutoPlay` settings module factory (`userSettingsModule`) and `utils/AvatarUtils.tsx` (`avatarUtilsModule`) | `after` (exports `param(5)`) | `disableGifAutoPlay`, `forceStaticAvatarDecoration` | Disables GIF autoplay setting getters and forces static avatar-decoration URLs (`canAnimate:false`) while keeping decoration art; manual banner playback intent preserved per prior trace. |
| `disableDiscoveryRoutes` | `modules/routing/RouteConstants.tsx` | `after` | `redirectDiscoveryRoutes` proxies `exports.Routes` | Redirects selected global server/app-discovery and app-directory routes to `/channels/@me`. **Does not include** `INVITE*`, `GUILD_CREATE`, or `GUILD_DISCOVERY` (see §2). |
| `disableServerDiscovery` | `modules/global_discovery_servers/GlobalDiscoveryServersFeaturedSearchManager.tsx` | `after` | `disableDiscoveryManager` on default manager | Disables featured fetch/connection-open trigger/queue/actions. Network/request suppression for featured server discovery; not proof of all discovery UI removal. |
| `removeNitroPromotions` | `PremiumFeatureUpsell.tsx`, `PremiumExpressionPickerFeatureUpsell.tsx`, `PremiumExpressionPickerSearchUpsell.tsx`, `StickerPickerPremiumSearchUpsell.tsx` (`default`), `EmojiPickerPremiumSearchUpsell.tsx` (`PremiumSearchUpsell`) | `after` | `hideExport` | Removes picker-context Nitro promo components only (narrow, path-anchored). |
| `removeNitroOfferSheets` | `modules/premium/native/trials/PremiumTrialOfferActionSheet.tsx` (17092), `modules/premium/native/discounts/PremiumDiscountOfferActionSheet.tsx` (18434) | `after` | `hideExport(default)` | Suppresses promo trial/discount offer action-sheet wrappers. No entitlement/purchase/subscription-management logic targeted. |
| `removeNitroFileUploadPromo` | `modules/premium/file_upload/native/NitroFileUploadUpsellPromoSheet.tsx` (18456) | `after` | `hideExport(default)` | Suppresses Nitro file-upload upsell promo sheet (CTA to Premium settings). **Not** upload-size enforcement/limit logic (limits/rollout live in `NitroFileUploadExperiments.tsx`, not patched). |

**Total:** 7 Reseam patch declarations, 8 promotional export removals (picker 5 + offer sheets 2 + file-upload promo 1) plus Discovery/media behavior patches.

### 1.2 Feature helpers (`patches/apps/discord/extensions/features/src/main/js/index.ts`)
- `withStaticChatMediaOptions`: pure, immutable copy; only forces `gifAutoPlay`/`animateEmoji` when `props.options` is an object; returns original for invalid shapes.
- `hideExport`: conservative no-op on non-object exports; replaces named export with `function DiscordZeroHiddenPromotion(){ return null; }`.
- `forceStaticAvatarDecoration`: wraps `getAvatarDecorationURL` only when function exists; forces `canAnimate:false` for object args, passes through others; updates `default` export object ref when present.
- `disableGifAutoPlay`: mutates only `exports.GifAutoPlay.useSetting/getSetting` when present.
- `disableDiscoveryManager`: defensive checks; disables featured manager methods/actions/queue without affecting other exports.
- `redirectDiscoveryRoutes`: proxies `Routes`; redirects only explicit fixed/dynamic discovery/app-directory route keys to `/channels/@me`; leaves all other route properties (including invites, guild create, channels, etc.) to original target via `Reflect.get`.

**Assessment:** helpers are defensive and narrowly scoped. `redirectDiscoveryRoutes` is the highest-impact surface (route resolution) but its allowlist excludes known protected invite/create keys by omission; runtime navigation/back-stack behavior remains unvalidated.

## 2. Documentation review

- **`docs/discovery-trace-352.17.md`:** clearly distinguishes CI/static evidence from runtime proof. Correctly protects add-server/create/join affordance (`HomeDrawerAddServerRow*`, `GuildsBarCreateJoinButton`/press handler F132199), invite route constants, and `GUILD_CREATE`. Identifies `GUILD_DISCOVERY` (`/guild-discovery`) as **unresolved/unpatched** due to `handleGuildJoin` (32811) and mixed references. Notes app-directory stores/actions intentionally untouched. Release status accurately stated as route/feed patches CI-validated; invite preservation statically scoped but not device-validated.
- **`docs/nitro-expansion-35217.md`:** documents implemented promo removals with module IDs/paths/exports/evidence and records deferred candidates (80867–80870 hooks, generic upsells) with concrete blockers (missing module-factory/export/caller proof; 5065 rollout affects actual upload limits). CI evidence, sizes, and release gates are explicit.
- **Consistency:** docs align with current `DiscordZero.kt`/helpers and CI history. Minor maintenance note: `docs/unbloat-research.md` remains valuable historical research but should be treated as build-specific leads (as it states); audit relies on current trace/nitro docs and latest CI.

## 3. Target uniqueness and shared-functionality risk

- **Static design controls:** every module-factory target uses a single embedded source path + `paramCount(7)` (10 module targets, 10 unique paths). Function target for chat media is constrained by name, 3 identifying strings, and `paramCount(1)`. No `replaceAll`/broad selectors in Reseam Kotlin; no patch targets added for invite/guild-create/guild-discovery routes, 5065 experiments/limits, or unresolved eligibility hooks.
- **CI evidence of unique match/apply:** latest successful `test-unbloat` run **42827307328** (commit `2a9f21b`, 352.17 arm64) logged **`patch application finished ... applied=7 ... dependencies=0 ... skipped=0 ... unmountable=0 ... failed=0`** with explicit apply for `staticChatMedia`, `staticProfileMedia`, `disableDiscoveryRoutes`, `disableServerDiscovery`, `removeNitroPromotions`, `removeNitroOfferSheets`, `removeNitroFileUploadPromo`.
- **Accidental shared-functionality risk (residual):** route proxying is global for the selected route keys (any caller resolving those keys is redirected); featured discovery manager is broadly disabled; hidden promo components return `null` (if a caller assumes a specific rendered structure in an untested context, UX could degrade). These risks are bounded by target selection but **not device-proven**.

## 4. Latest successful CI/workflow status

| Workflow | Run | Status | Notes |
|---|---|---|---|
| `Test DiscordZero unbloat patches` | [42827307328](https://github.com/danishtesting4/discordzero/actions/runs/42827307328) | ✅ success | Validates current 7-patch set on arm64 352.17: patch apply, locale trim, zipalign, sign, apksigner verify, `zipalign -c`, `aapt dump badging`, artifact upload. |
| `Inspect Discord Hermes bundle` | [42829316421](https://github.com/danishtesting4/discordzero/actions/runs/42829316421) | ✅ success | Eligibility-hook/experiment/generic-upsell evidence run. (42829335278 redundant dispatch also succeeded; 42830287114 in progress at audit time for latest query/workflow-doc updates.) |
| `Build Discord APKs (per ABI)` | [42805321472](https://github.com/danishtesting4/discordzero/actions/runs/42805321472) | ✅ success (main, historical) | Builds **stock merged per-ABI APKs** (no Reseam patch, no locale trim). Confirms split download/merge/ABI isolation/align/sign for 352.17, not patched/unbloat output. |
| `Python checks` / `Checks` | no run recorded on `nitro-expansion-35217` tip at audit time | **pending** | Workflow updated in this audit to run Python + JS feature-helper tests; requires CI execution on pushed commit/PR. |
| Python/workflow dispatch on branch | — | n/a | No `python-checks`/`Checks` run observed for `d51ea10`; local Python unavailable in audit environment. |

## 5. Automated tests — gaps and additions

### Existing
- `tests/test_download_base_apk.py`, `tests/test_trim_locale_caches.py`: good coverage for downloader normalization/validation/fallback and locale trim correctness/safety.

### Added in this audit
- **`tests/test_feature_helpers.test.mjs`** (Node built-in test runner, `--experimental-strip-types`): covers `withStaticChatMediaOptions` (immutable/static forcing, invalid shapes), `hideExport` (replacement, invalid inputs), `forceStaticAvatarDecoration` (wrap/default-ref/pass-through/no-op), `disableGifAutoPlay` (overrides/no-op), `disableDiscoveryManager` (disable/no-op/async generators/queue clear), `redirectDiscoveryRoutes` (fixed+dynamic redirects, **protected routes unchanged** incl. invites/guild create/channels, invalid inputs).
- **`tests/test_patch_invariants.py`**: static invariants for current patch set (expected patches declared, module-factory `paramCount(7)` + single unique source path, required promo/discovery/media targets present, expected `hideExport` export names, **forbidden risky/protected tokens absent** such as invite/guild-create/guild-discovery/experiments/eligibility hooks), feature-helper API presence, and CI workflow guardrails (test-unbloat/ABI/inspect steps and pinned checksums present).

### CI integration
- `.github/workflows/python-checks.yml` updated to `Checks` (broader path triggers, Node 24 setup) running `compileall`, `unittest discover -s tests -p "test_*.py" -v`, and `node --test --experimental-strip-types tests/test_feature_helpers.test.mjs`.

### Remaining gaps (not fully automatable here)
- **Patch matching / Reseam failure behavior at runtime:** true “target not found/non-unique” and “patch applied to real 352.17 bundle” validation depends on Reseam + real APK/bundle in CI (`test-unbloat` provides positive evidence; no negative-case fixture bundle committed).
- **End-to-end ABI unbloat packaging:** no workflow currently produces patched+trimmed+aligned+signed artifacts for all four ABIs with before/after manifests.
- **Runtime/UI behavior:** no instrumented device/emulator tests in repo; manual checklist required.

### Local verification (audit environment)
- `node --test --experimental-strip-types tests/test_feature_helpers.test.mjs`: **13 passed, 0 failed**.
- Python tests (`test_*.py`): **not executed locally** (Python not available in PATH); expected to run in CI `Checks`.

## 6. ABI build workflows — reproducibility and packaging

**`build-abi-apks.yml` (per-ABI, stock merge path):**
- ✅ Good controls: pinned APKEditor `V1.4.9` with SHA-256 check; explicit build-tools `35.0.0`; downloads specific splits per ABI (`base`, `config.en`, `config.xxhdpi`, ABI split) via `scripts/download_base_apk.py`; verifies ZIP integrity and exact ABI lib presence (rejects unexpected ABIs); `zipalign -f -p 4`, `apksigner sign`, `apksigner verify --verbose --print-certs`; per-ABI manifest with SHA-256/size.
- ⚠️ **Not the unbloat pipeline:** does not apply Reseam patches or locale trimming — outputs are stock merged APKs, unsuitable for “finished DiscordZero” release claims.
- ⚠️ **Reproducibility limits:** ephemeral CI-generated signing key per run (cannot produce update-compatible builds across runs); upstream split contents depend on mirror/tracker availability at build time (not pinned by checksum inputs except APK structural validation in downloader); runner/tooling drift possible (ubuntu-latest, actions major tags).
- ⚠️ **Locale/resource packaging:** includes `config.en` and `config.xxhdpi` only (consistent with current scripts) but does not include all density/language splits — acceptable if intentional for target, but should be documented/validated for device coverage.

**`test-unbloat.yml` (arm64 patched path):** strong for validation but single-ABI, depends on prebuilt source artifact (`42805321472`), uses temporary Reseam bundle signing key and temporary APK signing key, no before/after size manifest artifact beyond logs/summary.

**`download-apk-inputs.yml` (if used):** not re-audited in detail here; ensure it cannot be mistaken for patched release output.

## 7. Locale trimming and APK signing/verification

- **Locale trimming (`scripts/trim_locale_caches.py`, validated by `tests/test_trim_locale_caches.py` and CI):** targets only `res/raw/cache_intl_*compiledmessages.jsona`; parses JSON, replaces non-kept non-empty locale objects with `{}` (keeps resource entries/IDs), preserves `AndroidManifest.xml` and `resources.arsc` bytes/hash checks, preserves non-signature non-cache entries, removes v1 signature files (META-INF), verifies entry count and replaced contents, writes unsigned output. CI run 42827307328: 2097 caches, 1187 replaced, kept `enGB,id`, compressed 7,141,550→4,498 bytes saved (7,137,052). **Required resources preserved by design/tests:** manifest, resource table, bundle, non-locale assets. **Tradeoff:** non-kept locales fall back to English.
- **Signing/alignment/verification:** `test-unbloat` performs `zipalign -f -p 4` (align), `apksigner sign` (v2/v3/v4 defaults per toolchain), `apksigner verify --verbose`, `zipalign -c -p 4`, `aapt dump badging`; passed in 42827307328. `build-abi-apks` performs align/sign/verify per ABI. **Note:** all audited signing uses temporary CI keys (not update-compatible/publish keys) — correct for test artifacts, blocker for releasable update path.

## 8. Manual device-testing checklist (vs stock Discord 352.17)

> **Not performed.** Execute on representative devices/ABIs (at minimum arm64-v8a; others before multi-ABI release) using **DiscordZero patched/unbloat build** vs **stock Discord 352.17** (same ABI/version). Record device model, Android version, account type (free/Nitro), network conditions, screen recordings/logcat for failures. Use a safe test account/server where possible.

### 8.1 Install, launch, auth
- [ ] Install succeeds on clean device/profile; app label/icon/package behavior matches build expectations; no install conflicts beyond known signing differences.
- [ ] Cold launch, warm launch, and relaunch after force-stop: no crash/ANR/hang.
- [ ] Login (password + 2FA if enabled), logout, session persistence across restart.
- [ ] Account switcher/multi-account flows if available.
- [ ] Push notification registration/token behavior after login (where testable).

### 8.2 Invites, Add Server, create/join (Priority 1 critical)
- [ ] **Invite deep link** from browser/external app opens correctly and allows joining target server.
- [ ] **Invite code/link paste** in-app joins server successfully.
- [ ] Invalid/expired invite shows appropriate error (no crash, no redirect loop).
- [ ] **Add Server / guild create-join UI** opens from guild bar/home drawer; no missing/broken primary actions.
- [ ] **Create server** flow completes end-to-end.
- [ ] Join server does not route to `/channels/@me` unexpectedly except intended discovery redirects.
- [ ] `GUILD_DISCOVERY`-related behavior: observe whether `/guild-discovery` paths are reachable/broken (currently unpatched/unresolved); do not assume fixed.

### 8.3 Discovery and navigation
- [ ] Global server discovery entry points/routes (if reachable) redirect safely to DM home (`/channels/@me`) without crash.
- [ ] Global app discovery / application directory routes/search/profile/category/store-sku redirects behave safely; no navigation trap.
- [ ] **Back navigation** from redirected screens returns to a sensible prior screen (no infinite redirect/back-stack corruption).
- [ ] Tabs/drawer/home surfaces remain usable; guild list, DMs, channel switching unaffected.
- [ ] App commands/application behavior not regressed by route redirects or untouched app-directory stores (sanity check in guild/chat).

### 8.4 Messaging and media
- [ ] Send/receive text messages in DM and guild channels; edit/delete/react.
- [ ] Mentions, replies, threads, embeds, links, spoilers render correctly.
- [ ] GIFs, emoji, stickers: default animation behavior matches intended patch (static/default-safe) without breaking manual playback or non-animated content.
- [ ] Image/video/attachment viewing and download.
- [ ] Profile/avatar/banner rendering: static decoration behavior as intended; normal avatars/banners/profile editing unaffected.

### 8.5 File uploads (Priority 2 critical)
- [ ] **Normal-size upload** (image/file within limits) succeeds in DM and guild.
- [ ] **Large upload** near allowed limit for account type succeeds/fails with correct behavior.
- [ ] **Over-limit upload** shows correct limit/error UX and does not crash; no missing required error state (note: file-upload upsell promo sheet removed — verify enforcement/error remains intact).
- [ ] Nitro file-upload rollout/limits behavior unchanged for eligible/non-eligible users as applicable (no unintended 1GB/limit regression).
- [ ] Upload progress/cancel/retry, multiple attachments.

### 8.6 Nitro, subscriptions, gifts, perks, account
- [ ] Nitro/subscription settings screens load and function (view/manage where applicable).
- [ ] No crashes in billing/premium/settings surfaces due to hidden offer sheets/promos.
- [ ] **Trial/discount offer promo sheets absent** (if triggered in test conditions) without breaking legitimate subscription management/purchase flows.
- [ ] Gifts/perks/account features (profile customization, boosts/Nitro features available to account) behave normally.
- [ ] No false entitlement loss; no blocked legitimate purchase/manage actions.

### 8.7 Emoji, stickers, expressions
- [ ] Emoji picker, sticker picker, GIF picker basic functionality.
- [ ] Previously removed Nitro promo components absent in pickers (as applicable) without breaking picker usability/search/selection.
- [ ] Custom emoji/stickers in servers where permitted.

### 8.8 Notifications and voice
- [ ] Foreground/background notification delivery for messages/mentions/calls (platform-dependent).
- [ ] Notification open navigates to correct channel/message.
- [ ] Voice channel join/leave, mute/deafen, speaking indicators.
- [ ] Voice call/DM call basic stability; audio routing; permissions.
- [ ] Video/screen share sanity check if available (regression-sensitive).

### 8.9 Locale, accessibility, stability
- [ ] English (US base/en-GB kept) and Indonesian display correctly; other locales fall back to English as expected.
- [ ] Reduced motion/accessibility settings: no regressions, essential feedback/loading indicators intact.
- [ ] Extended soak: scrolling, media-heavy channels, search, settings — monitor memory/CPU/crash logs vs stock.

### 8.10 Comparison and evidence capture
- [ ] For each critical flow, compare DiscordZero vs stock 352.17 on same device/account conditions.
- [ ] Capture: pass/fail, screenshots/video, logcat excerpts, steps to reproduce, and whether issue is release-blocking.

## 9. Remaining release blockers

1. **Device/runtime validation not performed (blocking):** all Priority 1 and Priority 2 runtime checks in §8 remain unverified, especially invite deep links/codes, create-server/add-server flows, discovery redirects/back navigation, and file uploads (normal/large/over-limit) given removed promo sheet.
2. **`GUILD_DISCOVERY` (`/guild-discovery`) unresolved:** route not redirected/patched; caller/handler impact not fully proven — must be traced and either safely handled or explicitly accepted with runtime evidence.
3. **No multi-ABI unbloat release pipeline:** `build-abi-apks.yml` produces stock merged APKs; `test-unbloat.yml` validates only arm64 patched+trimmed build. Missing per-ABI patched artifacts, before/after manifests, and publish-grade verification.
4. **Release signing/reproducibility:** audited builds use temporary CI keys (and test-unbloat depends on prior source artifact). Production release requires controlled signing key management and reproducible/pinned inputs.
5. **CI confirmation for new tests:** `Checks` workflow (Python + JS feature-helper tests) added but not yet evidenced green on the pushed audit commit/PR run.
6. **Potential UX edge cases (needs runtime confirmation):** `null`-rendered hidden promo components and proxied route redirects could produce blank sheets/unexpected navigation in untested contexts; discovery removal is intentionally partial (featured feed + selected routes).

**Recommendation:** keep draft PR open, run `Checks` on branch, expand unbloat pipeline to all ABIs with manifests, complete §8 device matrix against stock 352.17, then decide publish readiness. No merge/release/release-channel publication from this audit.