import os
import glob
from BioMetaDB.Config.config_manager import Config
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Serializers.count_table import CountTable

"""
Script holds functionality for UPDATE, which updates existing/adds new records to database
Handles new column generation and SQL migration 

"""


def _update_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file, alias):
    """ Display summary of input parameters before creating database

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Table that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    print("UPDATE:\tUpdate table in existing database")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name, "\n")
    print(" Table aliases:\t\t\t%s" % alias)
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _update_table_display_message_epilogue():
    print("Update complete!", "\n")


def update_existing_table(config_file, table_name, directory_name, data_file, alias, silent):
    """

    :param alias:
    :param silent:
    :param config_file:
    :param table_name:
    :param directory_name:
    :param data_file:
    :return:
    """
    config = Config()
    config_file = glob.glob(os.path.join(config_file, "config/*.ini"))[0]
    config.read(config_file)
    if alias != "None":
        if alias not in config[ConfigKeys.TABLES_TO_ALIAS].keys():
            print(
                "!! Table does not exist! Run CREATE to add to existing database, or INIT to create in new database !!"
            )
            exit(1)
        table_name = config[ConfigKeys.TABLES_TO_ALIAS][alias]
    if table_name not in config.keys():
        print("!! Table does not exist! Run CREATE to add to existing database, or INIT to create in new database !!")
        exit(1)
    if silent == "n":
        _update_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            directory_name,
            data_file,
            alias
        )
    cfg = ConfigManager(config, table_name)
    if data_file != "None":
        data_to_add = CountTable(data_file)
    else:
        data_to_add = None
    if directory_name != "None":
        genomic_files_to_add = (_f for _f in os.listdir(directory_name))
    else:
        genomic_files_to_add = ()
    if alias == "None":
        new_attrs = ClassManager.populate_data_to_existing_table(table_name, data_to_add, cfg, genomic_files_to_add,
                                                                 directory_name, silent, alias)
    else:
        new_attrs = ClassManager.populate_data_to_existing_table(table_name, data_to_add, cfg, genomic_files_to_add,
                                                                 directory_name, silent)
    ClassManager.write_class(new_attrs, cfg.classes_file)
    if not silent:
        _update_table_display_message_epilogue()