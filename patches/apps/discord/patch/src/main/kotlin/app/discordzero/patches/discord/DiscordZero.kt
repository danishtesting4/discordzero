package app.discordzero.patches.discord

import app.reseam.discord.bindings.Features
import app.reseam.patch.after
import app.reseam.patch.before
import app.reseam.patch.function
import app.reseam.patch.patch
import app.reseam.patch.replace

private val setPrefersReducedMotion = function {
    strings("ACCESSIBILITY_SET_PREFERS_REDUCED_MOTION", "REDUCED_MOTION")
    paramCount(1)
}

private val getAvatarDecorationURL = function {
    strings("canAnimate", "ANIMATED", "STATIC")
    paramCount(1)
}

private val useNitroFileUploadAnnouncementEligible = function {
    strings("useNitroFileUploadRolloutEnabled")
    paramCount(1)
}

private val useNitroFileUploadUpsellEligible = function {
    strings("useNonNitroFileUploadMarketingEnabled")
    paramCount(1)
}

private val nitroUpsellButton = function {
    strings("experimental_premium-primary", "NitroWheelIcon")
    paramCount(1)
}

private val premiumFeatureUpsellPill = function {
    strings("native.PremiumFeatureUpsell", "featureName", "ShinyButton")
    paramCount(1)
}

private val premiumExpressionPickerSearchUpsell = function {
    strings("ctaText", "PressableOpacity", "upsell")
    paramCount(1)
}

private val premiumFeatureUpsell = function {
    strings("featureName", "useAnalyticsContext", "shouldShow")
    paramCount(1)
}

private val premiumUpsellAlert = function {
    strings("Nitro Upsell", "PREMIUM_UPSELL_ALERT")
    paramCount(1)
}

private val nitroUpsell = function {
    strings("subscribeNowPressable")
    paramCount(1)
}

private val nitroFileUploadUpsellPromoSheet = function {
    strings("markAsDismissed", "AUTO_DISMISS")
    paramCount(1)
}

private val premiumTrialOfferActionSheetContent = function {
    strings("subscriptionTrial", "NitroWumpusFlightRight3dIllustration")
    paramCount(1)
}

private val premiumDiscountOfferActionSheetContent = function {
    strings("discountOffer", "NitroWumpusFlightRight3dIllustration")
    paramCount(1)
}

val reduceAutomaticAnimations = patch("Reduce automatic animations") {
    description("Disables GIF and banner autoplay, uses static avatar decorations, and keeps manual banner playback available.")
    compatibleWith("com.discord")

    execute {
        setPrefersReducedMotion.before {
            param(0).assign(bool(true))
        }

        getAvatarDecorationURL.before {
            param(0).assign(Features.withStaticAvatarDecoration(param(0)))
        }
    }
}

val removeNitroPromotions = patch("Remove Nitro promotions") {
    description("Suppresses Nitro upload marketing, picker promotions, upsell buttons, and trial or discount offer surfaces.")
    compatibleWith("com.discord")

    execute {
        useNitroFileUploadAnnouncementEligible.after {
            result.assign(bool(false))
        }

        useNitroFileUploadUpsellEligible.after {
            result.assign(bool(false))
        }

        nitroUpsellButton.replace {
            returnNull()
        }

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

        premiumUpsellAlert.replace {
            returnNull()
        }

        nitroUpsell.replace {
            returnNull()
        }

        nitroFileUploadUpsellPromoSheet.replace {
            returnNull()
        }

        premiumTrialOfferActionSheetContent.replace {
            returnNull()
        }

        premiumDiscountOfferActionSheetContent.replace {
            returnNull()
        }
    }
}
