package app.discordzero.patches.discord

import app.reseam.discord.bindings.Features
import app.reseam.patch.after
import app.reseam.patch.before
import app.reseam.patch.function
import app.reseam.patch.patch

private val createMessageContent = function {
    name("createMessageContent")
    strings("renderGiftCode", "animatingStickerMessageId", "createActivityInstanceEmbed")
    paramCount(1)
}

private val premiumFeatureUpsellModule = function {
    strings("modules/premium/roadblocks/native/views/PremiumFeatureUpsell.tsx")
    paramCount(7)
}

private val premiumExpressionPickerFeatureUpsellModule = function {
    strings("modules/premium/roadblocks/native/views/PremiumExpressionPickerFeatureUpsell.tsx")
    paramCount(7)
}

private val premiumExpressionPickerSearchUpsellModule = function {
    strings("modules/premium/roadblocks/native/views/PremiumExpressionPickerSearchUpsell.tsx")
    paramCount(7)
}

private val emojiPickerPremiumSearchUpsellModule = function {
    strings("modules/emoji_picker/native/components/EmojiPickerPremiumSearchUpsell.tsx")
    paramCount(7)
}

private val stickerPickerPremiumSearchUpsellModule = function {
    strings("modules/stickers/native/StickerPickerPremiumSearchUpsell.tsx")
    paramCount(7)
}

private val userSettingsModule = function {
    strings("GifAutoPlay", "gifAutoPlay")
    paramCount(7)
}

private val avatarUtilsModule = function {
    strings("utils/AvatarUtils.tsx")
    paramCount(7)
}

private val globalDiscoveryFeaturedManagerModule = function {
    strings("modules/global_discovery_servers/GlobalDiscoveryServersFeaturedSearchManager.tsx")
    paramCount(7)
}

private val routeConstantsModule = function {
    strings("modules/routing/RouteConstants.tsx")
    paramCount(7)
}

private val nitroFileUploadUpsellPromoSheetModule = function {
    strings("modules/premium/file_upload/native/NitroFileUploadUpsellPromoSheet.tsx")
    paramCount(7)
}

private val premiumTrialOfferActionSheetModule = function {
    strings("modules/premium/native/trials/PremiumTrialOfferActionSheet.tsx")
    paramCount(7)
}

private val premiumDiscountOfferActionSheetModule = function {
    strings("modules/premium/native/discounts/PremiumDiscountOfferActionSheet.tsx")
    paramCount(7)
}

val staticChatMedia = patch("Disable automatic chat media animation") {
    description("Disables automatic GIF playback and animated emoji in message content.")
    compatibleWith("com.discord")

    execute {
        createMessageContent.before {
            param(0).assign(Features.withStaticChatMediaOptions(param(0)))
        }
    }
}

val staticProfileMedia = patch("Disable automatic profile media animation") {
    description("Turns off GIF autoplay for profile banners and uses static avatar-decoration assets; manual banner playback remains available.")
    compatibleWith("com.discord")

    execute {
        userSettingsModule.after {
            param(5).assign(Features.disableGifAutoPlay(param(5)))
        }

        avatarUtilsModule.after {
            param(5).assign(Features.forceStaticAvatarDecoration(param(5)))
        }
    }
}

val disableDiscoveryRoutes = patch("Disable Discovery routes") {
    description("Redirects public server and application discovery routes to the DM home.")
    compatibleWith("com.discord")

    execute {
        routeConstantsModule.after {
            param(5).assign(Features.redirectDiscoveryRoutes(param(5)))
        }
    }
}

val disableServerDiscovery = patch("Disable server discovery requests") {
    description("Disables featured server discovery fetches and their connection-open trigger.")
    compatibleWith("com.discord")

    execute {
        globalDiscoveryFeaturedManagerModule.after {
            param(5).assign(Features.disableDiscoveryManager(param(5)))
        }
    }
}

val removeNitroPromotions = patch("Remove Nitro promotions") {
    description("Removes Nitro promotion components from the emoji and sticker pickers.")
    compatibleWith("com.discord")

    execute {
        premiumFeatureUpsellModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }

        premiumExpressionPickerFeatureUpsellModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }

        premiumExpressionPickerSearchUpsellModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }

        emojiPickerPremiumSearchUpsellModule.after {
            param(5).assign(Features.hideExport(param(5), string("PremiumSearchUpsell")))
        }

        stickerPickerPremiumSearchUpsellModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }
    }
}

val removeNitroOfferSheets = patch("Remove Nitro offer sheets") {
    description("Removes premium trial and discount offer action sheets.")
    compatibleWith("com.discord")

    execute {
        premiumTrialOfferActionSheetModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }

        premiumDiscountOfferActionSheetModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }
    }
}

val removeNitroFileUploadPromo = patch("Remove Nitro file upload upsell promo") {
    description("Removes the Nitro file upload upsell promo action sheet.")
    compatibleWith("com.discord")

    execute {
        nitroFileUploadUpsellPromoSheetModule.after {
            param(5).assign(Features.hideExport(param(5), string("default")))
        }
    }
}
