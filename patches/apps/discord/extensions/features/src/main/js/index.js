export function withStaticAvatarDecoration(options) {
    if (options == null || typeof options !== "object") {
        return options;
    }

    return {
        ...options,
        canAnimate: false,
    };
}
