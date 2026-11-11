# Package ID audit — `com.discord` → `com.discordzero` (Discord 352.17)

**Date:** 2026-11-11  
**Branch:** `nitro-expansion-35217` (HEAD `ef5f18c` at audit start)  
**Scope:** Phase 1 repository + APK artifact audit for feasibility of a separate DiscordZero Android application ID. **No implementation changes made; no package-renamed APK produced.**

## Evidence sources
- **Source repo:** recursive scan of non-binary source/config/docs files (excluding `build/ci-reports/`, `build/ci-artifacts/`, `.git/`) for `com.discord`.
- **APK (validated unbloat arm64 artifact):** `build/ci-reports/42995108843/discordzero-352.17-arm64-v8a-unbloat/discordzero-352.17-arm64-v8a-unbloat.apk` (`352.17`/`352017`, SHA-256 `723928756f7a7f0d4bc72e8d6c905f7a2554b388ca174a0ab48985ea5a18e43b`, temporary CI-signed).
- **Tools:** `aapt dump badging/xmltree/resources/strings`, zip entry inspection, manifest dump (`build/ci-reports/42995108843/manifest-xmltree.txt`, **100** lines containing `com.discord`).

## Summary
A reliable rename from `com.discord` to `com.discordzero` is **not achievable with the current build architecture** (Reseam Hermes bytecode patching of prebuilt APKs + locale trim + zipalign/sign). The package identity is embedded across manifest, resources.arsc package namespace, 3 DEX files, Hermes/RN bundles, native libraries, authorities/permissions/providers, and app integration surfaces. Exhaustive, consistent renaming without regressions would require a dedicated APK repackaging pipeline (decode/rename/rebuild) and extensive runtime validation; producing a renamed APK with the current tooling would risk a misleading/broken artifact. **Implementation stopped at audit (blocker documented).**

## 1. Repository/source occurrences (`com.discord`)

| Location | Occurrence | Classification | Notes |
|---|---|---|---|
| `patches/apps/discord/patch/src/main/kotlin/app/discordzero/patches/discord/DiscordZero.kt:77,88,103,114,125,152,167` | `compatibleWith("com.discord")` (7 patches) | **Build/test-only reference (patch targeting) for current mode; Must change for a `com.discordzero` build mode** | Reseam patch applicability target. A separate renamed build mode would need these to target `com.discordzero` (or be parameterized) while keeping `com.discord` mode intact. |
| `patches/manifest.toml`, `patches/settings.gradle.kts`, `patches/apps/discord/patch/build.gradle.kts`, `patches/apps/discord/extensions/features/build.gradle.kts` | No `com.discord` string | **No change (current)** | Workspace/bundle config; may need mode-aware wiring only if implementation adds dual-mode outputs. |
| `scripts/download_base_apk.py`, `scripts/trim_locale_caches.py`, `scripts/check_tracker.py` | No `com.discord` string | **Build/test-only / No change** | Operate on APK contents/splits/versioning, not package ID. |
| `.github/workflows/*.yml` (build/test/inspect/download/tracker) | No `com.discord` string | **Build/test-only reference / Must change (new workflow mode) if renamed CI added** | Existing workflow meanings must remain unchanged; a renamed build would require separate workflow/mode and artifact naming/manifests. |
| `tests/test_patch_invariants.py` | No direct `com.discord` token (guards patch targets/forbidden tokens) | **Build/test-only reference / Must change if dual-mode introduced** | Invariants currently assume existing patch declarations; dual-mode would require verifying both modes without breaking originals. |
| `docs/release-readiness-audit.md:11` | Describes `compatibleWith("com.discord")` | **Build/test-only documentation** | Accurate for current build; would need update if dual-mode added. |
| `docs/device-smoke-test-352.17.md:18,26,27,28` | Installed package/activity/log references (`com.discord`, `com.discord/.main.MainDefault`) | **Build/test-only/runtime evidence for current package** | Must remain accurate for existing artifacts/tests; renamed build would have different package/components. |

## 2. APK manifest/package metadata (authoritative for install identity)

**Observed:** package `com.discord`, `versionName=352.17 - Stable`, `versionCode=352017`, `minSdk=24`, `targetSdk=36`, label/icon Discord. **100 manifest elements** contain `com.discord`.

