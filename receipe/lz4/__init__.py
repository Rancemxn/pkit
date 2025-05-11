from pythonforandroid.recipe import PythonRecipe  # type: ignore


class Lz4Recipe(PythonRecipe):
    version = "v4.4.4"
    url = "https://github.com/python-lz4/python-lz4/archive/refs/tags/{version}.zip"

    name = "lz4"

    depends = ["python3", "setuptools"]

    hostpython_depends = ["setuptools", "wheel", "pkgconfig", "setuptools_scm"]

    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env["PYLZ4_USE_SYSTEM_LZ4"] = "0"
        return env

    def build_arch(self, arch):
        super().build_arch(arch)


recipe = Lz4Recipe()
