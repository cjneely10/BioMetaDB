import os
from sqlalchemy.orm import mapper
from Models.models import BaseData
from Models.functions import DBUserClass
from Config.config_manager import Config
from Config.config_manager import ConfigKeys
from Config.config_manager import ConfigManager
from DBManagers.class_manager import ClassManager

"""

"""


def _remove_table_display_message_prelude(db_name, working_directory, table_name, alias):
    """ Display summary of input parameters before creating database

    :param alias:
    :param db_name: (str)   Name of db
    :param working_directory: (str) Path to working directory
    :param table_name: (str)    Table that will be created
    :return:
    """
    print("REMOVE:\tCreate table in existing database")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s.db" % db_name.strip(".db"))
    print(" Name of table:\t\t\t%s" % table_name, "\n")
    print(" Table aliases:\t\t\t%s" % alias)
    print("DATA:\tDelete table")
    print(" Table name:\t%s" % table_name, "\n")


def _remove_columns_display_message_epilogue():
    print("Table removed from database!", "\n")


def remove_table_from_database(config_file, table_name, alias):
    config = Config()
    config.read(config_file)
    if alias != "None":
        table_name = config[ConfigKeys.TABLES_TO_ALIAS][alias]
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
    UserClass = type(alias or table_name, (DBUserClass,), {})
    mapper(UserClass, TableClass)
    all_records = sess.query(UserClass).all()
    for record in all_records:
        if record:
            print(" ..Removing record %s" % record)
            os.remove(record.full_path())
    TableClass.drop(engine)
    cfg.remove_table_from_config_file(table_name)
    _remove_columns_display_message_epilogue()
    os.remove(cfg.classes_file)
    _remove_columns_display_message_epilogue()
