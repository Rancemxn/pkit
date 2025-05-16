from pythonforandroid.recipe import CompiledComponentsPythonRecipe  # type: ignore


class LZ4Recipe(CompiledComponentsPythonRecipe):
    version = "4.4.4"

    url = "https://github.com/python-lz4/python-lz4/archive/refs/tags/v{version}.tar.gz"

    name = "lz4"

    call_hostpython_via_targetpython = False

    site_packages_name = "lz4"


recipe = LZ4Recipe()
