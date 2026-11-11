import test from 'node:test';
import assert from 'node:assert/strict';

import {
  withStaticChatMediaOptions,
  hideExport,
  forceStaticAvatarDecoration,
  disableGifAutoPlay,
  disableDiscoveryManager,
  redirectDiscoveryRoutes,
} from '../patches/apps/discord/extensions/features/src/main/js/index.ts';

test('withStaticChatMediaOptions forces static chat media on object props', () => {
  const input = { options: { gifAutoPlay: true, animateEmoji: true, keep: 1 }, other: 2 };
  const output = withStaticChatMediaOptions(input);
  assert.notEqual(output, input);
  assert.notEqual(output.options, input.options);
  assert.deepEqual(output.options, { gifAutoPlay: false, animateEmoji: false, keep: 1 });
  assert.equal(output.other, 2);
  assert.deepEqual(input.options, { gifAutoPlay: true, animateEmoji: true, keep: 1 });
});

test('withStaticChatMediaOptions returns original for invalid shapes', () => {
  assert.equal(withStaticChatMediaOptions(null), null);
  assert.equal(withStaticChatMediaOptions(undefined), undefined);
  const noOptions = { foo: 1 };
  assert.equal(withStaticChatMediaOptions(noOptions), noOptions);
  const badOptions = { options: null };
  assert.equal(withStaticChatMediaOptions(badOptions), badOptions);
});

test('hideExport replaces named export with null-returning component', () => {
  const exportsObj = { default: () => 'promo', keep: 1 };
  const out = hideExport(exportsObj, 'default');
  assert.equal(out, exportsObj);
  assert.equal(typeof exportsObj.default, 'function');
  assert.equal(exportsObj.default(), null);
  assert.equal(exportsObj.keep, 1);
});

test('hideExport is safe for invalid inputs', () => {
  assert.equal(hideExport(null, 'default'), null);
  assert.equal(hideExport(undefined, 'default'), undefined);
});

test('forceStaticAvatarDecoration wraps getAvatarDecorationURL and preserves default export ref', () => {
  const calls = [];
  const original = (opts) => { calls.push(opts); return { ...opts, url: 'x' }; };
  const defaultExports = { getAvatarDecorationURL: original, other: 1 };
  const exportsObj = { getAvatarDecorationURL: original, default: defaultExports };
  const out = forceStaticAvatarDecoration(exportsObj);
  assert.equal(out, exportsObj);
  const result = exportsObj.getAvatarDecorationURL({ canAnimate: true, id: 1 });
  assert.deepEqual(calls[0], { canAnimate: false, id: 1 });
  assert.deepEqual(result, { canAnimate: false, id: 1, url: 'x' });
  // default export function ref updated
  const result2 = defaultExports.getAvatarDecorationURL({ canAnimate: true });
  assert.deepEqual(result2, { canAnimate: false, url: 'x' });
  assert.equal(defaultExports.other, 1);
});

test('forceStaticAvatarDecoration leaves non-object options untouched except call-through', () => {
  const calls = [];
  const original = (opts) => { calls.push(opts); return opts; };
  const exportsObj = { getAvatarDecorationURL: original };
  forceStaticAvatarDecoration(exportsObj);
  exportsObj.getAvatarDecorationURL('raw');
  assert.deepEqual(calls, ['raw']);
});

test('forceStaticAvatarDecoration is no-op without target function', () => {
  const exportsObj = { getAvatarDecorationURL: 1 };
  const out = forceStaticAvatarDecoration(exportsObj);
  assert.equal(out, exportsObj);
  assert.equal(exportsObj.getAvatarDecorationURL, 1);
});

test('disableGifAutoPlay overrides GifAutoPlay getters', () => {
  const exportsObj = { GifAutoPlay: { useSetting: () => true, getSetting: () => true } };
  const out = disableGifAutoPlay(exportsObj);
  assert.equal(out, exportsObj);
  assert.equal(exportsObj.GifAutoPlay.useSetting(), false);
  assert.equal(exportsObj.GifAutoPlay.getSetting(), false);
});

test('disableGifAutoPlay is safe for missing/invalid setting', () => {
  assert.doesNotThrow(() => disableGifAutoPlay({}));
  assert.doesNotThrow(() => disableGifAutoPlay({ GifAutoPlay: null }));
  assert.equal(disableGifAutoPlay(null), null);
});