| Class | Examples (from `aapt dump xmltree`) | Classification | Notes |
|---|---|---|---|
| Application package | `manifest package="com.discord"` | **Must change** | Defines install identity; must become `com.discordzero` for side-by-side install. Also affects resources package namespace and runtime package context. |
| Custom permission + use | `com.discord.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` (declared/used) | **Must change** | Must be unique to avoid install/conflict with official Discord. |
| Content provider authorities | `com.discord.file-provider` (FileProvider), `com.discord.imagepickerprovider`, `com.discord.fileprovider`, `com.discord.provider`, `com.discord.androidx-startup`, `com.discord.firebaseinitprovider`, `com.discord.SentryInitProvider`, `com.discord.SentryPerformanceProvider` | **Must change** | Authorities must be globally unique per install; conflicts prevent side-by-side install or break providers (file sharing, Firebase init, Sentry, startup). |
| Application/components/task affinity | `com.discord.MainApplication`, `com.discord.TTIComponentFactory`, activities/aliases/services/receivers (`com.discord.main.*`, `com.discord.share.ShareActivity`, `com.discord.notifications.*`, `com.discord.foreground_service.*`, `com.discord.telecom.service.*`, `com.discord.socialrpc.*`, `com.discord.samsung.*`, `com.discord.file_downloader.*`, `com.discord.chrome_custom_tabs.*`, `com.discord.react.headless_tasks.*`, etc.), `taskAffinity` `com.discord.share` / `com.discord.custom_tab_host` | **Must change (manifest/component identity) / Requires runtime investigation (class-name vs package coupling)** | Component class names are Java/Kotlin classes in DEX; renaming package identity may require renaming classes/namespaces in DEX/resources or careful manifest remapping. Aliases/targets and task affinities must not conflict. |
| Custom intent actions | `com.discord.intent.action.SDK`, `com.discord.intent.action.CONNECT`, `com.discord.intent.action.NOTIFICATION_ACTION` | **Requires runtime investigation** | Changing avoids cross-app collisions but may break integrations expecting stock actions; keeping may cause ambiguity with stock app installed. |
| Package-visibility queries | `<queries><package name="com.discord">`, `com.discord.buildOverride`, `com.discord.debug` | **Must remain unchanged** (for visibility of official/debug/build-override packages) **and/or Requires runtime investigation** | These declare visibility of other Discord packages, not this app’s identity; blind rename could alter intended behavior. |
| Deep links / web domains / schemes | `https://discord.com`, `*.discord.com`, `discord.gg`, `discord.gift`, `discordapp.onelink.me`, `l.discord.com`, path patterns (`/invite/`, `/channels/`, etc.), custom scheme `discord://app/...` | **Must remain unchanged (web domains/paths) / Requires runtime investigation (ownership/verification behavior)** | These are Discord’s domains/links; they should continue to resolve to Discord services. Side-by-side install means Android may prompt/choose handler; App Links verification and in-app routing for a renamed package need runtime validation. |
| FCM/messaging declaration | `com.discord.notifications.service.NotificationService` intent filter `com.google.firebase.MESSAGING_EVENT` | **Must change (component identity if renamed) / Requires runtime investigation (functionality)** | Service/component identity tied to package/classes; push delivery depends on Firebase config/app registration (see below). |

## 3. DEX, Hermes/React Native bundles, and native libraries

| Artifact | Evidence | Classification | Notes |
|---|---|---|---|
| DEX | `classes*.dex` count **3** | **Must change (if class/package renamed) / Requires runtime investigation** | App code/classes likely under `com.discord.*` namespaces and may contain package-name string literals. Consistent renaming across all DEX, manifest, and resources is required for a true package rename. |
| Hermes/RN bundles | `assets/index.android.bundle` (~71 MB), `assets/index.android.bundle.patch` (~70 MB) present | **Requires runtime investigation; likely Must change for some references** | JS/Hermes bytecode may contain package/name strings, deep-link handling assumptions, native module expectations, or internal identifiers. Reseam patches Hermes bytecode for targeted modules, but does not perform global package renaming. |
| Native libraries (`lib/arm64-v8a/*.so`, 40+ incl. `libdiscord.so`, `libappmodules.so`, `libreactnative.so`, Hermes/JSI libs, etc.) | Present in APK | **Requires runtime investigation** | Native code may embed package names, paths, or checks; binary-safe renaming is non-trivial and ABI-specific. |
| Resources.arsc | `Package 0 id=0x7f name=com.discord` (`aapt dump resources`) | **Must change** | Resource table package name/namespace tied to application package; must be updated consistently with manifest/DEX. |
| Firebase/Google config artifacts | `res/raw/firebase_common_keep.xml`, `firebase-annotations/encoders/iid-interop/measurement-connector.properties`, `googleid.properties`, `play-services-*.properties`, `com.discord.firebaseinitprovider` authority | **Requires runtime investigation; likely Must change (authority) and high risk for runtime behavior** | Firebase/FCM project/app configuration may be embedded in resources/values/assets and tied to the registered app; renaming package can break push notifications, analytics, and Google integrations without correct reconfiguration. |

