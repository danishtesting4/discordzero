package app.discordzero.patches.discord

import app.reseam.patch.ExtJsModule
import app.reseam.patch.after
import app.reseam.patch.before
import app.reseam.patch.export
import app.reseam.patch.function
import app.reseam.patch.patch
import app.reseam.patch.wrap

private object Features : ExtJsModule("discord-features") {
    val forceStaticAvatarDecoration by export()
}

private val setPrefersReducedMotion = function {
    name("setPrefersReducedMotion")
    strings("ACCESSIBILITY_SET_PREFERS_REDUCED_MOTION", "REDUCED_MOTION")
    paramCount(1)
}

private val getAvatarDecorationURL = function {
    name("getAvatarDecorationURL")
    strings("canAnimate", "ANIMATED", "STATIC")
    paramCount(1)
}

private val useNitroFileUploadAnnouncementEligible = function {
    name("useNitroFileUploadAnnouncementEligible")
    strings("useNitroFileUploadRolloutEnabled")
    paramCount(1)
}

private val useNitroFileUploadUpsellEligible = function {
    name("useNitroFileUploadUpsellEligible")
    strings("useNonNitroFileUploadMarketingEnabled")
    paramCount(1)
}

private val nitroUpsellButton = function {
    name("NitroUpsellButton")
    strings("experimental_premium-primary", "NitroWheelIcon")
    paramCount(1)
}

private val premiumUpsellAlert = function {
    name("PremiumUpsellAlert")
    strings("Nitro Upsell", "PREMIUM_UPSELL_ALERT")
    paramCount(1)
}

private val nitroUpsell = function {
    name("NitroUpsell")
    strings("subscribeNowPressable")
    paramCount(1)
}

private val nitroFileUploadUpsellPromoSheet = function {
    name("NitroFileUploadUpsellPromoSheet")
    strings("markAsDismissed", "AUTO_DISMISS")
    paramCount(1)
}

private val premiumTrialOfferActionSheetContent = function {
    name("PremiumTrialOfferActionSheetContent")
    strings("subscriptionTrial", "NitroWumpusFlightRight3dIllustration")
    paramCount(1)
}

private val premiumDiscountOfferActionSheetContent = function {
    name("PremiumDiscountOfferActionSheetContent")
    strings("discountOffer", "NitroWumpusFlightRight3dIllustration")
    paramCount(1)
}

val reduceAutomaticAnimations = patch("Reduce automatic animations") {
    description("Disables autoplay and uses static avatar decorations while keeping manual banner playback available.")
    compatibleWith("com.discord")

    execute {
        setPrefersReducedMotion.before {
            param(0).assign(bool(true))
        }

        getAvatarDecorationURL.wrap(Features.forceStaticAvatarDecoration)
    }
}

val removeNitroPromotions = patch("Remove Nitro promotions") {
    description("Suppresses Nitro upload marketing, upsell dialogs, and trial or discount offer surfaces.")
    compatibleWith("com.discord")

    execute {
        useNitroFileUploadAnnouncementEligible.after {
            result.assign(bool(false))
        }

        useNitroFileUploadUpsellEligible.after {
            result.assign(bool(false))
        }

        nitroUpsellButton.alwaysReturnNull()
        premiumUpsellAlert.alwaysReturnNull()
        nitroUpsell.alwaysReturnNull()
        nitroFileUploadUpsellPromoSheet.alwaysReturnNull()
        premiumTrialOfferActionSheetContent.alwaysReturnNull()
        premiumDiscountOfferActionSheetContent.alwaysReturnNull()
    }
}
