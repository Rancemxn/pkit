from pythonforandroid.recipe import PythonRecipe  # type: ignore


class Lz4Recipe(PythonRecipe):
    version = "v4.4.4"
    url = "https://github.com/python-lz4/python-lz4/archive/refs/tags/{version}.zip"

    name = "lz4"

    depends = ["python3", "setuptools"]

    hostpython_depends = ["setuptools", "wheel", "pkgconfig"]

    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def build_arch(self, arch):
        super().build_arch(arch)


recipe = Lz4Recipe()
