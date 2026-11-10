const PICKER_FEATURES = new Set(["emojisEverywhere", "stickersEverywhere"]);

export function withStaticAvatarDecoration(options: any) {
    if (options == null || typeof options !== "object") {
        return options;
    }

    return {
        ...options,
        canAnimate: false,
    };
}

export function isPickerUpsell(props: any) {
    return props != null && PICKER_FEATURES.has(props.featureName);
}
