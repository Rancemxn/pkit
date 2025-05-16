from pythonforandroid.recipe import PyProjectRecipe  # type: ignore


class BrotliRecipe(PyProjectRecipe):
    version = "4.4.4"

    url = "https://github.com/python-lz4/python-lz4/archive/refs/tags/v{version}.tar.gz"

    name = "brotli"

    site_packages_name = "brotli"


recipe = BrotliRecipe()
