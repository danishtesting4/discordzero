pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
        maven("https://git.reseam.app/api/packages/reseam/maven") {
            mavenContent { includeGroupAndSubgroups("app.reseam") }
        }
    }
}

plugins {
    id("app.reseam.workspace") version "0.30.0"
}

rootProject.name = "discordzero"
