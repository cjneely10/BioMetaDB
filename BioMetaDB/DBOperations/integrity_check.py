from sqlalchemy.orm import mapper
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBManagers.integrity_manager import IntegrityManager

"""
Script will hold functionality that allows user to fix integrity issues within the project structure
These issues include:
    

"""


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
    tables_to_search = ["ALL", ]
    if table_name is None or (table_name == "None" and alias == "None"):
        tables_to_search = list(config[ConfigKeys.TABLES_TO_DB].keys())
    im = IntegrityManager(config, tables_to_search)
    for table in tables_to_search:
        cfg = ConfigManager(config, table)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table, engine)
        UserClass = type(table, (DBUserClass,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
    del im
