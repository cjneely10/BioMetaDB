import os
import glob
from configparser import ConfigParser
from BioMetaDB.Config.directory_manager import Directories
from BioMetaDB.Exceptions.config_manager_exceptions import TableNameNotFoundError
from BioMetaDB.Exceptions.config_manager_exceptions import ConfigAssertString


class Config(ConfigParser):
    """ Placeholder class for calling configparser

    """
    pass


class ConfigKeys:
    """ Wrapper class holds const strings for simple access

    """
    TABLES_TO_DB = "TABLES_TO_DB"
    TABLES_TO_ALIAS = "TABLES_TO_ALIAS"
    working_dir = "working_dir"
    migrations_dir = "migrations_dir"
    config_dir = "config_dir"
    class_dir = "class_dir"
    db_dir = "db_dir"
    rel_work_dir = "rel_work_dir"
    rel_db_dir = "rel_db_dir"
    rel_classes_dir = "rel_classes_dir"
    DATABASES = "DATABASES"
    db_name = "db_name"


class ConfigManager:

    def __init__(self, config, table_name):
        """ Serializes output from configparser object for ease of access

        :param config: (Config)     Config object using project config file
        :param table_name: (str)    Name of table
        """
        if table_name not in config[ConfigKeys.TABLES_TO_DB].keys():
            raise TableNameNotFoundError(table_name)
        self.config = config
        self.table_name = table_name
        self.db_name = config[ConfigKeys.TABLES_TO_DB][table_name]
        self.working_dir = config[ConfigKeys.DATABASES][ConfigKeys.working_dir]
        self.db_file = config[ConfigKeys.TABLES_TO_DB][table_name] + ".db"
        self.db_dir = os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.working_dir], Directories.DATABASE)
        self.table_dir = os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.db_dir], table_name)
        self.classes_dir = config[table_name][ConfigKeys.class_dir]
        self.classes_file = os.path.join(self.classes_dir, table_name + ".json")
        self.rel_work_dir = config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir]
        self.rel_db_dir = config[ConfigKeys.DATABASES][ConfigKeys.rel_db_dir]
        self.rel_classes_dir = config[table_name][ConfigKeys.rel_classes_dir]
        self.migrations_dir = config[ConfigKeys.DATABASES][ConfigKeys.migrations_dir]
        self.config_dir = config[ConfigKeys.DATABASES][ConfigKeys.config_dir]

    def update_config_file(self, table_name):
        """ Creates updated table info in config file, writes new file

        :param table_name:
        :return:
        """
        abs_path_working_dir = os.path.abspath(self.working_dir)
        self.config[table_name] = {
            ConfigKeys.working_dir: abs_path_working_dir,
            ConfigKeys.rel_work_dir: self.working_dir,
            ConfigKeys.rel_db_dir: os.path.join(self.working_dir, Directories.DATABASE),
            ConfigKeys.rel_classes_dir: os.path.join(self.working_dir, Directories.CLASSES),
            ConfigKeys.db_dir: os.path.join(abs_path_working_dir, Directories.DATABASE),
            ConfigKeys.class_dir: os.path.join(abs_path_working_dir, Directories.CLASSES),
            ConfigKeys.migrations_dir: os.path.join(abs_path_working_dir, Directories.MIGRATIONS),
        }
        self.config[ConfigKeys.TABLES_TO_DB][table_name] = self.db_name
        with open(os.path.join(os.path.join(self.working_dir, Directories.CONFIG), self.db_name + ".ini"), "w") as W:
            self.config.write(W)

    def remove_table_from_config_file(self, table_name):
        """ Removes table info from config file and rewrites

        :param table_name:
        :return:
        """
        del self.config[table_name]
        del self.config[ConfigKeys.TABLES_TO_DB][table_name]
        with open(os.path.join(os.path.join(self.working_dir, Directories.CONFIG), self.db_name + ".ini"), "w") as W:
            self.config.write(W)

    @staticmethod
    def confirm_config_set(config_file):
        """ Static method to confirm that the config file was passed and exists

        :param config_file:
        :return:
        """
        assert config_file != "None", ConfigAssertString.CONFIG_FILE_NOT_PASSED
        config = Config()
        config_file = glob.glob(os.path.join(config_file, "config/*.ini"))
        assert config_file != [], ConfigAssertString.CONFIG_FILE_NOT_FOUND
        config.read(config_file[0])
        return config, config_file[0]
