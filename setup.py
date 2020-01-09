import os
from Cython.Build import cythonize
from setuptools import setup, Extension
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), "r") as f:
    long_description = f.read()

extensions = [
    Extension("Accessories.arg_parse", ["BioMetaDB/Accessories/arg_parse.pyx"]),

]

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")

setup(
    name='BioMetaDB',
    version='0.1.2.7',
    description='Use biological data to generate SQL database schema',
    url="https://github.com/cjneely10/BioMetaDB",
    author="Christopher Neely",
    author_email="christopher.neely1200@gmail.com",
    license="GNU GPL 3",
    install_requires=install_requires,
    python_requires='>=3.6',
    ext_modules=cythonize(["*/*/*.pyx", ]),
)

