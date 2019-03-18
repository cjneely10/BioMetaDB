import os
import glob
from Config.directory_manager import Directories
from Serializers.count_table import CountTable
from Config.config_manager import Config
from Config.config_manager import ConfigManager
from Config.config_manager import ConfigKeys
from DBManagers.class_manager import ClassManager
from DBManagers.type_mapper import TypeMapper

"""
Script will hold functionality for CREATE, to create new tables when in existing database
Function called from ProgramCaller

"""


def _create_table_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file, alias):
    """ Display summary of input parameters before creating database

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Table that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    print("CREATE:\tCreate table in existing database")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name, "\n")
    print(" Table aliases:\t\t\t%s" % alias)
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _create_table_display_message_epilogue():
    print("New table creation complete!", "\n")


def _create_all_directories(working_directory, table_name):
    """ Creates directories for table and class info

    :param working_directory: (str) Name of package directory
    :param table_name: (str)    Name of db table to create
    :return:
    """
    db_dir = os.path.join(working_directory, Directories.DATABASE)
    os.makedirs(os.path.join(db_dir, table_name), exist_ok=True)


def create_table_in_existing_database(config_file, table_name, directory_name, data_file, alias, silent):
    """

    :param silent:
    :param config_file:
    :param table_name:
    :param directory_name:
    :param data_file:
    :param alias:
    :return:
    """
    config = Config()
    config_file = glob.glob(os.path.join(config_file, "config/*.ini"))[0]
    config.read(config_file)
    if table_name in config.keys():
        print("!! Table exists, exiting. To update table, use UPDATE !!")
        exit(1)
    if silent == "n":
        _create_table_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name],
                                              config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
                                              table_name,
                                              directory_name,
                                              data_file,
                                              alias)
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
    # Gather bio data from folder
    if directory_name != "None":
        genomic_files_to_add = (_f for _f in os.listdir(directory_name))
    else:
        genomic_files_to_add = ()
    # Create new table directories
    _create_all_directories(config[ConfigKeys.DATABASES][ConfigKeys.working_dir], table_name)
    # Update config object with new data
    config[table_name] = {
        ConfigKeys.rel_classes_dir: os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
                                                 Directories.CLASSES),
        ConfigKeys.class_dir: os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.working_dir], Directories.CLASSES),
    }
    config.set(ConfigKeys.TABLES_TO_DB, table_name, config[ConfigKeys.DATABASES][ConfigKeys.db_name])
    config.set(ConfigKeys.TABLES_TO_ALIAS, alias, table_name)
    # Write new config file
    with open(config_file, "w") as W:
        config.write(W)
    # Update ConfigManager object
    cfg = ConfigManager(config, table_name)
    # Create new table and populate with new data
    ClassManager.create_initial_table_in_db(cfg.db_name, cfg.working_dir, table_name, data_types, silent, initial=False)
    if data_file is not "None":
        for _data in initial_data:
            ClassManager.populate_data_to_existing_table(table_name, _data, cfg,
                                                         genomic_files_to_add, directory_name, silent)
    if not silent:
        _create_table_display_message_epilogue()
