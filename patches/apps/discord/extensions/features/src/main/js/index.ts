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
