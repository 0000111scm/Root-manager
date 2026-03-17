[app]
title = Root Cleaner
package.name = rootcleaner
package.domain = org.example
source.dir = .
source.include_exts = py
version = 0.1
requirements = python3,kivy
orientation = portrait

[buildozer]
log_level = 2

[android]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.arch = arm64-v8a
