from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory
from os.path import exists, join
import sh
import glob


class SKLearnRecipe(CythonRecipe):
    version = '0.23.2'
    url = 'https://github.com/scikit-learn/scikit-learn/archive/{version}.tar.gz'

    depends = ['python3', 'numpy', 'scipy', 'joblib', 'threadpoolctl']

    conflicts = []  # A list of any recipe names that cannot be built
                    # alongside this one

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['CFLAGS'] += ' -fopenmp'
        env['CXXFLAGS'] += ' -fopenmp'
        env['LDFLAGS'] += ' -fopenmp'
        env['SKLEARN_FAIL_NO_OPENMP'] = '1'
        return env

    def should_build(self, arch):
        # Add a check for whether the recipe is already built if you
        # want, and return False if it is.
        return True

    def prebuild_arch(self, arch):
        super().prebuild_arch(self)
        # Do any extra prebuilding you want, e.g.:
        #self.apply_patch('path/to/patch.patch')

    def build_arch(self, arch):
        super().build_arch(self)
        # Build the code. Make sure to use the right build dir, e.g.
        #with current_directory(self.get_build_dir(arch.arch)):
        #    sh.ls('-lathr')  # Or run some commands that actually do
        #                     # something

    def postbuild_arch(self, arch):
        super().prebuild_arch(self)
        # Do anything you want after the build, e.g. deleting
        # unnecessary files such as documentation

recipe = SKLearnRecipe()
