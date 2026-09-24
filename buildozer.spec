[app]
title = سفینه نادری
package.name = spaceshooter
package.domain = org.ostadnaderi
source.dir = .
source.include_exts = py,png,jpg,ttf
version = 0.5
requirements = python3,pygame-ce==2.4.0
orientation = portrait
fullscreen = 0
android.api = 31
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.exported_activities = org.kivy.android.PythonActivity
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.entrypoint = org.kivy.android.PythonActivity
p4a.branch = master
p4a.bootstrap = sdl2
[buildozer]
log_level = 2
warn_on_root = 0
