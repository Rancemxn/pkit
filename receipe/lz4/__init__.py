from pythonforandroid.recipe import PyProjectRecipe  # type: ignore


class LZ4Recipe(PyProjectRecipe):
    version = "4.4.4"

    url = "https://github.com/python-lz4/python-lz4/archive/refs/tags/v{version}.tar.gz"

    name = "lz4"

    site_packages_name = "lz4"

    def get_recipe_env(self, arch, *args, **kwargs):
        env = super().get_recipe_env(arch, *args, **kwargs)
        env["PYLZ4_USE_SYSTEM_LZ4"] = "0"

        return env


recipe = LZ4Recipe()
