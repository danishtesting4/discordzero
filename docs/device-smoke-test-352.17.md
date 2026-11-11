# DiscordZero 352.17 — emulator smoke test (limited)

**Date:** 2026-11-11  
**Scope:** limited runtime smoke test only (not a substitute for the full device checklist). **No login, messaging, notifications, voice, invite/join/create-server, discovery navigation, upload, Nitro settings/gifts/perks/subscription, or emoji/sticker functional flows were tested.** No accounts/credentials were used.

## Environment
- **Host:** Windows 10.0.19045 (local environment)
- **Android SDK:** `C:\Users\danis\AppData\Local\Android\Sdk`
- **ADB:** `platform-tools/adb.exe` 1.0.41 (37.0.1-15733141)
- **Emulator:** `emulator.exe`, AVD `andistro_test` (Pixel 6 profile, `abi.type=x86_64`, Play Store disabled), WHPX acceleration usable
- **Emulated device:** `emulator-5554` (`sdk_gphone64_x86_64`), **Android 14 (API 34)**, `x86_64`, build `sdk_gphone64_x86_64-userdebug 14 UE1A.230829.050 12077443 dev-keys`
- **Launch flags:** `-no-window -no-audio -no-boot-anim -gpu swiftshader_indirect`

## Artifact tested
- **ABI:** `x86_64` only
- **APK:** `discordzero-352.17-x86_64-unbloat.apk` (CI run [42995108843](https://github.com/danishtesting4/discordzero/actions/runs/42995108843), `352.17`, source `42805321472`, `enGB,id`, **temporary CI-signed, non-publishable**)
- **Pre-install hash (verified):** `7a65f554e97002b6f06bcefafa6c34c60678903fa52062c71a15254f23db2cd5`
- **Installed package:** `com.discord`, `versionName=352.17 - Stable`, `versionCode=352017`, `minSdk=24`, `targetSdk=36`, `base.apk=/data/app/~~pjSXW1iIU5Ki1VapzngtZQ==/com.discord-AWBejcnWiGhJICS8MSNi-Q==/base.apk`

## Results (x86_64, `andistro_test` / API 34, limited smoke)
Status legend: **PASS** = observed as expected in this scope; **FAIL** = observed failure/regression; **BLOCKED** = could not execute due to environment/account/prerequisite; **NOT TESTED** = not executed (no claim made).

| ID | Area | Test | Result | Evidence/notes |
|---|---|---|---|---|
| S1 | Packaging/install | APK hash matches CI manifest/artifact | **PASS** | Local SHA-256 `7a65f554...db2cd5` matched expected x86_64 output |
| S2 | Packaging/install | Install on emulator | **PASS** | `adb install -r -g` succeeded; `pm path com.discord` returned installed base APK |
| S3 | Launch | Initial launch immediately post-install (monkey) | **BLOCKED** | `java.lang.SecurityException: Package com.discord is currently frozen!` during dexopt/finalization; ActivityManager force-stopped. Timing/package-state issue, not confirmed app defect |
| S4 | Launch/runtime | Relaunch after settle (`am start com.discord/.main.MainDefault`) | **PASS (smoke)** | Process `pid 4557`, resumed `com.discord/.main.MainDefault`, window present |
| S5 | Runtime startup | Hermes/RN/JS startup, no immediate Discord fatal crash | **PASS (smoke, limited window)** | `ReactNativeJS: Running "Discord"`, Hermes JNI registration, `libdiscord.so` activity; no `FATAL EXCEPTION`/`AndroidRuntime` crash or `UnsatisfiedLinkError` observed in captured window |
| S6 | Runtime | Locale/resource warnings | **PASS (non-fatal, observed)** | `en-US` missing-message warnings (e.g. `2F5EsD`, `PA8TUT`, `0uDEd6`, `y2oJvM`); app remained running |
| S7 | Observability | UI hierarchy dump / interactive UI inspection | **BLOCKED** | `uiautomator dump` failed (`null root node`); screenshot captured but not visually reviewed in-session |
| S8 | Environment | Emulator/system stability during run | **FAIL (environment, non-Discord)** | `mCurrentFocus=Application Not Responding: com.android.systemui` while Discord remained resumed; attributed to headless/swiftshader emulator pressure, not a confirmed Discord crash |
| F1 | Auth/core | Login, session, logout | **NOT TESTED** | No credentials/account interaction performed |
| F2 | Messaging | DM/guild messaging, edit/delete/react/reply/thread | **NOT TESTED** |  |
| F3 | Notifications | Push/in-app notification behavior | **NOT TESTED** |  |
| F4 | Voice/calls | Voice join/controls, calls | **NOT TESTED** |  |
| F5 | Invites/join/create | Invite deep links/codes, Add Server, create/join | **NOT TESTED** | Release-critical; requires accounts/server/invite fixtures |
| F6 | Discovery/navigation | Discovery redirects, back navigation, `/guild-discovery` | **NOT TESTED** | `/guild-discovery` remains unresolved/unpatched per trace |
| F7 | Uploads | Normal/large/over-limit uploads and limit UX | **NOT TESTED** | Release-critical; requires account/network/files |
| F8 | Nitro/premium | Settings, gifts, perks, subscriptions/entitlements, promo absence | **NOT TESTED** |  |
| F9 | Media/expressions | Emoji, stickers, GIFs, avatars, profile decorations | **NOT TESTED** |  |
| F10 | Comparison | Baseline vs stock Discord 352.17 (same ABI/device conditions) | **NOT TESTED** | Stock baseline not executed in this run |
| F11 | Other ABIs | `arm64-v8a`, `armeabi-v7a`, `x86` runtime validation | **NOT TESTED** | x86_64 emulator only |

## Interpretation
- **Positive smoke signal (limited):** the x86_64 unbloat build is installable and can start, load Hermes/React Native, and run Discord JS to a resumed main activity on an x86_64 Android 14 emulator without an observed immediate Discord fatal crash.
- **Not validated:** all functional/runtime flows in `docs/device-test-execution-template.md` remain untested (login, messaging, notifications, voice, invites/Add Server/create/join, discovery redirects/back navigation/`/guild-discovery`, normal/large/over-limit uploads, Nitro settings/gifts/perks/subscriptions, emoji/stickers/GIFs/avatars/profile decorations), as well as `arm64-v8a`, `armeabi-v7a`, and `x86` on compatible real devices/emulators.

## Repeatable execution plan (recommended)
1. Boot the AVD interactively for observable/manual testing (avoid headless where possible):  
   `emulator -avd andistro_test -gpu host` (or `swiftshader_indirect` if needed), wait for `adb shell getprop sys.boot_completed` = `1`.
2. Record **stock Discord 352.17** baseline on the same ABI/device conditions first (install/launch behavior, target flows, screenshots/logcat).
3. Install and test **DiscordZero x86_64** artifact (verify SHA-256 before install), then compare against baseline.
4. Prioritize: login/messaging/notifications/voice; invites/Add Server/create/join; Discovery redirects/back navigation/`/guild-discovery`; normal/large/over-limit uploads; Nitro settings/gifts/perks/subscriptions; emoji/stickers/GIFs/avatars/profile decorations.
5. Capture per-test evidence: result (PASS/FAIL/BLOCKED/NOT TESTED), screenshot/video, logcat (`adb logcat -d` / filtered), reproduction steps, and crash/ANR details.
6. Repeat on other compatible ABI environments/devices where practical (`arm64-v8a` physical device preferred; `armeabi-v7a`/`x86` as available).

## Follow-up required
1. Execute the full per-ABI checklist in `docs/device-test-execution-template.md` on compatible devices/emulators vs stock Discord 352.17.
2. Re-test `x86_64` on a stable interactive device/emulator with account/test fixtures and captured evidence for prioritized flows.
3. Treat `/guild-discovery` as unresolved until observed and decided.
4. Keep Nitro scope frozen, PR #1 draft, temporary CI signing separate from release signing, and no release/release-channel publication until runtime + packaging + signing gates are satisfied.