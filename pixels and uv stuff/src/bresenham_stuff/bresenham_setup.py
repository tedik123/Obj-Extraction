from glob import glob
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

__version__ = "0.0.1"


ext_modules = [
    Pybind11Extension("bresenham_triangle_class",
                      ["bresenham.cpp"],
                      # Example: passing in the version to the compiled code
                      define_macros=[('VERSION_INFO', __version__)],
                      ),
]

# setup(..., ext_modules=ext_modules)
setup(name="bresenham_triangle_class",
      version=__version__,
      ext_modules=ext_modules,
      cmdclass={"build_ext": build_ext})
