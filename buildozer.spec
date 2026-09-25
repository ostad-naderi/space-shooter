[app]
title = سفینه نادری
package.name = spaceshooter
package.domain = org.ostadnaderi

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,wav,mp3
version = 2.1

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
