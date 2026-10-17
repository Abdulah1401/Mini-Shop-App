[app]
title = MiniShop
package.name = minishop
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
version = 0.1.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True

android.presplash_color = #FF6B00
android.wakelock = 0
android.release_artifact = aab
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
