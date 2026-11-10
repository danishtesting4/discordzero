export function withStaticChatMediaOptions(props: any) {
    if (props == null || typeof props !== "object") {
        return props;
    }

    const options = props.options;
    if (options == null || typeof options !== "object") {
        return props;
    }

    return {
        ...props,
        options: {
            ...options,
            gifAutoPlay: false,
            animateEmoji: false,
        },
    };
}

export function hideExport(exports: any, exportName: string) {
    if (exports == null || typeof exports !== "object") {
        return exports;
    }

    exports[exportName] = function DiscordZeroHiddenPromotion() {
        return null;
    };

    return exports;
}

export function forceStaticAvatarDecoration(exports: any) {
    if (exports == null || typeof exports !== "object") {
        return exports;
    }

    const original = exports.getAvatarDecorationURL;
    if (typeof original !== "function") {
        return exports;
    }

    const staticDecorationURL = function (options: any) {
        if (options != null && typeof options === "object") {
            return original({
                ...options,
                canAnimate: false,
            });
        }

        return original(options);
    };

    exports.getAvatarDecorationURL = staticDecorationURL;

    const defaultExports = exports.default;
    if (defaultExports != null && typeof defaultExports === "object") {
        defaultExports.getAvatarDecorationURL = staticDecorationURL;
    }

    return exports;
}

export function disableGifAutoPlay(exports: any) {
    if (exports == null || typeof exports !== "object") {
        return exports;
    }

    const setting = exports.GifAutoPlay;
    if (setting != null && typeof setting === "object") {
        setting.useSetting = function () {
            return false;
        };
        setting.getSetting = function () {
            return false;
        };
    }

    return exports;
}

export function disableDiscoveryManager(exports: any) {
    if (exports == null || typeof exports !== "object") {
        return exports;
    }

    const manager = exports.default;
    if (manager == null || typeof manager !== "object") {
        return exports;
    }

    manager.isFetchEnabled = false;
    manager.handleConnectionOpen = function () {};
    if (manager.actions != null && typeof manager.actions === "object") {
        manager.actions.POST_CONNECTION_OPEN = function () {};
    }
    manager.fetchFeaturedGuilds = async function* () {};
    manager.fetchCategoryFeaturedGuilds = async function* () {};
    if (manager.queue != null && typeof manager.queue.clear === "function") {
        manager.queue.clear();
    }

    return exports;
}

export function redirectDiscoveryRoutes(exports: any) {
    if (exports == null || typeof exports !== "object") {
        return exports;
    }

    const routes = exports.Routes;
    if (routes == null || typeof routes !== "object") {
        return exports;
    }

    const home = "/channels/@me";
    const fixedRoutes = new Set([
        "GLOBAL_DISCOVERY",
        "GLOBAL_DISCOVERY_SERVERS",
        "GLOBAL_DISCOVERY_APPS",
        "GLOBAL_DISCOVERY_APPS_SEARCH",
        "APPLICATION_DIRECTORY",
        "APPLICATION_DIRECTORY_SEARCH",
    ]);
    const dynamicRoutes = new Set([
        "GLOBAL_DISCOVERY_APPS_CATEGORY",
        "GLOBAL_DISCOVERY_APPS_PROFILE",
        "GLOBAL_DISCOVERY_APPS_PROFILE_SECTION",
        "GLOBAL_DISCOVERY_APPS_PROFILE_STORE_SKU",
        "APPLICATION_DIRECTORY_PROFILE",
        "APPLICATION_DIRECTORY_PROFILE_SECTION",
        "APPLICATION_DIRECTORY_PROFILE_STORE_SKU",
    ]);

    exports.Routes = new Proxy(routes, {
        get(target, property, receiver) {
            if (typeof property === "string" && fixedRoutes.has(property)) {
                return home;
            }
            if (typeof property === "string" && dynamicRoutes.has(property)) {
                return function () {
                    return home;
                };
            }
            return Reflect.get(target, property, receiver);
        },
    });

    return exports;
}
