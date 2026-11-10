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
