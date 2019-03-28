import os
import shutil
from sqlalchemy.orm import mapper

from BioMetaDB.Exceptions.config_manager_exceptions import TableNameAssertString
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager

"""
Script will hold functionality for REMOVE, which removes a table from a database,
deleting all associated files

"""


def _remove_table_display_message_prelude(db_name, working_directory, table_name, alias):
    """ Display summary of input parameters before creating database

    :param alias:
    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Record that will be created
    :return:
    """
    print("REMOVE:\tCreate table in existing database")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name)
    print(" Record aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tDelete table")
    print(" Record name:\t%s" % table_name, "\n")


def _remove_columns_display_message_epilogue():
    print("Record removed from database!", "\n")


def remove_table_from_database(config_file, table_name, alias, silent):
    """ Function removes a given table from a database

    :param silent:
    :param config_file:
    :param table_name:
    :param alias:
    :return:
    """
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
        assert table_name is not None, TableNameAssertString.TABLE_NOT_FOUND
    if not silent:
        _remove_table_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            alias
        )

    cfg = ConfigManager(config, table_name)
    engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    TableClass = ClassManager.get_class_orm(table_name, engine)
    UserClass = type(table_name, (Record,), {})
    mapper(UserClass, TableClass)
    all_records = sess.query(UserClass).all()
    for record in all_records:
        if record:
            print_if_not_silent(silent, " ..Removing record %s" % record._id)
            try:
                os.remove(record.full_path())
            except OSError:
                continue
    TableClass.drop(engine)
    cfg.remove_table_from_config_file(table_name)
    os.remove(cfg.classes_file)
    shutil.rmtree(cfg.table_dir)
    if not silent:
        _remove_columns_display_message_epilogue()
