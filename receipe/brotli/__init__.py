from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
import sh
import os


class BrotliRecipe(PythonRecipe):
    version = "v1.1.0"

    url = "https://github.com/google/brotli/archive/refs/tags/{version}.zip"

    name = "brotli"

    depends = ["python3", "setuptools"]

    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def build_arch(self, arch):
        info(f"Building brotli for {arch.arch}")
        env = self.get_recipe_env(arch)

        super().build_arch(arch)


recipe = BrotliRecipe()
