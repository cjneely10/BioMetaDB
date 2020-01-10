import os
from Cython.Build import cythonize
import setuptools
from setuptools import setup, Extension
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), "r") as f:
    long_description = f.read()

# with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "requirements.txt"), "r") as fp:
#     install_requires = fp.read().strip().split("\n")

extensions = [
    Extension("BioMetaDB.Accessories.arg_parse", ["BioMetaDB/Accessories/arg_parse.c"]),
    Extension("BioMetaDB.Accessories.bio_ops", ["BioMetaDB/Accessories/bio_ops.c"]),
    Extension("BioMetaDB.Accessories.ops", ["BioMetaDB/Accessories/ops.c"]),
    Extension("BioMetaDB.Accessories.program_caller", ["BioMetaDB/Accessories/program_caller.c"]),
    Extension("BioMetaDB.DataStructures.record_list", ["BioMetaDB/DataStructures/record_list.c"]),
    Extension("BioMetaDB.DBManagers.class_manager", ["BioMetaDB/DBManagers/class_manager.c"]),
    Extension("BioMetaDB.DBManagers.integrity_manager", ["BioMetaDB/DBManagers/integrity_manager.c"]),
    Extension("BioMetaDB.DBManagers.update_manager", ["BioMetaDB/DBManagers/update_manager.c"]),
    Extension("BioMetaDB.Models.functions", ["BioMetaDB/Models/functions.c"]),
    Extension("BioMetaDB.Serializers.count_table", ["BioMetaDB/Serializers/count_table.c"]),
    Extension("BioMetaDB.Serializers.fix_file", ["BioMetaDB/Serializers/fix_file.c"]),
    Extension("BioMetaDB.Serializers.tsv_joiner", ["BioMetaDB/Serializers/tsv_joiner.c"]),
]

setup(
    name='BioMetaDB',
    version='0.1.2.34',
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

