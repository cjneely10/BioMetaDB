import os
from Cython.Build import cythonize
import setuptools
from setuptools import setup, Extension
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), "r") as f:
    long_description = f.read()


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

extensions = [
    Extension("BioMetaDB.Accessories.arg_parse", ["BioMetaDB/Accessories/arg_parse.pyx"]),
    Extension("BioMetaDB.Accessories.bio_ops", ["BioMetaDB/Accessories/bio_ops.pyx"]),
    Extension("BioMetaDB.Accessories.ops", ["BioMetaDB/Accessories/ops.pyx"]),
    Extension("BioMetaDB.Accessories.program_caller", ["BioMetaDB/Accessories/program_caller.pyx"]),
    Extension("BioMetaDB.DataStructures.record_list", ["BioMetaDB/DataStructures/record_list.pyx"]),
    Extension("BioMetaDB.DBManagers.class_manager", ["BioMetaDB/DBManagers/class_manager.pyx"]),
    Extension("BioMetaDB.DBManagers.integrity_manager", ["BioMetaDB/DBManagers/integrity_manager.pyx"]),
    Extension("BioMetaDB.DBManagers.update_manager", ["BioMetaDB/DBManagers/update_manager.pyx"]),
    Extension("BioMetaDB.Models.functions", ["BioMetaDB/Models/functions.pyx"]),
    Extension("BioMetaDB.Serializers.count_table", ["BioMetaDB/Serializers/count_table.pyx"]),
    Extension("BioMetaDB.Serializers.fix_file", ["BioMetaDB/Serializers/fix_file.pyx"]),
    Extension("BioMetaDB.Serializers.tsv_joiner", ["BioMetaDB/Serializers/tsv_joiner.pyx"]),
]

if CYTHONIZE:
    extensions = cythonize(extensions)
else:
    extensions = no_cythonize(extensions)

setup(
    name='BioMetaDB',
    version='0.1.2.35',
    description='Use biological data to generate SQL database schema',
    url="https://github.com/cjneely10/BioMetaDB",
    author="Christopher Neely",
    author_email="christopher.neely1200@gmail.com",
    license="GNU GPL 3",
    install_requires=[
        "SQLAlchemy==1.3.12",
        "biopython==1.76",
        "configparser==3.8.1",
        "Cython==0.29.14"
    ],
    python_requires='>=3.6',
    ext_modules=extensions,
    # ext_modules=cythonize(["*/*/*.pyx"]),
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'dbdm = BioMetaDB.dbdm:run'
        ]
    },
)