test('disableDiscoveryManager disables featured fetch manager safely', async () => {
  let cleared = 0;
  let postCalled = 0;
  const manager = {
    isFetchEnabled: true,
    handleConnectionOpen: () => { throw new Error('should not run'); },
    actions: { POST_CONNECTION_OPEN: () => { postCalled++; } },
    async *fetchFeaturedGuilds() { yield 1; },
    async *fetchCategoryFeaturedGuilds() { yield 2; },
    queue: { clear: () => { cleared++; } },
  };
  const exportsObj = { default: manager };
  const out = disableDiscoveryManager(exportsObj);
  assert.equal(out, exportsObj);
  assert.equal(manager.isFetchEnabled, false);
  assert.equal(manager.handleConnectionOpen(), undefined);
  assert.equal(manager.actions.POST_CONNECTION_OPEN(), undefined);
  assert.equal(postCalled, 0);
  const a = await manager.fetchFeaturedGuilds().next();
  const b = await manager.fetchCategoryFeaturedGuilds().next();
  assert.deepEqual(a, { value: undefined, done: true });
  assert.deepEqual(b, { value: undefined, done: true });
  assert.equal(cleared, 1);
});

test('disableDiscoveryManager is safe for invalid inputs', () => {
  assert.equal(disableDiscoveryManager(null), null);
  assert.doesNotThrow(() => disableDiscoveryManager({}));
  assert.doesNotThrow(() => disableDiscoveryManager({ default: null }));
});

test('redirectDiscoveryRoutes redirects fixed and dynamic discovery routes only', () => {
  const originalRoutes = {
    GLOBAL_DISCOVERY: '/discovery/servers',
    GLOBAL_DISCOVERY_SERVERS: '/discovery/servers',
    GLOBAL_DISCOVERY_APPS: '/discovery/applications',
    GLOBAL_DISCOVERY_APPS_SEARCH: '/discovery/applications/search',
    APPLICATION_DIRECTORY: '/application-directory',
    APPLICATION_DIRECTORY_SEARCH: '/application-directory/search',
    GLOBAL_DISCOVERY_APPS_CATEGORY: (id) => `/discovery/applications/categories/${id}`,
    GLOBAL_DISCOVERY_APPS_PROFILE: (id) => `/discovery/applications/${id}`,
    GLOBAL_DISCOVERY_APPS_PROFILE_SECTION: (id, s) => `/discovery/applications/${id}/${s}`,
    GLOBAL_DISCOVERY_APPS_PROFILE_STORE_SKU: (id, sku) => `/discovery/applications/${id}/store/${sku}`,
    APPLICATION_DIRECTORY_PROFILE: (id) => `/application-directory/${id}`,
    APPLICATION_DIRECTORY_PROFILE_SECTION: (id, s) => `/application-directory/${id}/${s}`,
    APPLICATION_DIRECTORY_PROFILE_STORE_SKU: (id, sku) => `/application-directory/${id}/store/${sku}`,
    INVITE: '/invite/:code',
    INVITE_LOGIN: '/invite/:code/login',
    INVITE_REGISTER: '/invite/:code/register',
    INVITE_PROXY: (code) => `/invite/${code}`,
    GUILD_CREATE: '/guilds/create',
    CHANNEL: (guildId, channelId) => `/channels/${guildId}/${channelId}`,
  };
  const exportsObj = { Routes: originalRoutes };
  const out = redirectDiscoveryRoutes(exportsObj);
  assert.equal(out, exportsObj);
  const r = exportsObj.Routes;
  assert.notEqual(r, originalRoutes); // proxied
  assert.equal(r.GLOBAL_DISCOVERY, '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_SERVERS, '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS, '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS_SEARCH, '/channels/@me');
  assert.equal(r.APPLICATION_DIRECTORY, '/channels/@me');
  assert.equal(r.APPLICATION_DIRECTORY_SEARCH, '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS_CATEGORY('x'), '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS_PROFILE('x'), '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS_PROFILE_SECTION('x','y'), '/channels/@me');
  assert.equal(r.GLOBAL_DISCOVERY_APPS_PROFILE_STORE_SKU('x','y'), '/channels/@me');
  assert.equal(r.APPLICATION_DIRECTORY_PROFILE('x'), '/channels/@me');
  assert.equal(r.APPLICATION_DIRECTORY_PROFILE_SECTION('x','y'), '/channels/@me');
  assert.equal(r.APPLICATION_DIRECTORY_PROFILE_STORE_SKU('x','y'), '/channels/@me');
  // protected/shared routes untouched
  assert.equal(r.INVITE, '/invite/:code');
  assert.equal(r.INVITE_LOGIN, '/invite/:code/login');
  assert.equal(r.INVITE_REGISTER, '/invite/:code/register');
  assert.equal(r.INVITE_PROXY('abc'), '/invite/abc');
  assert.equal(r.GUILD_CREATE, '/guilds/create');
  assert.equal(r.CHANNEL('1','2'), '/channels/1/2');
});

test('redirectDiscoveryRoutes is safe for invalid inputs', () => {
  assert.equal(redirectDiscoveryRoutes(null), null);
  assert.doesNotThrow(() => redirectDiscoveryRoutes({}));
  assert.doesNotThrow(() => redirectDiscoveryRoutes({ Routes: null }));
});
