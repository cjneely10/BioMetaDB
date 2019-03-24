import os
import glob
from sqlalchemy.orm import mapper

from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.Config.config_manager import Config
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Exceptions.config_manager_exceptions import ConfigAssertString
from BioMetaDB.Exceptions.remove_columns_from_table_exceptions import ListFileNotProvidedError

"""
Script will hold functionality for DELETE, which deletes records from database and associated files

"""


def _delete_records_display_message_prelude(db_name, working_directory, table_name, alias, records_to_remove):
    """ Display initial message summarizing operation on files

    :param db_name:
    :param working_directory:
    :param table_name:
    :param alias:
    :param records_to_remove:
    :return:
    """
    print("DELETE:\tRemove list of records from database, delete associated files")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t%s" % db_name)
    print(" Name of table:\t\t%s" % table_name)
    print(" Table aliases:\t\t%s" % alias)
    print("DATA:\tRemove records from database")
    print(" Records:\t%s" % ",".join(records_to_remove).strip(","), "\n")


def _remove_columns_display_message_epilogue():
    print("Records removed from database!", "\n")


def delete_from_table(config_file, table_name, list_file, alias, silent):
    """

    :param silent:
    :param config_file:
    :param table_name:
    :param list_file:
    :param alias:
    :return:
    """
    assert config_file != "None", ConfigAssertString.CONFIG_FILE_NOT_PASSED
    config = Config()
    config_file = glob.glob(os.path.join(config_file, "config/*.ini"))
    assert config_file != [], ConfigAssertString.CONFIG_FILE_NOT_FOUND
    config.read(config_file[0])
    if alias != "None":
        table_name = config[ConfigKeys.TABLES_TO_ALIAS][alias]
    if list_file == "None":
        raise ListFileNotProvidedError
    ids_to_remove = set(line.rstrip("\r\n") for line in open(list_file, "r"))
    if not silent:
        _delete_records_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            alias,
            ids_to_remove
        )

    cfg = ConfigManager(config, table_name)
    engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    TableClass = ClassManager.get_class_orm(table_name, engine)
    UserClass = type(table_name, (DBUserClass,), {})
    mapper(UserClass, TableClass)
    for _id in ids_to_remove:
        print_if_not_silent(silent, " ..Removing record %s" % _id)
        os.remove(sess.query(UserClass).filter_by(_id=_id).first().full_path())
        sess.delete(sess.query(UserClass).filter_by(_id=_id).first())
    sess.commit()
    if not silent:
        _remove_columns_display_message_epilogue()
