from pythonforandroid.recipe import PyProjectRecipe  # type: ignore


class BrotliRecipe(PyProjectRecipe):
    version = "1.1.0"

    url = "https://github.com/google/brotli/archive/refs/tags/v{version}.tar.gz"

    name = "brotli"

    site_packages_name = "brotli"


recipe = BrotliRecipe()
