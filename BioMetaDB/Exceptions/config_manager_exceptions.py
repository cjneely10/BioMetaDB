from BioMetaDB.Exceptions.error import Error


class TableNameNotFoundError(Error):
    pass


class ConfigAssertString:
    CONFIG_FILE_NOT_PASSED = "Config file for project not passed"
    CONFIG_FILE_NOT_FOUND = "Config file for project not found"


class TableNameAssertString:
    TABLE_NOT_FOUND = "Table not found"
