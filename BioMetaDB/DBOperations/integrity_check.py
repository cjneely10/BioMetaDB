from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB import get_table


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
    table = get_table(config_file, table_name)

