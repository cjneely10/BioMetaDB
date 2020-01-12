import os
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Serializers.count_table import CountTable
from BioMetaDB.DBOperations.integrity_check import integrity_check

"""
Script holds functionality for UPDATE, which updates existing/adds new records to database
Handles new column generation and SQL migration 

"""


def _update_display_message_prelude(db_name, working_directory, table_name, directory_name, data_file, alias):
    """ Display summary of input parameters before creating database

    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Record that will be created
    :param directory_name: (str)    Directory with files to add
    :param data_file: (str)     File with metadata for storing in database
    :return:
    """
    print("UPDATE:\tUpdate table in existing database")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name)
    print(" Table aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _update_table_display_message_epilogue():
    print("Update complete!", "\n")


def update_existing_table(config_file, table_name, directory_name, data_file, alias, silent, integrity_cancel):
    """

    :param config_file:
    :param table_name:
    :param directory_name:
    :param data_file:
    :param alias:
    :param silent:
    :param integrity_cancel:
    :return:
    """
    _cfg, _tbl, _al, _sil = config_file, table_name, alias, silent
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
        if table_name is None:
            print(
                "!! Table does not exist! Run CREATE to add to existing database, or INIT to create in new database !!"
            )
            exit(1)
    if table_name != "None" and table_name not in config.keys():
        print("!! Table does not exist! Run CREATE to add to existing database, or INIT to create in new database !!")
        exit(1)
    cfg = ConfigManager(config, table_name)
    if not silent:
        _update_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            directory_name,
            data_file,
            alias
        )
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
    if not integrity_cancel:
        integrity_check(_cfg, _tbl, _al, _sil)
