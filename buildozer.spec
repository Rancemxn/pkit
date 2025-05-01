[app]
title = Phicain

package.name = pkit

package.domain = org.Rancemxn

source.dir = src

source.include_exts = py

source.exclude_dirs = __pycache__

version.regex = __version__ = ['"](.*)['"]

version.filename = %(source.dir)s/main.py

requirements = python3,hostpython3,sdl3

orientation = landscape, landscape-reverse

fullscreen = 1

android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE

android.api = 31

android.minapi = 21

android.ndk_path = 

android.sdk_path =

android.skip_update = False

android.accept_sdk_license = True

android.apptheme = "@android:style/Theme.NoTitleBar"

android.logcat_filters = pkit:S python:D

android.archs = arm64-v8a

android.allow_backup = True

#p4a.local_recipes =

p4a.bootstrap = sdl3

p4a.branch = develop

[buildozer]
log_level = 2

warn_on_root = 0