import os
from BioMetaDB.Accessories.ops import touch
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Serializers.count_table import CountTable
from BioMetaDB.Config.directory_manager import Directories
from BioMetaDB.Exceptions.create_database_exceptions import CreateDBAssertString
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBManagers.type_mapper import TypeMapper
from BioMetaDB.Config.config_manager import Config
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.DBOperations.integrity_check import integrity_check


"""
Function handles creating database and first table
Initializes with provided directory and data file

"""


def _initialization_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file, alias):
    """ Display summary of input parameters before creating database

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Record that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    print("INIT:\tCreate project database and initialize")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name)
    print(" Table aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _initialization_display_message_epilogue():
    print("Initialization complete!", "\n")


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
    migrations_dir = os.path.join(working_directory, Directories.MIGRATIONS)
    os.makedirs(classes_dir)
    os.makedirs(config_dir)
    os.makedirs(db_dir)
    os.makedirs(migrations_dir)
    table_dir = os.path.join(db_dir, table_name)
    return classes_dir, config_dir, db_dir, table_dir


def create_database(db_name, table_name, directory_name, data_file, alias, silent, integrity_cancel):
    """ Function called from dbdm initializes project/module

    :param db_name: (str)   Name of db
    :param table_name: (str)    Record that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :param alias:
    :param silent:
    :param integrity_cancel:
    :return:
    """
    # Confirm working dir does not exist and that directory with genomes does exist
    # assert db_name != "None", CreateDBAssertString.WORKING_DB_NOT_SET
    if db_name == "None":
        print(CreateDBAssertString.WORKING_DB_NOT_SET)
        exit(1)
    # assert table_name != "None", CreateDBAssertString.TABLE_NAME_NOT_SET
    if table_name == "None":
        print(CreateDBAssertString.TABLE_NAME_NOT_SET)
        exit(1)
    # assert os.path.isdir(db_name) is False, CreateDBAssertString.WORKING_DIR_EXISTS
    if os.path.isdir(db_name):
        print(CreateDBAssertString.WORKING_DIR_EXISTS)
        exit(1)
    # if directory_name != "None":
    #     assert os.path.isdir(directory_name), CreateDBAssertString.SEQUENCE_DIR_NOT_EXISTS
    if directory_name != "None" and not os.path.isdir(directory_name):
        print(CreateDBAssertString.SEQUENCE_DIR_NOT_EXISTS)
        exit(1)
    table_name = table_name.lower()
    if not silent:
        _initialization_display_message_prelude(db_name, db_name, table_name, directory_name, data_file, alias)
    # Gather files to commit and initial data to store for each file
    print_if_not_silent(silent, "Beginning process...")
    print_if_not_silent(silent, " Getting files from %s" % directory_name)
    if directory_name != "None":
        genomic_files_to_add = (_f for _f in os.listdir(directory_name))
    else:
        genomic_files_to_add = ()
    data_types = {}
    initial_data = []
    if data_file is not "None":
        _initial_data = CountTable(data_file)
        # Ignore first column name, typically announcing "Name" or "Genome ID"
        # Get names and types of each column in dict
        # Key is header name (which will be used as name of column in database)
        # Value is type of data (int, float, str) that is found for a random genome id's data value
        # TODO: Data type determination requires a uniformity from the .tsv file data. Consider a workaround
        data_types = TypeMapper.get_translated_types(_initial_data, TypeMapper.py_type_to_string)
        initial_data.append(_initial_data)
    # Create working directories
    print_if_not_silent(silent, " Creating directories at database root %s" % db_name)
    classes_dir, config_dir, db_dir, table_dir = _create_all_directories(db_name, table_name)
    # Create database file
    print_if_not_silent(silent, " Creating database file in %s" % db_dir)
    touch(os.path.join(db_dir, db_name + ".db"))
    # Write configuration info
    config_file = db_name + ".ini"
    print_if_not_silent(silent, " Writing database configuration to %s" % os.path.join(config_dir, config_file))
    config = Config()
    abs_path_working_dir = os.path.abspath(db_name)
    db_name = os.path.basename(db_name)
    config[ConfigKeys.DATABASES] = {
        ConfigKeys.db_name: db_name,
        ConfigKeys.working_dir: abs_path_working_dir,
        ConfigKeys.rel_work_dir: db_name,
        ConfigKeys.migrations_dir: os.path.join(abs_path_working_dir, Directories.MIGRATIONS),
        ConfigKeys.config_dir: os.path.join(abs_path_working_dir, Directories.CONFIG),
        ConfigKeys.db_dir: os.path.join(abs_path_working_dir, Directories.DATABASE),
        ConfigKeys.rel_db_dir: os.path.join(db_name, Directories.DATABASE),
    }
    config[table_name] = {
        ConfigKeys.rel_classes_dir:     os.path.join(db_name, Directories.CLASSES),
    }
    config[ConfigKeys.TABLES_TO_DB] = {
        table_name: db_name,
    }
    config[ConfigKeys.TABLES_TO_ALIAS] = {
        "{}|{}".format(alias, table_name): table_name,
    }
    with open(os.path.join(config_dir, config_file), "w") as W:
        config.write(W)
    # Create table
    print_if_not_silent(silent, "Creating new table %s at %s" % (table_name, os.path.join(db_dir, db_name)))
    os.makedirs(table_dir)
    ClassManager.create_initial_table_in_db(db_name, db_name, table_name, data_types, silent, initial=False)
    # Populate table with data from file and genomes
    # Get config file - confirms that it was written correctly
    cfg = ConfigManager(config, table_name)
    if data_file is not "None":
        for _data in initial_data:
            ClassManager.populate_data_to_existing_table(table_name, _data, cfg,
                                                         genomic_files_to_add, directory_name, silent)
    if not silent:
        _initialization_display_message_epilogue()
    if not integrity_cancel:
        integrity_check(db_name, table_name, "None", silent)
