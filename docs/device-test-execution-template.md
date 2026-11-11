# DiscordZero 352.17 — real-device test execution template

**Status:** template/preparation only. **No device testing has been performed or claimed.**  
**Packaging evidence (separate gate):** unbloat CI run [42995108843](https://github.com/danishtesting4/discordzero/actions/runs/42995108843) (352.17, source 42805321472, `enGB,id`, temporary CI signing, non-publishable artifacts). Packaging/integrity verification is **not** runtime/application compatibility proof.

## Scope and controls
- **Feature set:** frozen (no speculative Nitro patches). Compare **DiscordZero unbloat APKs** vs **stock Discord 352.17** (same version/ABI where possible).
- **ABIs/artifacts (CI-verified packaging):**
  - `arm64-v8a`: `discordzero-352.17-arm64-v8a-unbloat.apk` (SHA-256 `723928756f7a7f0d4bc72e8d6c905f7a2554b388ca174a0ab48985ea5a18e43b`)
  - `armeabi-v7a`: `discordzero-352.17-armeabi-v7a-unbloat.apk` (SHA-256 `407dc5c1b3476ee0163c00864a6f8b10021bde20778b8712cdc0ac5b04ef71f6`)
  - `x86`: `discordzero-352.17-x86-unbloat.apk` (SHA-256 `367e0e4411e2d7c06fdbc8a1f80b03fcf516b9f0d1f6a6ed6c23ef52d76318f0`)
  - `x86_64`: `discordzero-352.17-x86_64-unbloat.apk` (SHA-256 `7a65f554e97002b6f06bcefafa6c34c60678903fa52062c71a15254f23db2cd5`)
- **Signing:** temporary CI-generated (non-publishable). Install/update behavior may differ from release-signed builds; record this in results.
- **Release posture:** PR #1 draft, no merge, no release/release-channel publish, no finished `release/` APKs.

## Test environment matrix (fill per run)
| Run | ABI | Device/emulator | Android version | Arch/ABI match | DiscordZero APK (hash verified) | Stock 352.17 APK/build | Account type | Network | Date/tester | Notes |
|---|---|---|---:|---|---|---|---|---|---|---|
| 1 | arm64-v8a |  |  |  |  |  |  |  |  |  |
| 2 | armeabi-v7a |  |  |  |  |  |  |  |  |  |
| 3 | x86 |  |  |  |  |  |  |  |  |  |
| 4 | x86_64 |  |  |  |  |  |  |  |  |  |

> Record any install conflicts/signature differences, clean install vs upgrade, and whether the same account/server conditions were used for DiscordZero and stock comparison.

## Evidence capture (recommended)
- Verify APK hash before install: `sha256sum <apk>` (Linux/macOS) or `Get-FileHash <apk> -Algorithm SHA256` (PowerShell).
- Install: `adb install -r <apk>` (note: temp CI signing may prevent upgrade over differently signed installs).
- Log capture: `adb logcat -c` before test, then `adb logcat -v time > logcat_<abi>_<case>.txt` (or filtered: `adb logcat *:E AndroidRuntime:E Discord:E`).
- Crash/tombstone: `adb bugreport` or capture `logcat` around failure; note ANR/crash dialogs and reproduction steps.
- Screen recording/screenshot per critical case (especially invites, discovery redirects/back nav, uploads, Nitro/settings flows).

## Result legend
- **Pass:** matches expected behavior and stock baseline (where applicable) with no crash/regression.
- **Fail (blocking):** crash, data-loss/security concern, core flow broken, or release-gating regression.
- **Fail (non-blocking):** minor/acceptable deviation (document rationale).
- **N/A:** not applicable to ABI/device/account state.
- **Unresolved:** observed issue needs trace/fix decision (e.g. `/guild-discovery`).

## Priority 1 — Login, messaging, notifications, voice
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P1-01 |  |  | Cold/warm launch | Install, launch, force-stop relaunch | No crash/ANR/hang; comparable startup |  |  |  |  |
| P1-02 |  |  | Login/logout/session | Login (+2FA if enabled), relaunch, logout | Auth/session works as stock |  |  |  |  |
| P1-03 |  |  | Messaging (DM/guild) | Send/receive/edit/delete/react/reply/thread | Core messaging unaffected |  |  |  |  |
| P1-04 |  |  | Embeds/links/mentions | Common message content | Renders/interacts as stock |  |  |  |  |
| P1-05 |  |  | Notifications | Receive/open notification (foreground/background as testable) | Delivery/open routing intact |  |  |  |  |
| P1-06 |  |  | Voice join/controls | Join/leave channel, mute/deafen, indicators | Voice usable, no crash |  |  |  |  |
| P1-07 |  |  | Call basics (if testable) | DM/call connect, audio routing, permissions | Comparable stability |  |  |  |  |

## Priority 2 — Invites, Add Server, create/join (release-critical)
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P2-01 |  |  | Invite deep link | Open invite URL from browser/external app | Correct invite flow/join |  |  |  |  |
| P2-02 |  |  | Invite code in-app | Paste/use invite code | Join succeeds |  |  |  |  |
| P2-03 |  |  | Invalid/expired invite | Use invalid or expired code/link | Proper error, no crash/redirect loop |  |  |  |  |
| P2-04 |  |  | Add Server entry points | Open from guild bar/home drawer | Primary actions present/functional |  |  |  |  |
| P2-05 |  |  | Create server | Complete create-server flow | End-to-end success |  |  |  |  |
| P2-06 |  |  | Join server | Complete join flow | No unintended `/channels/@me` redirection |  |  |  |  |

## Priority 3 — Discovery redirects, back navigation, `/guild-discovery`
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17 / intended patch) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P3-01 |  |  | Global server discovery route(s) | Navigate to reachable discovery entry/route | Safe redirect to `/channels/@me`, no crash |  |  |  |  |
| P3-02 |  |  | App discovery / app directory routes | Navigate/search/profile/category/store-sku where reachable | Safe redirect, no trap/crash |  |  |  |  |
| P3-03 |  |  | Back navigation | Back from redirected screens | Sensible back-stack behavior, no loop |  |  |  |  |
| P3-04 |  |  | `/guild-discovery` | Attempt to reach/use `/guild-discovery` path if exposed | **Observed behavior recorded** (currently unresolved/unpatched in trace) |  |  |  |  |
| P3-05 |  |  | Guild list/DM/channel nav sanity | Normal navigation across app | Unaffected core navigation |  |  |  |  |

