# Reference: https://github.com/kivy/python-for-android/issues/3137#issuecomment-2764709681

from pythonforandroid.toolchain import Recipe, current_directory, shprint  # type: ignore
from os.path import realpath
import sh  # type: ignore
from multiprocessing import cpu_count


class FFMpegRecipe(Recipe):
    version = "n6.1.2"
    url = "https://github.com/FFmpeg/FFmpeg/archive/{version}.zip"
    depends = ["sdl3", "av_codecs", "ffpyplayer_codecs"]
    patches = ["patches/configure.patch"]
    _libs = [
        "libavcodec.so",
        "libavfilter.so",
        "libavutil.so",
        "libswscale.so",
        "libavdevice.so",
        "libavformat.so",
        "libswresample.so",
        "libpostproc.so",
        "libffmpegbin.so",
    ]
    built_libraries = dict.fromkeys(_libs, "./lib")

    def should_build(self, arch):
        return True

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["NDK"] = self.ctx.ndk_dir
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = arch.get_env()
            cflags = []
            ldflags = []

            # enable hardware acceleration codecs
            flags = ["--enable-jni", "--enable-mediacodec"]

            # Enable GPL
            flags += ["--enable-gpl"]

            # Enable GPL3
            flags += ["--enable-version3"]

            # libx264
            flags += ["--enable-libx264"]
            build_dir = Recipe.get_recipe("libx264", self.ctx).get_build_dir(arch.arch)
            cflags += ["-I" + build_dir + "/include/"]
            # Newer versions of FFmpeg prioritize the dynamic library and ignore
            # the static one, unless the static library path is explicitly set.
            ldflags += [build_dir + "/lib/" + "libx264.a"]

            # libshine
            flags += ["--enable-libshine"]
            build_dir = Recipe.get_recipe("libshine", self.ctx).get_build_dir(arch.arch)
            cflags += ["-I" + build_dir + "/include/"]
            ldflags += ["-lshine", "-L" + build_dir + "/lib/"]
            ldflags += ["-lm"]

            # libvpx
            flags += ["--enable-libvpx"]
            build_dir = Recipe.get_recipe("libvpx", self.ctx).get_build_dir(arch.arch)
            cflags += ["-I" + build_dir + "/include/"]
            ldflags += ["-lvpx", "-L" + build_dir + "/lib/"]

            # Enable all codecs:
            flags += [
                "--enable-parsers",
                "--enable-decoders",
                "--enable-encoders",
                "--enable-muxers",
                "--enable-demuxers",
            ]
            # needed to prevent _ffmpeg.so: version node not found for symbol av_init_packet@LIBAVFORMAT_52
            # /usr/bin/ld: failed to set dynamic section sizes: Bad value
            flags += [
                "--disable-symver",
            ]

            # disable doc
            flags += [
                "--disable-doc",
            ]

            # other flags:
            flags += [
                "--enable-filter=aresample,resample,crop,adelay,volume,scale",
                "--enable-protocol=file,http,hls,udp,tcp",
                "--enable-hwaccels",
                "--enable-pic",
                "--disable-static",
                "--disable-debug",
                "--enable-shared",
            ]

            if "arm64" in arch.arch:
                arch_flag = "aarch64"
            elif "x86" in arch.arch:
                arch_flag = "x86"
                flags += ["--disable-asm"]
            else:
                arch_flag = "arm"

            # android:
            flags += [
                "--target-os=android",
                "--enable-cross-compile",
                "--cross-prefix={}-".format(arch.target),
                "--arch={}".format(arch_flag),
                "--strip={}".format(self.ctx.ndk.llvm_strip),
                "--sysroot={}".format(self.ctx.ndk.sysroot),
                "--enable-neon",
                "--prefix={}".format(realpath(".")),
            ]

            if arch_flag == "arm":
                cflags += [
                    "-mfpu=vfpv3-d16",
                    "-mfloat-abi=softfp",
                    "-fPIC",
                ]

            env["CFLAGS"] += " " + " ".join(cflags)
            env["LDFLAGS"] += " " + " ".join(ldflags)

            configure = sh.Command("./configure")
            shprint(configure, *flags, _env=env)
            shprint(sh.make, "-j", str(cpu_count()), _env=env)
            shprint(sh.make, "install", _env=env)


recipe = FFMpegRecipe()
