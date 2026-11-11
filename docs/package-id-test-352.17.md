# Package ID separation test record — `com.discordzero` (352.17)

**Status:** **BLOCKED** (no `com.discordzero` APK produced).  
**Reason:** Phase 1 audit (`docs/package-id-audit.md`) concluded a reliable package rename is **not achievable with the current build architecture** (Reseam Hermes bytecode patching of prebuilt APKs + locale trim + zipalign/sign). Per constraints, implementation/CI/verification stopped at the documented blocker to avoid producing a misleading APK.

## Build / artifact (renamed package)
| Field | Value | Result |
|---|---|---|
| Build commit | `048f943` (`nitro-expansion-35217`, PR #1 draft) — audit only | **BLOCKED** |
| Workflow run (`com.discordzero`) | N/A | **NOT TESTED** |
| Renamed artifact locations | N/A (none produced) | **BLOCKED** |
| Renamed artifact SHA-256 hashes | N/A | **NOT TESTED** |
| Manifest package ID (`com.discordzero`) | N/A | **NOT TESTED** |
| Conflicting authorities/components check | N/A (no renamed manifest/APK) | **NOT TESTED** |
| APK signature verification | N/A | **NOT TESTED** |
| ZIP alignment verification | N/A | **NOT TESTED** |
| Version name / version code (352.17 / 352017) | N/A | **NOT TESTED** |
| ABI / native library contents verification | N/A | **NOT TESTED** |
| Reseam patch application (`com.discordzero` target) | N/A | **NOT TESTED** |

## Device/runtime verification (itel S666LN, Android 13/API 33, arm64-v8a)
| Test | Result | Notes |
|---|---|---|
| Install alongside official Discord (no uninstall/replace of Play Store install) | **BLOCKED** | No `com.discordzero` APK available. Official Discord install on device (`com.discord` 352.17, `352017`) was **not uninstalled, replaced, or modified**. |
| Confirm both packages appear independently | **NOT TESTED** |  |
| Launch DiscordZero and capture logcat | **NOT TESTED** |  |
| Login | **NOT TESTED** |  |
| Notifications / FCM | **NOT TESTED** |  |
| Deep links / app links / custom scheme | **NOT TESTED** |  |
| App integrations / OAuth / package-dependent behavior | **NOT TESTED** |  |

## Reference: existing `com.discord` (unchanged) packaging evidence
Validated unbloat artifacts from CI [42995108843](https://github.com/danishtesting4/discordzero/actions/runs/42995108843) (352.17, source 42805321472, temporary CI-signed, non-publishable; **not** `com.discordzero`):

| ABI | Output SHA-256 |
|---|---|
| arm64-v8a | `723928756f7a7f0d4bc72e8d6c905f7a2554b388ca174a0ab48985ea5a18e43b` |
| armeabi-v7a | `407dc5c1b3476ee0163c00864a6f8b10021bde20778b8712cdc0ac5b04ef71f6` |
| x86 | `367e0e4411e2d7c06fdbc8a1f80b03fcf516b9f0d1f6a6ed6c23ef52d76318f0` |
| x86_64 | `7a65f554e97002b6f06bcefafa6c34c60678903fa52062c71a15254f23db2cd5` |

## Known limitations / blockers
- Package identity is embedded across manifest (package, permission, 8+ authorities/providers, components/aliases, affinities, actions), resources.arsc, 3 DEX files, Hermes/RN bundles, native libs, and integration configs (Firebase/FCM, deep/app links, OAuth). Current pipeline cannot perform exhaustive, consistent rename.
- Any future dual-mode implementation must keep `com.discord` outputs/workflows intact, avoid broad search-replace, add dedicated repackaging+verification, and complete runtime validation before compatibility claims.
- **Not performed/claimed:** side-by-side install, launch, login, notifications, deep links, or app-integration compatibility for `com.discordzero`.

**Controls:** `main` unmodified, PR #1 open/draft, no GitHub releases/production artifacts published, existing `com.discord` build path preserved, no Nitro/Discovery/animation/locale-scope expansion.