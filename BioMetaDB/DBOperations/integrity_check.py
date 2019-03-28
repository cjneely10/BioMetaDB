from sqlalchemy.orm import mapper
from random import randint
from datetime import datetime
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBManagers.integrity_manager import IntegrityManager

"""
Script will hold functionality that allows user to fix integrity issues within the project structure
These issues include:
    

"""


def _integrity_check_display_message_prelude(db_name, working_directory, tables_to_search, fixfile_prefix):
    """ Display initial message summarizing operation on files

    :param db_name:
    :param working_directory:
    :param table_name:
    :param alias:
    :param fixfile_prefix:
    :return:
    """
    print("INTEGRITY:\tCheck project for data issues")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s" % db_name)
    print(" Tables in check:\t\t%s" % ", ".join(tables_to_search).rstrip(", "))
    print(" Fix file generated:\t\t%s" % fixfile_prefix, "\n")


def _integrity_check_display_message_epilogue():
    print("Integrity check complete!", "\n")


def integrity_check(config_file, table_name, alias):
    """

    :param config_file:
    :param table_name:
    :param alias:
    :return:
    """
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
    if table_name is None or (table_name == "None" and alias == "None"):
        tables_to_search = list(config[ConfigKeys.TABLES_TO_DB].keys())
    else:
        tables_to_search = [table_name,]
    py_fixfile_name = "{}.{}.{}.fix".format(datetime.today().strftime("%Y%m%d"),
                                            str(randint(1, 1001)), "_".join(tables_to_search))
    _integrity_check_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name],
                                             config[ConfigKeys.DATABASES][ConfigKeys.working_dir],
                                             tables_to_search,
                                             py_fixfile_name)
    im = IntegrityManager(config, py_fixfile_name, tables_to_search)
    im.initial_project_check()
    im.table_check()
    for table in tables_to_search:
        cfg = ConfigManager(config, table)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table, engine)
        UserClass = type(table, (DBUserClass,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        im.record_check(sess, UserClass, table)
    del im
    _integrity_check_display_message_epilogue()
