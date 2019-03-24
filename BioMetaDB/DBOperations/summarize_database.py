import os
import glob
from sqlalchemy.orm import mapper
from BioMetaDB.Exceptions.config_manager_exceptions import ConfigAssertString
from BioMetaDB.DataStructures.record_list import RecordList
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import Config, ConfigManager, ConfigKeys


"""
Script will hold functionality to display to stdout a summary of key project details

"""


def summarize_database(config_file):
    assert config_file != "None", ConfigAssertString.CONFIG_FILE_NOT_PASSED
    config = Config()
    config_file = glob.glob(os.path.join(config_file, "config/*.ini"))[0]
    assert config_file != [], ConfigAssertString.CONFIG_FILE_NOT_FOUND
    config.read(config_file)
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    for table_name in tables_in_database:
        cfg = ConfigManager(config, table_name)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(table_name, engine)
        UserClass = type(table_name, (DBUserClass,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        rl = RecordList(sess, UserClass, cfg)
        print(rl.get_summary_string())
