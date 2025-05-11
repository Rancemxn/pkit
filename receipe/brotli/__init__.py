from pythonforandroid.recipe import PythonRecipe  # type: ignore


class BrotliRecipe(PythonRecipe):
    version = "v1.1.0"

    url = "https://github.com/google/brotli/archive/refs/tags/{version}.zip"

    name = "brotli"

    depends = ["python3", "setuptools"]

    hostpython_prerequisites = [
        "setuptools",
        "wheel",
        "pkgconfig",
        "setuptools_scm",
        "pip",
    ]
    source_subdir = "python"
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def build_arch(self, arch):
        self.get_recipe_env(arch)

        super().build_arch(arch)


recipe = BrotliRecipe()
