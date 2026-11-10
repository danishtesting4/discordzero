package app.discordzero.patches.discord

import app.reseam.discord.bindings.Features
import app.reseam.patch.before
import app.reseam.patch.function
import app.reseam.patch.patch
import app.reseam.patch.replace

private val createMessageContent = function {
    name("createMessageContent")
    strings("renderGiftCode", "animatingStickerMessageId", "createActivityInstanceEmbed")
    paramCount(1)
}

private val premiumFeatureUpsellPill = function {
    name("PremiumFeatureUpsellPill")
    strings("native.PremiumFeatureUpsell", "featureName", "ShinyButton")
    paramCount(1)
}

private val premiumExpressionPickerSearchUpsell = function {
    name("PremiumExpressionPickerSearchUpsell")
    strings("ctaText", "PressableOpacity", "upsell")
    paramCount(1)
}

private val premiumFeatureUpsell = function {
    name("PremiumFeatureUpsell")
    strings("featureName", "useAnalyticsContext", "shouldShow")
    paramCount(1)
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

val removeNitroPromotions = patch("Remove Nitro promotions") {
    description("Hides Nitro upsell buttons and promotional surfaces in the emoji and sticker pickers.")
    compatibleWith("com.discord")

    execute {
        premiumFeatureUpsellPill.replace {
            returnNull()
        }

        premiumExpressionPickerSearchUpsell.replace {
            returnNull()
        }

        premiumFeatureUpsell.before {
            whenTrue(Features.isPickerUpsell(param(0))) {
                returnNull()
            }
        }
    }
}
