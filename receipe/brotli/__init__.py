from pythonforandroid.recipe import PythonRecipe  # type: ignore


class BrotliRecipe(PythonRecipe):
    version = "v1.1.0"

    url = "https://github.com/google/brotli/archive/refs/tags/{version}.zip"

    name = "brotli"

    depends = ["setuptools"]

    patches = ["patches/setup.patch"]

    call_hostpython_via_targetpython = False

    install_in_hostpython = False

    def build_arch(self, arch):
        super().build_arch(arch)


recipe = BrotliRecipe()
