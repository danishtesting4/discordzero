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
