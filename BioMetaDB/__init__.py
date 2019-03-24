import os
import glob
from sqlalchemy.orm import mapper
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.Config.config_manager import ConfigManager, Config
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import ConfigKeys

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
    cfg = Config()
    config_path = glob.glob(os.path.join(config_path, "config/*.ini"))[0]
    cfg.read(config_path)
    if alias:
        table_name = cfg[ConfigKeys.TABLES_TO_ALIAS][alias]
    config = ConfigManager(cfg, table_name)
    # Get session to return
    engine = BaseData.get_engine(config.db_dir, config.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    # Generate table class and name based on presence of alias
    TableClass = ClassManager.get_class_orm(table_name, engine)
    UserClass = type(table_name, (DBUserClass,), {})
    # Map to SQL orm
    mapper(UserClass, TableClass)
    return sess, UserClass