## 4. Build/test/tooling implications

| Area | Classification | Notes |
|---|---|---|
| Reseam patch compatibility | **Must change for renamed build mode; Must remain unchanged for existing mode** | `compatibleWith("com.discord")` matches stock package; a `com.discordzero` APK/build would require corresponding compatibility (parameterized or parallel patch set) without altering current outputs. |
| Current build architecture (`reseam patch` + `scripts/trim_locale_caches.py` + zipalign/sign) | **Insufficient for reliable rename (blocker)** | No manifest package rewrite, no resources.arsc package rename, no DEX class/package ref rewrite, no Hermes/global string ref rewrite, no authority/provider/permission/component conflict rewrite, no native binary rewrite. |
| CI workflows/artifacts | **Build/test-only; existing meanings Must remain unchanged** | `build-abi-apks.yml` (stock), `build-unbloat-abi-apks.yml`/`test-unbloat.yml` (unbloat, temporary CI-signed), manifests/hashes/naming all assume current identity. Any renamed mode needs separate, explicit outputs/manifests and must not overwrite existing artifacts. |
| Invariant/verification tests | **Build/test-only; Must change if dual-mode added** | `tests/test_patch_invariants.py` and workflow checks must validate both `com.discord` and `com.discordzero` modes independently if implemented. |

## 5. Viability assessment

**Technically viable in principle:** yes, *only* with a dedicated APK repackaging/rename pipeline that exhaustively and consistently updates manifest package/components/authorities/permissions/task affinities/intent actions (as appropriate), resources.arsc, DEX package/class references, Hermes bundle strings/references, provider/file-sharing configs, and any native/resource-embedded identifiers — followed by rebuild, alignment, signing, and comprehensive runtime testing.

**Viable with current build architecture:** **No (blocker).** The existing Reseam + trim + align/sign pipeline cannot reliably perform the required cross-artifact rename. Attempting partial/automated broad replacement would be high-risk and could produce a misleading, installable-in-name-only or functionally broken APK (conflicting authorities, broken providers/Firebase/push/links/auth, class/package mismatches, or crashes).

## 6. Required stop / blocker

Per constraints, **implementation halted after audit**: no source renaming, no dual-mode workflow, no renamed APK, no CI artifacts for `com.discordzero`, and no device install/swap performed. To proceed safely, the project would need (at minimum): a scoped, reversible dual-mode design preserving `com.discord` outputs; a proven APK rename/repackage toolchain integrated into CI; exhaustive automated verification of manifest/resources/DEX/bundle refs and authority uniqueness; and runtime validation (install side-by-side, launch, login, notifications/FCM, deep/app links, share/file-provider, app integrations) on test environments — **not** on the physical device without explicit, non-destructive setup.

## 7. Occurrence classification index (requested)

- **Must change (for a successful `com.discordzero` identity):** manifest `package`; custom permission `com.discord.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`; all `com.discord*` provider authorities; component/app/task-affinity identities tied to package installation uniqueness; resources.arsc package name; DEX package/class namespace references; any package-identity strings required for app/provider resolution.
- **Must remain unchanged:** Discord web domains/hosts/paths and external brand/service endpoints (`discord.com`, `*.discord.com`, `discord.gg`, `discord.gift`, `discordapp.onelink.me`, etc.); `<queries>` entries intended to detect official/debug/build-override Discord packages (unless deliberately redesigned); existing `com.discord` build mode, artifacts, and workflow semantics.
- **Requires runtime investigation:** Hermes/JS bundle and native library embedded strings; Firebase/FCM/push registration and `firebaseinitprovider` behavior; custom intent actions collision/compatibility; App Links/deep-link/custom-scheme handling when side-by-side; OAuth/account integrations; share/file-provider behavior; any hardcoded package checks in DEX/native/JS.
- **Build/test-only reference:** `compatibleWith("com.discord")` in patch sources (current mode), CI/workflow/test naming and assumptions, docs describing current package/test evidence. These must be preserved for current mode and carefully duplicated/parameterized for any future dual-mode work.