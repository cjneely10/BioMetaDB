from sqlalchemy.orm import mapper
from BioMetaDB.DataStructures.record_list import RecordList
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys


"""
Script will hold functionality to display to stdout a summary of key project details

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
    print(" Name of table:\t\t\t%s" % table_name)
    print(" Table aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tPopulate table")
    print(" Get metadata from\t\t%s" % data_file)
    print(" Copy fastx files from\t\t%s" % directory_name, "\n")


def _update_table_display_message_epilogue():
    print("Update complete!", "\n")


def summarize_database(config_file):
    config = ConfigManager.confirm_config_set(config_file)
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    for table_name in tables_in_database:
        cfg = ConfigManager(config, table_name)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table_name, engine)
        UserClass = type(table_name, (DBUserClass,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        rl = RecordList(sess, UserClass, cfg)
        print(rl.get_summary_string())
