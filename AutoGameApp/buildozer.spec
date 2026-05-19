[app]
title = Auto Game
package.name = autogame
package.domain = com.autogame
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Requirements
requirements = python3,kivy,pillow,numpy,opencv

# Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Icon
# icon.filename = %(source.dir)s/icon.png

# Log
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
