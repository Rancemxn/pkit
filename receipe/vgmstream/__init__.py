from pythonforandroid.toolchain import Recipe, current_directory, shprint  # type: ignore
import sh  # type: ignore
import os


class VgmstreamRecipe(Recipe):
    name = "vgmstream"
    version = "r1980"
    url = f"https://github.com/vgmstream/vgmstream/archive/refs/tags/{version}.zip"

    depends = [
        "ffmpeg_bin",
        "libvorbis",
    ]

    # 声明需要 C++ STL 共享库
    need_stl_shared = True

    # 声明 vgmstream 编译后会生成的库文件及其相对路径（在 vgmstream 的构建目录中）
    # 根据 CMakeLists.txt 和构建目标 (libvgmstream_shared.so) 来确定
    # 文档提到输出可能在 build/src/libvgmstream.so
    # CMakeLists.txt 中提到 BUILD_SHARED 选项
    # 所以假设目标库是 libvgmstream_shared.so，并且在 src 子目录中生成
    built_libraries = {"libvgmstream.so": "./lib"}

    # 如果需要应用补丁，在这里列出补丁文件
    # patches = ['vgmstream_android.patch']

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        env = self.get_recipe_env(arch)  # 获取包含 NDK 工具链的环境变量

        # 创建 CMake 构建目录 (在 vgmstream 源目录内或旁边)
        cmake_build_dir = os.path.join(build_dir, "cmake_build")
        os.makedirs(cmake_build_dir, exist_ok=True)

        with current_directory(cmake_build_dir):
            # 使用 CMake 命令配置构建
            # 这里是关键！需要向 CMake 传递 Android NDK 工具链、ABI、API 级别等参数
            # 还需要传递 USE_* 选项来启用依赖，并传递 *_PATH 变量来告诉 CMake 在哪里找到依赖库
            # p4a 的 env 已经包含了 NDK 工具链信息，但传递给 CMake 需要通过特定参数
            # NDK 的 CMake 工具链文件会读取 ANDROID_* 变量
            # vgmstream 的 CMakeLists.txt 会读取 USE_* 和 *_PATH 变量

            # 获取 NDK 路径和工具链文件路径
            ndk_dir = self.ctx.ndk_dir
            cmake_toolchain_file = os.path.join(
                ndk_dir, "build", "cmake", "android.toolchain.cmake"
            )

            # 构建 CMake 配置命令
            cmake_args = [
                "-S",
                build_dir,  # vgmstream 源代码的根目录
                "-B",
                ".",  # 当前目录作为构建目录
                "-DCMAKE_TOOLCHAIN_FILE={}".format(cmake_toolchain_file),
                "-DANDROID_ABI={}".format(arch.arch),
                "-DANDROID_PLATFORM=android-{}".format(self.ctx.ndk_api),
                "-DCMAKE_BUILD_TYPE=Release",  # 或者 Debug
                "-DBUILD_SHARED_LIBS=ON",  # 构建共享库
                "-DVGM_BUILD_SHARED=ON",  # 构建 vgmstream 核心共享库 (根据 vgmstream 的 CMakeLists.txt)
                # 关闭其他不需要的目标
                "-DBUILD_CLI=ON",
                "-DBUILD_FB2K=OFF",
                "-DBUILD_WINAMP=OFF",
                "-DBUILD_XMPLAY=OFF",
                "-DBUILD_V123=OFF",
                "-BUILD_STATIC=ON",
                "-DBUILD_AUDACIOUS=OFF",
                "-USE_MPEG=OFF",
                "-USE_VORBIS=ON",
                "-USE_FFMPEG=ON",
                "-USE_G7221=OFF",
                "-USE_G719=OFF",
                "-USE_ATRAC9=OFF",
                "-USE_SPEEX=OFF",
            ]

            # 运行 CMake 配置
            shprint(sh.cmake, *cmake_args, _env=env)

            # 运行 CMake 构建
            shprint(sh.cmake, "--build", ".", _env=env)

            # 编译成功后，根据 built_libraries 复制库文件
            # p4a 的 install_libraries 方法会自动处理 built_libraries
            # 但您需要确保 built_libraries 中的路径是相对于 cmake_build_dir 的正确路径
            # 根据 vgmstream 的 CMakeLists.txt 和构建过程，libvgmstream_shared.so 可能在 src 子目录
            # 如果 built_libraries 定义是 {'libvgmstream_shared.so': 'src'}，p4a 会查找 cmake_build_dir/src/libvgmstream_shared.so


recipe = VgmstreamRecipe()
