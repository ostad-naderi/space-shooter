[app]
title = سفینه نادری
package.name = spaceshooter
package.domain = org.ostadnaderi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0

requirements = python3,kivy==2.2.1,pygame-ce

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.exported_activities = org.kivy.android.PythonActivity

# *** برنچ معتبر و سازگار با پایتون ۳.۱۰ ***
p4a.branch = v2023.09.16

[buildozer]
log_level = 2
warn_on_root = 0
