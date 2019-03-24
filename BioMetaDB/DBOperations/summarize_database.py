from sqlalchemy.orm import mapper
from BioMetaDB.DataStructures.record_list import RecordList
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys


"""
Script will hold functionality to display to stdout a summary of key project details

"""


def _update_display_message_prelude(db_name):
    """ Display summary of input parameters before displaying db summary

    :param db_name: (str)   Name of db
    :return:
    """
    print("SUMMARIZE:\tView summary of all tables in database")
    print(" Project root directory:\t%s" % db_name)
    print(" Name of database:\t\t%s.db\n" % db_name.strip(".db"))


def summarize_database(config_file, view):
    """ Function will query all tables listed in the config file, outputting simple
    metrics to the screen

    :param view:
    :param config_file:
    :return:
    """
    config, config_file = ConfigManager.confirm_config_set(config_file)
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    _update_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name])
    for table_name in tables_in_database:
        cfg = ConfigManager(config, table_name)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table_name, engine)
        UserClass = type(table_name, (DBUserClass,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        rl = RecordList(sess, UserClass, cfg, compute_metadata=True)
        if view:
            print(rl.get_columns())
        else:
            print(rl.summarize())
