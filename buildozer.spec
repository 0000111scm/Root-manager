[app]
title = Root Cleaner
package.name = rootcleaner
package.domain = org.example
source.dir = .
source.include_exts = py,kv
version = 0.1
orientation = portrait
fullscreen = 0

requirements = python3,kivy
android.api = 34
android.minapi = 24
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.debug = 1

[buildozer]
log_level = 2
