[app]
title = سفینه نادری
package.name = spaceshooter
package.domain = org.ostadnaderi
source.dir = .
source.include_exts = py,png,jpg,ttf
version = 0.4
requirements = python3,pygame-ce==2.4.0
orientation = portrait
fullscreen = 0
android.api = 30
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.exported_activities = org.kivy.android.PythonActivity
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
p4a.branch = master
[buildozer]
log_level = 2
warn_on_root = 0
