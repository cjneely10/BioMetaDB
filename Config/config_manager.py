import os
from configparser import ConfigParser
from Config.directory_manager import Directories


class Config(ConfigParser):
    """ Placeholder class for calling configparser

    """
    pass


class ConfigKeys:
    TABLES_TO_DB = "TABLES_TO_DB"
    working_dir = "working_dir"
    class_dir = "class_dir"
    db_dir = "db_dir"
    rel_work_dir = "rel_work_dir"
    rel_db_dir = "rel_db_dir"
    rel_classes_dir = "rel_clases_dir"


class ConfigManager:

    def __init__(self, config, table_name):
        """ Serializes output from configparser object

        :param config: (Config)     Config object using project config file
        :param table_name: (str)    Name of table
        """
        self.working_dir = config[table_name][ConfigKeys.working_dir]
        self.db_name = config[ConfigKeys.TABLES_TO_DB][table_name]
        self.db_file = config[ConfigKeys.TABLES_TO_DB][table_name] + ".db"
        self.db_dir = os.path.join(config[table_name][ConfigKeys.working_dir], Directories.DATABASE)
        self.table_dir = config[table_name][ConfigKeys.class_dir]
        self.table_file = os.path.join(self.table_dir, table_name + ".json")
        self.rel_work_dir = config[table_name][ConfigKeys.rel_work_dir]
        self.rel_db_dir = config[table_name][ConfigKeys.rel_db_dir]
        self.rel_classes_dir = config[table_name][ConfigKeys.rel_classes_dir]
