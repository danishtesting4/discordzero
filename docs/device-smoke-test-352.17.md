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

## Observed results

| Check | Result | Evidence/notes |
|---|---|---|
| APK hash matches CI manifest/artifact | **Pass** | Local SHA-256 matched expected x86_64 output hash |
| Install on emulator | **Pass** | `adb install -r -g` succeeded; `pm path com.discord` returned installed base APK |
| Initial launch attempt (monkey, immediately post-install) | **Fail/inconclusive** | `java.lang.SecurityException: Package com.discord is currently frozen!` during install/dexopt finalization; ActivityManager force-stopped process. Attributed to post-install package state/timing, not confirmed as app defect |
| Relaunch after settle (`am start com.discord/.main.MainDefault`) | **Pass (smoke)** | Process started (`pid 4557`), task/activity resumed: `topResumedActivity=... com.discord/.main.MainDefault`, window present (`com.discord/com.discord.main.MainDefault`) |
| JS/Hermes/React Native startup | **Observed** | Logcat: `ReactNativeJS: Running "Discord"`, Hermes executor/instance JNI registration, `libdiscord.so` load activity; no `FATAL EXCEPTION`/`AndroidRuntime` crash or `UnsatisfiedLinkError` for Discord observed in captured window |
| Locale warnings | **Observed (non-fatal)** | `ReactNativeJS` warnings for missing message keys in `en-US` / default locale (e.g. `2F5EsD`, `PA8TUT`, `0uDEd6`, `y2oJvM`); app remained running |
| UI automation dump | **Inconclusive** | `uiautomator dump` failed (`null root node returned by UiTestAutomationBridge`); screenshot captured to host temp file but not visually reviewed in this session |
| Emulator/system stability | **Caveat** | `dumpsys window` showed `mCurrentFocus=Window{... Application Not Responding: com.android.systemui}` while Discord task remained resumed; likely emulator/system-ui instability under headless swiftshader load, not attributed to Discord crash from available evidence |

## Interpretation
- **Positive smoke signal (limited):** the x86_64 unbloat build is installable and can start, load Hermes/React Native, and run Discord JS to a resumed main activity on an x86_64 Android 14 emulator without an observed immediate Discord fatal crash.
- **Not validated:** all functional/runtime flows in `docs/device-test-execution-template.md` remain untested (login, messaging, notifications, voice, invites/Add Server/create/join, discovery redirects/back navigation/`/guild-discovery`, normal/large/over-limit uploads, Nitro settings/gifts/perks/subscriptions, emoji/stickers/GIFs/avatars/profile decorations), as well as `arm64-v8a`, `armeabi-v7a`, and `x86` on compatible real devices/emulators.

## Follow-up required
1. Execute the full per-ABI checklist in `docs/device-test-execution-template.md` on compatible devices/emulators vs stock Discord 352.17.
2. Re-test `x86_64` on a stable device/emulator with interactive access, account credentials (as appropriate), and log/screen capture for the prioritized flows.
3. Treat `/guild-discovery` as unresolved until observed and decided.
4. Keep Nitro scope frozen, PR #1 draft, temporary CI signing separate from release signing, and no release/release-channel publication until runtime + packaging + signing gates are satisfied.