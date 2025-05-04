import os
import shutil
from os.path import join
from loguru import logger

from ...libcheck import cmd
from ...syscheck import check_android

vgm_bin_path: str = "vgmstream-cli"

if check_android():
    logger.info("Android Platform detected. Vgmstream Path Fix Start.")
    from android import mActivity  # type: ignore

    app_info = mActivity.getApplicationInfo()
    native_lib_dir: str = app_info.nativeLibraryDir
    vgm_bin_path = join(native_lib_dir, "libvgmstream-cli.so")
    logger.info(f"Found Vgmstream-cli locate in {vgm_bin_path}")

    vgmdir = join(mActivity.getFilesDir().getAbsolutePath(), "vgmstream")
    shutil.rmtree(vgmdir, ignore_errors=True)
    os.makedirs(vgmdir, exist_ok=True)

    built_libraries = [
        "libvgmstream-cli.so",
        "libvgmstream.so",
        "libvorbis_vgm.so",
        "libvorbisfile_vgm.so",
        "libogg_vgm.so",
        "libavcodec_vgm.so",
        "libavformat_vgm.so",
        "libavutil_vgm.so",
        "libswresample_vgm.so",
    ]
    for lib in built_libraries:
        shutil.copy2(join(native_lib_dir, lib), join(vgmdir, lib.replace("_vgm", "")))

    vgm_bin_path = join(vgmdir, "libvgmstream-cli.so")

    logger.info(f"Move to {vgm_bin_path}")

    os.environ["LD_LIBRARY_PATH"] = (
        vgmdir + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    )

    logger.debug(f"LD_LIBRARY_PATH update to: {os.environ.get('LD_LIBRARY_PATH', '')}")

    logger.info("LD_LIBRARY_PATH Patch Done.")

logger.info("Test Vgmstream")

cmd([vgm_bin_path, "-h"])
