from pythonforandroid.recipe import CompiledComponentsPythonRecipe  # type: ignore
from pythonforandroid.toolchain import info, shprint  # type: ignore
from pythonforandroid.toolchain import current_directory  # type: ignore
from os.path import join
import sh  # type: ignore
import glob


class BrotliRecipe(CompiledComponentsPythonRecipe):
    version = "1.1.0"
    url = "https://github.com/google/brotli/archive/refs/tags/v{version}.tar.gz"
    name = "brotli"

    depends = ["python3"]
    conflicts = []

    site_packages_name = "brotli"

    def build_compiled_components(self, arch):
        info(f"Building compiled components in {self.name}")
        env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.hostpython_location)

        with current_directory(self.get_build_dir(arch.arch)):
            if self.install_in_hostpython:
                shprint(hostpython, "setup.py", "clean", "--all", _env=env)

            shprint(
                hostpython,
                "setup.py",
                self.build_cmd,
                "-v",
                _env=env,
                *self.setup_extra_args,
            )

            build_lib_dir_glob = glob.glob(join("build", "lib.*"))
            if not build_lib_dir_glob:
                info("Could not find build/lib.* directory for stripping.")
            else:
                build_lib_dir = build_lib_dir_glob[0]
                if not self.ctx.with_debug_symbols:
                    info(f"Stripping libraries in {build_lib_dir}")
                    shprint(
                        sh.find,
                        build_lib_dir,
                        "-name",
                        "*.so",
                        "-exec",
                        env["STRIP"],
                        "--strip-unneeded",
                        "{}",
                        ";",
                        _env=env,
                    )

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        if env is None:
            env = self.get_recipe_env(arch)

        info(f"Installing {self.name} into site-packages")
        hostpython = sh.Command(self.hostpython_location)
        installdir = self.ctx.get_python_install_dir(arch.arch)
        with current_directory(installdir):
            shprint(
                hostpython,
                "setup.py",
                "install",
                "-O2",
                "--root={}".format(installdir),
                "--install-lib=.",
                _env=env,
                *self.setup_extra_args,
            )

            if self.install_in_hostpython:
                self.install_hostpython_package(arch)


recipe = BrotliRecipe()
