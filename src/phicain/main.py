# __version__ = "0.2.0" # 你的版本号定义
# 通常版本号定义在项目的 __init__.py 文件中更规范，Buildozer 也可以配置从那里读取

import subprocess
import os  # 导入 sys 用于打印到 stderr
from android import mActivity  # type: ignore # 忽略 android 库的类型检查错误
from os.path import join

# 通常在项目入口文件会导入其他模块或启动主应用逻辑
# from phicain.main import main_app # 示例：如果你的主应用逻辑在一个 Typer 应用中


def get_ffmpeg_android_path():
    """在 Android 环境中获取打包好的 ffmpeg 可执行文件路径"""
    try:
        # 获取应用信息
        app_info = mActivity.getApplicationInfo()
        # 获取原生库目录
        native_lib_dir = app_info.nativeLibraryDir
        # 构建 ffmpeg 可执行文件的完整路径 (根据配方将其命名为 libffmpegbin.so)
        ffmpeg_bin_path = join(native_lib_dir, "libffmpegbin.so")

        if not os.path.exists(ffmpeg_bin_path):
            print(f"FFmpeg executable not found in native lib dir: {ffmpeg_bin_path}")
            return None

        print(f"Detected FFmpeg path: {ffmpeg_bin_path}")
        return ffmpeg_bin_path

    except Exception as e:
        print(f"Error getting FFmpeg path on Android: {e}")
        return None


def test_ffmpeg_version():
    """
    尝试运行 'ffmpeg -version' 命令并捕获输出，用于诊断错误。
    """
    ffmpeg_path = get_ffmpeg_android_path()

    if not ffmpeg_path:
        print("FFmpeg path not available. Cannot run version test.")
        return

    print(f"Running command: [{ffmpeg_path}, -version]")

    try:
        # 运行 FFmpeg 命令并捕获输出
        # check=False 这样即使返回非零退出码也不会立即抛出异常，
        # 我们可以先查看 stderr 输出
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,  # 解码输出为文本
            check=False,  # <--- 将 check 设置为 False
        )

        # 检查返回码
        if result.returncode != 0:
            print(
                f"Command '{' '.join(result.args)}' returned non-zero exit status {result.returncode}."
            )
            print("--- FFmpeg stdout ---")
            print(result.stdout)
            print("--- FFmpeg stderr ---")
            print(result.stderr)  # <--- 打印标准错误
            print("---------------------")
        else:
            # 如果成功，打印标准输出
            print(f"Command '{' '.join(result.args)}' executed successfully.")
            print("--- FFmpeg stdout ---")
            print(result.stdout)
            print("---------------------")

    except FileNotFoundError:
        print(
            f"Error: FFmpeg executable not found at {ffmpeg_path}. Check if it was packaged correctly."
        )
    except Exception as e:
        print(f"An unexpected error occurred during FFmpeg version test: {e}")


# ==== 程序入口 ====
# 在 Android 应用启动时，通常会执行这里的代码
if __name__ == "__main__":
    # 在这里调用你的测试函数
    from android import mActivity  # type: ignore

    app_info = mActivity.getApplicationInfo()
    native_lib_dir = (
        app_info.nativeLibraryDir
    )  # 这个就是 /data/app/.../lib/arm64 这样的路径

    # 获取当前的 LD_LIBRARY_PATH，如果不存在则为空字符串
    current_ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
    # 将原生库目录添加到 LD_LIBRARY_PATH 的前面
    new_ld_library_path = native_lib_dir + os.pathsep + current_ld_library_path
    # 更新环境变量
    os.environ["LD_LIBRARY_PATH"] = new_ld_library_path
    test_ffmpeg_version()

    # 如果你的应用是 Kivy/或其他有主循环的框架，可能需要启动主循环
    # 如果只是一个运行后就退出的后台脚本，可以移除 while True: pass

    # 示例：如果你的主应用逻辑在 main_app 函数中
    # main_app() # 调用你的主应用入口函数

    # 如果应用只是运行一次命令就结束，不需要无限循环
    # while True: # 如果应用需要持续运行，例如 Kivy 应用的主循环
    #     pass

    # For a simple script that runs and exits:
    print("Script finished.")
    # Exit the process if necessary
    # import os
    # os._exit(0) # Use os._exit() for a clean exit in some Android contexts
