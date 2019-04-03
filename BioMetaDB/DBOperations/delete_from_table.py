import os
from sqlalchemy.orm import mapper
from BioMetaDB.DBOperations.integrity_check import integrity_check
from BioMetaDB.Exceptions.config_manager_exceptions import TableNameAssertString
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager
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
    print(" Table aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tRemove records from database")
    print(" Records:\t%s" % ",".join(records_to_remove).strip(","), "\n")


def _remove_columns_display_message_epilogue():
    print("Records removed from database!", "\n")


def delete_from_table(config_file, table_name, list_file, alias, silent, integrity_cancel):
    """

    :param silent:
    :param config_file:
    :param table_name:
    :param list_file:
    :param alias:
    :return:
    """
    _cfg, _tbl, _sil, _al = config_file, table_name, silent, alias
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
        assert table_name is not None, TableNameAssertString.TABLE_NOT_FOUND
    if list_file == "None":
        raise ListFileNotProvidedError
    cfg = ConfigManager(config, table_name)
    ids_to_remove = set(line.rstrip("\r\n") for line in open(list_file, "r"))
    if not silent:
        _delete_records_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            alias,
            ids_to_remove
        )

    engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    TableClass = ClassManager.get_class_orm(table_name, engine)
    UserClass = type(table_name, (Record,), {})
    mapper(UserClass, TableClass)
    for _id in ids_to_remove:
        print_if_not_silent(silent, " ..Removing record %s" % _id)
        try:
            os.remove(sess.query(UserClass).filter_by(_id=_id).first().full_path())
        except TypeError:
            continue
        sess.delete(sess.query(UserClass).filter_by(_id=_id).first())
    sess.commit()
    if not silent:
        _remove_columns_display_message_epilogue()
    if not integrity_cancel:
        integrity_check(_cfg, _tbl, _al, _sil)
