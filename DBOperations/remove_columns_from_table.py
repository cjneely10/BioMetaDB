import os
import glob
from datetime import datetime
from Models.models import BaseData
from Config.config_manager import Config
from Config.config_manager import ConfigKeys
from Config.config_manager import ConfigManager
from DBManagers.class_manager import ClassManager
from DBManagers.update_manager import UpdateManager
from Exceptions.remove_columns_from_table_exceptions import ListFileNotProvidedError

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
    print(" Table aliases:\t\t%s" % alias)
    print("DATA:\tRemove columns from schema")
    print(" Do not include columns:\t%s" % ",".join(cols_to_remove).strip(","), "\n")


def _remove_columns_display_message_epilogue():
    print("Columns removed from database!", "\n")


def remove_columns_from_table(config_file, table_name, list_file, alias, silent):
    """

    :param silent:
    :param config_file:
    :param table_name:
    :param list_file:
    :param alias:
    :return:
    """
    config = Config()
    config_file = glob.glob(os.path.join(config_file, "config/*.ini"))[0]
    config.read(config_file)
    if alias != "None":
        table_name = config[ConfigKeys.TABLES_TO_ALIAS][alias]
    if list_file == "None":
        raise ListFileNotProvidedError
    columns_to_remove = set(line.rstrip("\r\n") for line in open(list_file, "r"))
    if silent == "n":
        _remove_columns_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir],
            table_name,
            alias,
            columns_to_remove
        )

    cfg = ConfigManager(config, table_name)
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
