const PICKER_FEATURES = new Set(["emojisEverywhere", "stickersEverywhere"]);

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

export function isPickerUpsell(props: any) {
    return props != null && PICKER_FEATURES.has(props.featureName);
}
