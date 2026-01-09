[app]
title = YouTube Limiter
package.name = youtubelimiter
package.domain = org.parentalcontrol

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,xml

version = 1.2.0

requirements = python3,kivy,pyjnius,android

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,SYSTEM_ALERT_WINDOW,PACKAGE_USAGE_STATS,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,FOREGROUND_SERVICE_SPECIAL_USE,BIND_DEVICE_ADMIN,GET_TASKS,WAKE_LOCK

android.api = 35
android.minapi = 21
android.ndk = 25b
android.sdk = 35

android.accept_sdk_license = True

android.arch = arm64-v8a

android.allow_backup = True

presplash.filename = presplash.png

icon.filename = icon.png

android.manifest = AndroidManifest.xml

android.add_src = java

android.add_resources = res

services = TimerService:service/main.py:foreground

android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
