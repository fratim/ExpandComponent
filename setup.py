from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        name='growSomae',
        include_dirs=[np.get_include()],
        sources=['growSomae.pyx', 'cpp-growSomae.cpp'],
        extra_compile_args=['-O4', '-std=c++0x'],
        language='c++'
    )
]

setup(
    name='growSomae',
    ext_modules=cythonize(extensions)
)
