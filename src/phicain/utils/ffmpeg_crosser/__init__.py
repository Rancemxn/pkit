import subprocess
import os
import typing

from loguru import logger

from ..libcheck import cmd
from ..syscheck import check_android

if check_android():
    logger.info("Android Platform detected. FFmpeg Patch Start.")

    _original_run: typing.Callable = subprocess.run
    _original_Popen: typing.Callable = subprocess.Popen

    from android import mActivity  # type: ignore

    app_info = mActivity.getApplicationInfo()
    native_lib_dir: str = app_info.nativeLibraryDir
    ffmpeg_bin_path: str = os.path.join(native_lib_dir, "libffmpegbin.so")
    logger.debug(f"FFmpeg bin locate in {ffmpeg_bin_path}")

    ld_library_path: str = (
        native_lib_dir + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    )
    os.environ["LD_LIBRARY_PATH"] = ld_library_path
    logger.debug("LD_LIBRARY PATCHED")

    def _patched_arg0(command: list[str] | str) -> list[str]:
        if isinstance(command, str):
            command = command.split()
        if isinstance(command, tuple):
            command = list(command)
        if command[0] == "ffmpeg":
            command[0] = ffmpeg_bin_path
        return command

    def _patched_run(*args, **kwargs):
        logger.debug(f"subprocess.run receive task [{args[0]}]")
        args = (_patched_arg0(args[0]),) + args[1:]
        logger.debug(f"Patch to {args}")
        return _original_run(*args, **kwargs)

    def _patched_Popen(*args, **kwargs):
        logger.debug(f"subprocess.Popen receive task [{args[0]}]")
        args = (_patched_arg0(args[0]),) + args[1:]
        logger.debug(f"Patch to {args}")
        return _original_Popen(*args, **kwargs)

    subprocess.run = _patched_run
    subprocess.Popen = _patched_Popen

    logger.info("FFmpeg Patch Done.")

logger.info("Test FFmpeg with '--version'")

cmd(["ffmpeg"])

cmd(["ffmpeg", "--version"])
