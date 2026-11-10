const PICKER_FEATURES = new Set(["emojisEverywhere", "stickersEverywhere"]);

export function withStaticAvatarDecoration(options) {
    if (options == null || typeof options !== "object") {
        return options;
    }

    return {
        ...options,
        canAnimate: false,
    };
}

export function isPickerUpsell(props) {
    return props != null && PICKER_FEATURES.has(props.featureName);
}