## Priority 4 — File uploads (normal/large/over-limit)
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P4-01 |  |  | Normal upload (DM) | Upload small/normal file/image | Succeeds as stock |  |  |  |  |
| P4-02 |  |  | Normal upload (guild) | Upload in guild channel | Succeeds as stock |  |  |  |  |
| P4-03 |  |  | Large near-limit upload | Upload near account/channel limit | Correct success/failure behavior, no regression |  |  |  |  |
| P4-04 |  |  | Over-limit upload | Upload over limit | Correct limit/error UX, no crash; enforcement intact despite promo-sheet removal |  |  |  |  |
| P4-05 |  |  | Progress/cancel/retry/multi | Manage upload lifecycle | Comparable to stock |  |  |  |  |

## Priority 5 — Nitro settings, gifts, perks, subscriptions
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P5-01 |  |  | Nitro/subscription settings | Open and navigate settings/billing surfaces | Loads/functions; no crash from hidden promos |  |  |  |  |
| P5-02 |  |  | Gifts/perks/account surfaces | Access gifts/perks/account premium features as available | Legitimate flows intact |  |  |  |  |
| P5-03 |  |  | Subscription management | View/manage existing subscription (if applicable) | No blocked/altered legitimate management |  |  |  |  |
| P5-04 |  |  | Trial/discount promo surfaces | Trigger if naturally reachable | Promo sheets absent where patched, without breaking flow |  |  |  |  |
| P5-05 |  |  | Entitlements | Use Nitro/perk features entitled to account | No false entitlement loss |  |  |  |  |

## Priority 6 — Emoji, stickers, GIFs, avatars, profile decorations
| ID | ABI | Android | Test case | Steps | Expected (vs stock 352.17 / intended patch) | Actual | Result | Log/video evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P6-01 |  |  | Emoji picker/use | Pick/send emoji (including custom where permitted) | Functional; picker promo removals do not break usability |  |  |  |  |
| P6-02 |  |  | Sticker picker/use | Pick/send stickers | Functional; no broken picker state |  |  |  |  |
| P6-03 |  |  | GIFs/animated media | View/send GIFs and animated emoji behavior | Matches intended static/autoplay policy; no broken rendering |  |  |  |  |
| P6-04 |  |  | Avatars/profile rendering | View profiles, avatars, decorations | Static decoration behavior as intended; normal content unaffected |  |  |  |  |
| P6-05 |  |  | Manual media/banner behavior (if applicable) | Cases previously requiring manual playback/interaction | No regression from static-media changes |  |  |  |  |

## Summary (fill after execution)
| ABI | Device/Android | P1 | P2 | P3 | P4 | P5 | P6 | Blocking issues | Non-blocking issues | Overall |
|---|---|---|---|---|---|---|---|---|---|---|
| arm64-v8a |  |  |  |  |  |  |  |  |  |  |
| armeabi-v7a |  |  |  |  |  |  |  |  |  |  |
| x86 |  |  |  |  |  |  |  |  |  |  |
| x86_64 |  |  |  |  |  |  |  |  |  |  |

## Release readiness notes (post-test)
- [ ] All blocking issues triaged/fixed or explicitly accepted with evidence.
- [ ] `/guild-discovery` outcome documented (fixed, deferred with evidence, or accepted risk).
- [ ] Stable release signing/provenance strategy defined (separate from temporary CI signing).
- [ ] No GitHub release/release-channel publish and no finished `release/` APKs until runtime + packaging + signing gates are satisfied.
- [ ] PR #1 remains draft until release decision.

**Reminder:** successful CI packaging/verification proves artifact integrity, not device compatibility. Do not expand Nitro scope without new, proven-safe evidence.