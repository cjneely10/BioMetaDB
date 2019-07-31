# cython: language_level=3
import os
from sqlalchemy.orm import mapper
from random import randint
from datetime import datetime
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
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
    :param fixfile_prefix:
    :param tables_to_search:
    :return:
    """
    print("INTEGRITY:\tCheck project for data issues")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s" % db_name)
    print(" Tables in check:\t\t%s" % ", ".join(tables_to_search).rstrip(", "))
    print(" Fix file generated:\t\t%s" % fixfile_prefix)
    print(" Note: .fix file will auto-delete if no issues are found", "\n")


def _integrity_check_display_message_epilogue(passed, fix_file):
    if passed == 0:
        print("Integrity check complete with no errors!", "\n")
    else:
        print("Integrity check complete, see %s for errors!" % fix_file, "\n")


def integrity_check(config_file, table_name, alias, silent):
    """  Function called from dbdm that checks integrity and issues in project at all levels

    :param config_file:
    :param table_name:
    :param alias:l
    :return:
    """
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
    if table_name is None or (table_name == "None" and alias == "None"):
        tables_to_search = list(config[ConfigKeys.TABLES_TO_DB].keys())
    else:
        tables_to_search = [table_name, ]
    py_fixfile_name = "%s.%s.fix" % (datetime.today().strftime("%Y%m%d"),
                                     str(randint(1, 1001)))
    if not silent:
        _integrity_check_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name],
                                                 config[ConfigKeys.DATABASES][ConfigKeys.working_dir],
                                                 tables_to_search,
                                                 py_fixfile_name)
    im = IntegrityManager(config, py_fixfile_name, tables_to_search)
    # TODO: Implement table-level checks
    im.initialize_fix_file()
    im.initial_project_check()
    # im.table_check()
    for table in tables_to_search:
        cfg = ConfigManager(config, table)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table, engine)
        UserClass = type(table, (Record,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        im.record_check(sess, UserClass, table)
    if im.issues_found == 0:
        os.remove(py_fixfile_name)
    if not silent:
        _integrity_check_display_message_epilogue(im.issues_found, py_fixfile_name)
    del im
