from sqlalchemy.orm import mapper
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.Config.config_manager import ConfigManager, Config
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.DataStructures.record_list import RecordList

"""
Script is for top-level function and classes
This is meant for direct access by the user

"""


def get_table(config_path, table_name=None, alias=None):
    """ Primary method for users importing

    :param config_path:
    :param table_name:
    :param alias:
    :return:
    """
    # Load config data from file
    cfg, config_path = ConfigManager.confirm_config_set(config_path)
    if alias:
        table_name = ConfigManager.get_name_by_alias(alias, cfg)
    config = ConfigManager(cfg, table_name)
    # Get session to return
    engine = BaseData.get_engine(config.db_dir, config.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    # Generate table class and name based on presence of alias
    TableClass = ClassManager.get_class_orm(table_name, engine)
    UserClass = type(table_name, (Record,), {})
    # Map to SQL orm
    mapper(UserClass, TableClass)
    return RecordList(sess, UserClass, config)


def tables(config_path):
    cfg, config_path = ConfigManager.confirm_config_set(config_path)
    return list(cfg[ConfigKeys.TABLES_TO_DB].keys())
