__version__ = "0.2.0"

import subprocess
from android import mActivity  # type: ignore
from os.path import join

app_info = mActivity.getApplicationInfo()
native_lib_dir = app_info.nativeLibraryDir

ffmpeg_bin = join(native_lib_dir, "libffmpegbin.so")

print(
    subprocess.run(
        [ffmpeg_bin, "-version"], capture_output=True, text=True, check=True
    ).stdout
)

while True:
    pass
