# Discovery trace — Discord 352.17 / HBC 98

## Scope and evidence

This trace is tied to the Discord 352.17 arm64 bundle built by source run `42805321472`, inspected in run `42815262982` (HBC 98). Function IDs are bundle-specific and must be regenerated for each Discord build.

The inspection artifact was downloaded and reviewed. It contains 64 xref reports and 171 decompilations. This document distinguishes decompiled evidence from conclusions that still need handler-level inspection or device testing.

## Current implementation

The patch source currently contains two separate Discovery controls:

1. `disableServerDiscovery` patches the unique seven-parameter Metro factory for `modules/global_discovery_servers/GlobalDiscoveryServersFeaturedSearchManager.tsx`. It disables the featured-feed connection trigger and fetchers. The prior test build `42815357405` validated patch application and APK packaging.
2. `disableDiscoveryRoutes` patches the seven-parameter `modules/routing/RouteConstants.tsx` factory. Its helper wraps `exports.Routes` and redirects selected fixed and dynamic Discovery/application-directory route properties to `/channels/@me`.

The route patch was applied successfully in test-unbloat run `42815951706` for Discord 352.17 arm64. The log explicitly reports `disableDiscoveryRoutes` and `disableServerDiscovery` as applied; the APK was aligned, signed, and verified. This is build/patch validation only, not proof of navigation behavior on a device.

### Route keys currently redirected

Fixed route properties:
- `GLOBAL_DISCOVERY` → `/channels/@me`
- `GLOBAL_DISCOVERY_SERVERS` → `/channels/@me`
- `GLOBAL_DISCOVERY_APPS` → `/channels/@me`
- `GLOBAL_DISCOVERY_APPS_SEARCH` → `/channels/@me`
- `APPLICATION_DIRECTORY` → `/channels/@me`
- `APPLICATION_DIRECTORY_SEARCH` → `/channels/@me`

Dynamic route properties:
- `GLOBAL_DISCOVERY_APPS_CATEGORY`
- `GLOBAL_DISCOVERY_APPS_PROFILE`
- `GLOBAL_DISCOVERY_APPS_PROFILE_SECTION`
- `GLOBAL_DISCOVERY_APPS_PROFILE_STORE_SKU`
- `APPLICATION_DIRECTORY_PROFILE`
- `APPLICATION_DIRECTORY_PROFILE_SECTION`
- `APPLICATION_DIRECTORY_PROFILE_STORE_SKU`

Each dynamic route function currently returns `/channels/@me`.

## Protected add-server / invite path

### Add-server affordance

- Function 17836 is the Metro module factory for `modules/home_drawer/native/HomeDrawerAddServerRow.tsx`. It exports `HomeDrawerAddServerRowExpandedChildren`.
- Functions 78617 (React Compiler) and 78618 (fallback) both render a `HomeDrawerSharedItem` with a title generated from the same localized string. They do not contain the actual press action in the decompiled body.
- Functions 78615 (React Compiler) and 78616 (fallback) are `GuildsBarCreateJoinButton`. They consume `HomeDrawerAddServerRowExpandedChildren`, render a circle-plus button, and pass an `onPress` callback. In function 78615 that callback is nested function F132199.
- Functions 78613/78614 are named create/join handler wrappers. The actual behavior is delegated into nested functions, so these wrappers alone do not prove which action-sheet branches are shared.

**Decision:** do not hide `HomeDrawerAddServerRowExpandedChildren`, `GuildsBarCreateJoinButton`, or the shared create/join handler. The current artifact does not prove that a separate Discovery-only child exists inside this affordance.

### Invite route constants

The route-constants factory decompilation (function 1089) defines invite route properties separately:
- `INVITE`
- `INVITE_LOGIN`
- `INVITE_REGISTER`
- `INVITE_PROXY`

The Discovery route keys listed above are distinct properties. The current `redirectDiscoveryRoutes` helper does not include any of these invite properties, nor `GUILD_CREATE`.

This separation is positive static evidence that the route helper does not directly rewrite the invite route constants. It is not yet proof that invite acceptance works end-to-end: route callers, deep-link handling, and the shared create/join press handler still need tracing and runtime checks.

## Other surfaces and why they are not blanket targets

### Global server discovery

