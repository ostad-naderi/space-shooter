[app]
title = Space Shooter Ostad Naderi
package.name = spaceshooter
package.domain = org.ostadnaderi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3==3.10.12,kivy==2.3.0,pygame-ce

orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

android.allow_backup = True
android.accept_sdk_license = True
android.p4a_branch = develop

[buildozer]
log_level = 2
warn_on_root = 0
