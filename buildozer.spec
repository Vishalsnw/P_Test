[app]
title = YouTube Limiter
package.name = youtubelimiter
package.domain = org.parentalcontrol

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,xml

version = 1.3.3
p4a.branch = develop

requirements = python3,kivy,pyjnius,android

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,SYSTEM_ALERT_WINDOW,PACKAGE_USAGE_STATS,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,FOREGROUND_SERVICE_SPECIAL_USE,BIND_DEVICE_ADMIN,GET_TASKS,WAKE_LOCK,FOREGROUND_SERVICE_DATA_SYNC

android.ndk = 28
android.api = 35
android.minapi = 21
android.ndk_api = 21
android.sdk = 35
android.gradle_version = 8.9

# Linker flags for 16KB page support (ELF alignment)
android.extra_linker_flags = -Wl,-z,max-page-size=16384

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
