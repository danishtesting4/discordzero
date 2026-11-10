exports.forceStaticAvatarDecoration = function (original, options) {
    if (options == null || typeof options !== "object") {
        return original(options);
    }

    return original({
        ...options,
        canAnimate: false,
    });
};
