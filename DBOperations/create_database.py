import os
import random
from Accessories.ops import touch
from Serializers.count_table import CountTable
from Config.directory_manager import Directories
from Exceptions.create_database_exceptions import AssertString
from DBClassManager.class_manager import ClassManager
from DBClassManager.type_mapper import TypeMapper
from Config.config_manager import Config
from Config.config_manager import ConfigManager
from Config.config_manager import ConfigKeys


"""
Function handles creating database and first table
Initializes with provided directory and data file

"""


def _initialization_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file):
    """ Display summary of input parameters before creating database

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Table that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    print("INIT:\tCreate project database and initialize")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name, "\n")
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _initialization_display_message_epilogue():
    pass


def _create_all_directories(working_directory, table_name):
    """ Creates directories for package, database, config, and class info

    :param working_directory: (str) Name of package directory
    :param table_name: (str)    Name of db table to create
    :return:
    """
    os.makedirs(working_directory)
    classes_dir = os.path.join(working_directory, Directories.CLASSES)
    config_dir = os.path.join(working_directory, Directories.CONFIG)
    db_dir = os.path.join(working_directory, Directories.DATABASE)
    os.makedirs(classes_dir)
    os.makedirs(config_dir)
    os.makedirs(db_dir)
    table_dir = os.path.join(db_dir, table_name)
    return classes_dir, config_dir, db_dir, table_dir


def create_database(db_name, working_directory, table_name, directory_name, data_file):
    """ Function called from dbdm initializes project/module

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Table that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    # Confirm working dir does not exist and that directory with genomes does exist
    assert os.path.isdir(working_directory) is False, AssertString.WORKING_DIR_EXISTS
    assert os.path.isdir(directory_name), AssertString.SEQUENCE_DIR_NOT_EXISTS
    _initialization_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file)
    # Gather files to commit and initial data to store for each file
    print("Beginning process...")
    print("Getting files from %s" % directory_name)
    genomic_files_to_add = (_f for _f in os.listdir(directory_name))
    data_types = {}
    initial_data = []
    if data_file is not "None":
        for _file in data_file.split(","):
            _initial_data = CountTable(_file)
            # Ignore first column name, typically announcing "Name" or "Genome ID"
            # Get names and types of each column in dict
            # Key is header name (which will be used as name of column in database)
            # Value is type of data (int, float, str) that is found for a random genome id's data value
            # TODO: Data type determination requires a uniformity from the .tsv file data. Consider a workaround
            print("Gathering data from %s" % _file)
            data_types = {
                _initial_data.header[i]:
                    TypeMapper.py_type_to_string[
                        type(_initial_data.get_at(random.sample(_initial_data.file_contents.keys(), 1)[0], i - 1))
                    ]
                for i in range(1, len(_initial_data.header))
            }
            initial_data.append(_initial_data)
    # Create working directories
    print("Creating directories at database root %s" % working_directory)
    classes_dir, config_dir, db_dir, table_dir = _create_all_directories(working_directory, table_name)
    # Create database file
    print("Creating database file in %s" % db_dir)
    _db_name = db_name.strip(".db") + ".db"
    touch(os.path.join(db_dir, _db_name))
    # Write configuration info
    config_file = db_name + ".ini"
    print("Writing database configuration to %s" % os.path.join(config_dir, config_file))
    config = Config()
    abs_path_working_dir = os.path.abspath(working_directory)
    config[table_name] = {
        ConfigKeys.working_dir:  abs_path_working_dir,
        ConfigKeys.rel_work_dir: working_directory,
        ConfigKeys.rel_db_dir:  os.path.join(working_directory, Directories.DATABASE),
        ConfigKeys.rel_classes_dir:     os.path.join(working_directory, Directories.CLASSES),
        ConfigKeys.db_dir:       os.path.join(abs_path_working_dir, Directories.DATABASE),
        ConfigKeys.class_dir:    os.path.join(abs_path_working_dir, Directories.CLASSES),
    }
    config[ConfigKeys.TABLES_TO_DB] = {
        table_name: db_name,
    }
    with open(os.path.join(config_dir, config_file), "w") as W:
        config.write(W)
    # Create table
    print("Creating new table %s at %s" % (table_name, os.path.join(db_dir, _db_name)))
    os.makedirs(table_dir)
    ClassManager.create_db_and_initial_table(_db_name, working_directory, table_name, data_types)
    # Populate table with data from file and genomes
    cfg = ConfigManager(config, table_name)
    if data_file is not "None":
        for _data in initial_data:
            ClassManager.populate_data_to_existing_table(table_name, _data, cfg,
                                                         genomic_files_to_add, directory_name)

    print("Initialization complete!", "\n")
