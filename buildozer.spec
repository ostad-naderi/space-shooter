[app]
title = Space Shooter Ostad Naderi
package.name = spaceshooter
package.domain = org.ostadnaderi

source.dir = .
source.include_exts = py
version = 0.1

requirements = python3,pygame-ce

orientation = portrait
fullscreen = 1

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
