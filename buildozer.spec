[app]
title = Phicain

package.name = pkit

package.domain = org.Rancemxn

source.dir = src/phicain

source.include_exts = py

source.exclude_dirs = __pycache__

version.regex = __version__ = ['"](.*)['"]

version.filename = %(source.dir)s/__init__.py

requirements = \
    python3,\
    hostpython3,\
    sdl3,\
    android,\
    ffmpeg_bin,\
    pyjnius,\
    requests >= 2.32.3,\
    pysmartdl2 >= 2.0.1,\
    urllib3 >= 2.4.0,\
    loguru == 0.7.*

orientation = landscape, landscape-reverse

fullscreen = 1

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 33

android.minapi = 29

android.ndk = 27c

android.ndk_api = 29

android.accept_sdk_license = True

android.logcat_filters = *:S python:D

android.archs = arm64-v8a

android.allow_backup = True

p4a.local_recipes = receipe

p4a.bootstrap = sdl3

p4a.fork = Rancemxn

p4a.branch = develop

[buildozer]
log_level = 2

warn_on_root = 0