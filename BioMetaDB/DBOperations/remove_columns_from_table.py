from datetime import datetime
from BioMetaDB.DBOperations.integrity_check import integrity_check
from BioMetaDB.Exceptions.config_manager_exceptions import TableNameAssertString
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBManagers.update_manager import UpdateManager
from BioMetaDB.Exceptions.remove_columns_from_table_exceptions import ListFileNotProvidedError

"""
Script will hold functionality for REMOVECOL, to remove columns from existing table data
Saves migration
Creates new database table model

"""


def _remove_columns_display_message_prelude(db_name, working_directory, table_name, alias, cols_to_remove):
    """ Display initial message summarizing operation on files

    :param db_name:
    :param working_directory:
    :param table_name:
    :param alias:
    :param cols_to_remove:
    :return:
    """
    print("REMOVECOL:\tRemove list of columns from database schema")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t%s" % db_name)
    print(" Name of table:\t\t%s" % table_name)
    print(" Table aliases:\t\t\t%s" % alias, "\n")
    print("DATA:\tRemove columns from schema")
    print(" Do not include columns:\t%s" % ",".join(cols_to_remove).strip(","), "\n")


def _remove_columns_display_message_epilogue():
    print("Columns removed from database!", "\n")


def remove_columns_from_table(config_file, table_name, list_file, alias, silent, integrity_cancel):
    """

    :param config_file:
    :param table_name:
    :param list_file:
    :param alias:
    :param silent:
    :param integrity_cancel:
    :return:
    """
    _cfg, _tbl, _sil, _al = config_file, table_name, silent, alias
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
        # assert table_name is not None, TableNameAssertString.TABLE_NOT_FOUND
        if table_name is None:
            print(TableNameAssertString.TABLE_NOT_FOUND)
            exit(1)
    if list_file == "None":
        raise ListFileNotProvidedError("Provide file with list of columns to delete")
    cfg = ConfigManager(config, table_name)
    columns_to_remove = set(line.rstrip("\r\n") for line in open(list_file, "r"))
    if not silent:
        _remove_columns_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            alias,
            columns_to_remove
        )

    engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    TableClass = ClassManager.get_class_orm(table_name, engine)
    update_manager = UpdateManager(cfg, ClassManager.get_class_as_dict(cfg), sess)
    table_copy_csv = update_manager.create_table_copy(datetime.today().strftime("%Y%m%d"), TableClass, silent)
    new_attrs = {key: value
                 for key, value
                 in ClassManager.correct_dict(ClassManager.get_class_as_dict(cfg)).items()
                 if key not in columns_to_remove}
    UpdatedDBClass, metadata = ClassManager.generate_class(
        cfg.table_name,
        new_attrs,
        cfg.db_dir,
        cfg.db_name,
        cfg.table_dir
    )
    ClassManager.write_class(new_attrs, cfg.classes_file)
    cfg.update_config_file(table_name)
    update_manager.delete_old_table_and_populate(
        engine,
        TableClass,
        UpdatedDBClass,
        table_copy_csv,
        table_name,
        sess,
        silent
    )
    if not silent:
        _remove_columns_display_message_epilogue()
    if not integrity_cancel:
        integrity_check(_cfg, _tbl, _al, _sil)
