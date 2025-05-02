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
        "libogg",
    ]

    need_stl_shared = True

    built_libraries = {"libvgmstream.so": "."}

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        env = self.get_recipe_env(arch)

        cmake_build_dir = os.path.join(build_dir, "cmake_build")
        os.makedirs(cmake_build_dir, exist_ok=True)

        with current_directory(cmake_build_dir):
            ndk_dir = self.ctx.ndk_dir
            cmake_toolchain_file = os.path.join(
                ndk_dir, "build", "cmake", "android.toolchain.cmake"
            )

            cmake_args = [
                "-S",
                build_dir,
                "-B",
                ".",
                "-DCMAKE_SYSTEM_NAME=Android",
                "-DCMAKE_POSITION_INDEPENDENT_CODE=1",
                "-DCMAKE_TOOLCHAIN_FILE={}".format(cmake_toolchain_file),
                "-DCMAKE_ANDROID_ARCH_ABI={arch}".format(arch=arch.arch),
                "-DCMAKE_ANDROID_NDK=" + self.ctx.ndk_dir,
                "-DCMAKE_C_COMPILER={cc}".format(cc=arch.get_clang_exe()),
                "-DCMAKE_CXX_COMPILER={cc_plus}".format(
                    cc_plus=arch.get_clang_exe(plus_plus=True)
                ),
                "-DANDROID_ABI={}".format(arch.arch),
                "-DANDROID_PLATFORM=android-{}".format(self.ctx.ndk_api),
                "-DCMAKE_BUILD_TYPE=Release",
                "-DBUILD_SHARED_LIBS=ON",
                "-DVGM_BUILD_SHARED=ON",
                "-DBUILD_CLI=ON",
                "-DBUILD_FB2K=OFF",
                "-DBUILD_WINAMP=OFF",
                "-DBUILD_XMPLAY=OFF",
                "-DBUILD_V123=OFF",
                "-DBUILD_STATIC=ON",
                "-DBUILD_AUDACIOUS=OFF",
                "-DUSE_MPEG=OFF",
                "-DUSE_VORBIS=ON",
                "-DUSE_FFMPEG=ON",
                "-DUSE_G7221=OFF",
                "-DUSE_G719=OFF",
                "-DUSE_ATRAC9=OFF",
                "-DUSE_SPEEX=OFF",
                "-DUSE_CELT=OFF",
            ]

            shprint(sh.cmake, *cmake_args, _env=env)

            shprint(sh.cmake, "--build", ".", _env=env)


recipe = VgmstreamRecipe()