- `GLOBAL_DISCOVERY_SERVERS` xrefs are concentrated in the route/constants factory, server-discovery constants/stores/actions, the featured manager, and related utilities.
- Function 19421 is the `GlobalDiscoveryServersFeaturedSearchManager` module factory.
- Functions 15051–15053 are search-count/layout/results stores.
- Function 17957 exports guild discovery category metadata actions; 17958 is the category store.
- Function 162026 is a server-discovery action and 162027 is the search action.
- The xref report has no literal `/discovery/servers` string hit outside route constants; route identity is represented by the exported route key rather than repeated path strings.

The manager patch suppresses the featured feed. The route patch redirects the main route. Search stores/actions remain in the bundle; do not blanket-stub shared stores or analytics without proving all callers are Discovery-only.

### App directory

- Function 1089 is the route/constants module. It defines `/discovery/applications`, `/application-directory`, their search routes, and profile/category route builders.
- Function 1096 defines app-directory tab/category constants.
- Functions 12081–12088 are app-directory stores and action creators. Their exports include application lookup, embed-application lookup, categories, similar applications, search, collections, and guild integration-application IDs.
- Function 12150 is an application-directory store.
- Function 38673 reads `fromType` and references the global app-directory module.

These functions show that the app-directory subsystem includes more than a browse screen. In particular, application lookup and guild integration IDs may support command/app experiences that DiscordZero should preserve. The current route redirects are a narrower first step; do not disable the stores/action creators wholesale.

### Guild action sheet / guild directory

- Functions 15193 and 15253 are module factories for guild action-sheet directory components.
- Functions 70475/70476 implement `GuildActionSheetDirectoryActions`; the decompilation includes ordinary guild actions such as message-request privacy and leave-server behavior, not just Discovery.
- Functions 70598/70599 render `GuildActionSheetDirectory` using those actions.

**Decision:** do not remove the guild action sheet or its directory actions as part of global Discovery removal. Its mixed ownership makes broad removal unsafe.

### Legacy guild-discovery route needs separate tracing

Function 1089 also defines `GUILD_DISCOVERY` as `/guild-discovery`. This key is **not** included in the current `redirectDiscoveryRoutes` allowlist.

The `GUILD_DISCOVERY` xref report includes function 32811 (`handleGuildJoin`) as well as discovery analytics and guild-discovery metadata functions. That makes this route ambiguous until the handler is decompiled: it may participate in a join path, so it must not be redirected based on the route name alone.

## Minimal patch direction

1. Keep the existing featured-manager suppression.
2. Keep the current route redirects for the explicit global server/app discovery and app-directory routes.
3. Preserve all invite route keys and `GUILD_CREATE`.
4. Do not patch the add-server row, `GuildsBarCreateJoinButton`, create/join handler, guild action sheet, or app-directory stores/actions at this stage.
5. Trace the nested press handler and the `GUILD_DISCOVERY` references before considering any additional route or entry-point patch.
6. Only add a UI-entry patch if the decompilation proves a distinct Discovery-only control that does not share invite/create behavior.

## Next inspection targets

The inspect workflow has been extended to decompile:
- F132197, F132198, F132199 — nested create/join press handler path from `GuildsBarCreateJoinButton`
- 32811 — `handleGuildJoin`, which references `GUILD_DISCOVERY`
- 1362, 6843, 7799, 38673 — global app-directory entry points and `fromType` use
- 23821–23824 — dynamic app-directory route builders

It also now records xrefs for `INVITE`, `INVITE_PROXY`, `GUILD_CREATE`, `GUILD_DISCOVERY`, app-directory search routes, and create/join symbols.

## Required validation before calling Discovery removal finished

### CI / static
- The new inspect run must complete and the decompilation of F132199 and function 32811 must be reviewed.
- Reseam must continue to report unique target matches and successful application.
- The APK must pass alignment, signature, manifest, and package verification.

### Device / runtime
- Launch and login.
- Open the add-server UI.
- Complete joining by invite deep link and invite code.
- Complete create-server flow.
- Confirm global server discovery and app-directory routes return safely to DM home.
- Confirm no broken back navigation or crash when opening the add-server UI.
- Verify ordinary guild switching/navigation, messages, notifications, uploads, and voice.
- Compare invite joining against stock/unpatched 352.17.

Until the runtime checks pass, status remains **route/feed patches CI-validated; invite preservation statically scoped but not device-validated**.
