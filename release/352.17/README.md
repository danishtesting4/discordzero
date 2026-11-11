# DiscordZero 352.17 — patched testing APKs (CI artifacts)

This directory is prepared for the **four patched DiscordZero unbloat APKs** (Discord Android **352.17**, version code **352017**, package **`com.discord`**) produced by CI workflow run [42995108843](https://github.com/danishtesting4/discordzero/actions/runs/42995108843) (commit `8e489cd548aff78ac30611c3ac8974b486409390`).

## Purpose
- **Testing inputs** for the Valenced modded-client workflow and runtime validation.
- **Not production releases.** `build_type: testing`, `publishable_release_artifact: false`, **temporary CI signing certificate**.

## Contents
| ABI | File | SHA-256 | Size (bytes) |
|---|---|---|---:|
| arm64-v8a | `arm64-v8a.apk` | `723928756f7a7f0d4bc72e8d6c905f7a2554b388ca174a0ab48985ea5a18e43b` | 194,743,618 |
| armeabi-v7a | `armeabi-v7a.apk` | `407dc5c1b3476ee0163c00864a6f8b10021bde20778b8712cdc0ac5b04ef71f6` | 169,450,908 |
| x86 | `x86.apk` | `367e0e4411e2d7c06fdbc8a1f80b03fcf516b9f0d1f6a6ed6c23ef52d76318f0` | 189,209,577 |
| x86_64 | `x86_64.apk` | `7a65f554e97002b6f06bcefafa6c34c60678903fa52062c71a15254f23db2cd5` | 198,896,827 |

See [`manifest.json`](manifest.json) for machine-readable metadata.

## Important warnings
- **Temporary CI signing certificate:** these APKs **cannot install or update over the official Play Store Discord installation** because the signing certificate differs. Replacing the existing `com.discord` installation requires uninstalling it first, which **removes Discord app data and login/session** for that install/profile. Use a separate test environment/profile where possible.
- **Not runtime-validated/release-ready:** packaging/integrity was CI-verified, but full physical-device functional testing, stable production signing, and release readiness are separate gates. Do not treat these as production releases.
- **Package ID:** remains `com.discord` (verified).

## Integrity
Before use, verify each file against the SHA-256 hash in this README/manifest (e.g. `Get-FileHash <file> -Algorithm SHA256` on Windows or `sha256sum <file>` on Linux/macOS). Do not modify, recompress, re-sign, or rebuild the APKs.