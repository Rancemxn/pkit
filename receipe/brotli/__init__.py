from pythonforandroid.recipe import PyProjectRecipe  # type: ignore


class BrotliRecipe(PyProjectRecipe):
    version = "1.1.0"

    url = "https://github.com/google/brotli/archive/refs/tags/v{version}.tar.gz"

    name = "brotli"

    site_packages_name = "brotli"

    def get_recipe_env(self, arch, *args, **kwargs):
        env = super().get_recipe_env(arch, *args, **kwargs)
        env["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_BROTLI"] = self.version
        return env


recipe = BrotliRecipe()
