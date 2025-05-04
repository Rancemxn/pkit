import os
from os.path import realpath
from multiprocessing import cpu_count

from pythonforandroid.toolchain import Recipe, current_directory, shprint  # type: ignore
import sh  # type: ignore


class VgmstreamRecipe(Recipe):
    name = "vgmstream"
    version = "c32951e"  # Fix compile without mpg123 version
    url = "https://github.com/vgmstream/vgmstream/archive/c32951e914ab9401c83a6fb3f06f0cc9dc4f5ec3.zip"

    depends = ["libpthread"]

    patches = ["patches/ffmpeg.patch", "patches/CMakeLists.patch"]

    # Conflict with FFmpeg_bin, depends will save as another filename
    built_libraries = {
        "libvgmstream-cli.so": "./cmake_build",
        "libvgmstream.so": "./cmake_build",
        "libvorbis_vgm.so": "./cmake_build",
        "libvorbisfile_vgm.so": "./cmake_build",
        "libogg_vgm.so": "./cmake_build",
        "libavcodec_vgm.so": "./cmake_build",
        "libavformat_vgm.so": "./cmake_build",
        "libavutil_vgm.so": "./cmake_build",
        "libswresample_vgm.so": "./cmake_build",
    }

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["NDK"] = self.ctx.ndk_dir

        return env

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

            if "arm64" in arch.arch:
                arch_flag = "aarch64"
            elif "x86" in arch.arch:
                arch_flag = "x86"
            else:
                arch_flag = "arm"

            # Fix pthread link
            fake_libpthread_temp_folder = Recipe.get_recipe(
                "libpthread", self.ctx
            ).get_build_dir(arch.arch)
            fake_libpthread_temp_folder = os.path.join(
                fake_libpthread_temp_folder, "p4a-libpthread-recipe-tempdir"
            )
            env["LDFLAGS"] += f" -L{fake_libpthread_temp_folder}"

            cmake_args = [
                "-S",
                build_dir,
                "-B",
                ".",
                "-DANDROID_STL=" + self.stl_lib_name,
                "-DCMAKE_SYSTEM_NAME=Android",
                "-DCMAKE_POSITION_INDEPENDENT_CODE=1",
                "-DCMAKE_TOOLCHAIN_FILE={}".format(cmake_toolchain_file),
                "-DCMAKE_ANDROID_NDK=" + self.ctx.ndk_dir,
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
                "-DBUILD_STATIC=OFF",
                "-DBUILD_AUDACIOUS=OFF",
                "-DUSE_MPEG=OFF",
                "-DUSE_VORBIS=ON",
                "-DUSE_FFMPEG=ON",
                "-DUSE_G7221=OFF",
                "-DUSE_G719=OFF",
                "-DUSE_ATRAC9=OFF",
                "-DUSE_SPEEX=OFF",
                "-DUSE_CELT=OFF",
                # FFmpeg compile toolchain
                f"-DFFMPEG_CROSS_PREFIX={arch.target}",
                f"-DFFMPEG_ARCH={arch_flag}",
                f"-DFFMPEG_STRIP={self.ctx.ndk.llvm_strip}",
                f"-DFFMPEG_SYSROOT={self.ctx.ndk.sysroot}",
                f"-DFFMPEG_PREFIX={realpath('.')}",
                f"-DFF_CC={os.path.join(self.ctx.ndk.llvm_bin_dir, arch.target + '-clang')}",
                f"-DFF_CXX={os.path.join(self.ctx.ndk.llvm_bin_dir, arch.target + '-clang++')}",
                f"-DFF_AR={self.ctx.ndk.llvm_ar}",
                f"-DFF_RANLIB={self.ctx.ndk.llvm_ranlib}",
                "-DCMAKE_VERBOSE_MAKEFILE=ON",
                f"-DCMAKE_SHARED_LINKER_FLAGS={env['LDFLAGS']}",
                f"-DCMAKE_EXE_LINKER_FLAGS={env['LDFLAGS']}",
                f"-DCMAKE_MODULE_LINKER_FLAGS={env['LDFLAGS']}",
                "-DEMSCRIPTEN=OFF",
                # Build .so librarys
                "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            ]

            shprint(sh.cmake, *cmake_args, _env=env)

            # Make FFmpeg First
            shprint(
                sh.cmake,
                "--build",
                ".",
                "--target",
                "FFMPEG_MAKE",
                "-j",
                str(cpu_count()),
                _env=env,
            )

            # Build Cli
            build_targets = ["libvgmstream_shared", "vgmstream_cli"]
            shprint(
                sh.cmake,
                "--build",
                ".",
                "--target",
                *build_targets,
                "-j",
                str(cpu_count()),
                _env=env,
            )

            # Rename libs to avoid conflicts
            shprint(
                sh.cp,
                "./cli/vgmstream-cli",
                "libvgmstream-cli.so",
            )
            shprint(
                sh.cp,
                "./src/libvgmstream.so",
                "libvgmstream.so",
            )
            shprint(
                sh.cp,
                "./dependencies/ogg/libogg.so",
                "libogg_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/ffmpeg/bin/usr/local/lib/libavcodec.so",
                "libavcodec_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/ffmpeg/bin/usr/local/lib/libavformat.so",
                "libavformat_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/ffmpeg/bin/usr/local/lib/libavutil.so",
                "libavutil_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/vorbis/lib/libvorbis.so",
                "libvorbis_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/vorbis/lib/libvorbisfile.so",
                "libvorbisfile_vgm.so",
            )
            shprint(
                sh.cp,
                "./dependencies/ffmpeg/bin/usr/local/lib/libswresample.so",
                "libswresample_vgm.so",
            )


recipe = VgmstreamRecipe()
