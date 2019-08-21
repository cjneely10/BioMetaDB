import os
from distutils.core import setup
from Cython.Build import cythonize
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), "r") as f:
    long_description = f.read()
setup(
    name='BioMetaDB',    # This is the name of your PyPI-package.
    version='0.1.0',
    description='Use biological data to generate SQL database schema',
    url="https://github.com/cjneely10/BioMetaDB",
    author="Christopher Neely",
    author_email="christopher.neely1200@gmail.com",
    license="",
    ext_modules=cythonize(["*/*/*.pyx",]),
    requires=['biopython', 'Cython', 'SQLAlchemy'],
)

