[app]
title = Phicain

package.name = pkit

package.domain = org.Rancemxn

source.dir = src/phicain

source.include_exts = py, ttf

source.exclude_dirs = __pycache__

version.regex = __version__ = ['"](.*)['"]

version.filename = %(source.dir)s/__init__.py

requirements = python3,hostpython3,kivy,android,ffmpeg_bin,pyjnius,requests,pysmartdl2,urllib3,loguru,vgmstream

orientation = landscape, landscape-reverse

fullscreen = 1

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 29

android.minapi = 29

android.ndk = 25c

android.ndk_api = 29

android.accept_sdk_license = True

android.logcat_filters = *:S python:D

android.archs = arm64-v8a

android.allow_backup = True

p4a.local_recipes = receipe

p4a.bootstrap = sdl2



p4a.url = https://github.com/PitRc47/python-for-android

p4a.branch = main

[buildozer]
log_level = 2

warn_on_root = 0