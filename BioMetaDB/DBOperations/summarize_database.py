from sqlalchemy.orm import mapper
from BioMetaDB.DataStructures.record_list import RecordList
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys
from BioMetaDB.Exceptions.summarize_database_exceptions import SummarizeDBAssertString


"""
Script will hold functionality to display to stdout a summary of key project details

"""


def _summarize_display_message_prelude(db_name):
    """ Display summary of input parameters before displaying db summary

    :param db_name: (str)   Name of db
    :return:
    """
    print("SUMMARIZE:\tView summary of all tables in database")
    print(" Project root directory:\t%s" % db_name)
    print(" Name of database:\t\t%s.db\n" % db_name.strip(".db"))


def summarize_database(config_file, view, query, table_name, alias, write):
    """ Function will query all tables listed in the config file, outputting simple
    metrics to the screen

    :param alias:
    :param table_name:
    :param query:
    :param view:
    :param config_file:
    :return:
    """
    if not view:
        if query != "None":
            assert (query != "None" and (table_name != "None" or alias != "None")), SummarizeDBAssertString.QUERY_AND_TABLE_SET
        assert not (table_name != "None" and alias != "None"), SummarizeDBAssertString.ALIAS_OR_TABLE_ONLY
    config, config_file = ConfigManager.confirm_config_set(config_file)
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    _summarize_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name])
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
    if query == "None" and (table_name != "None" or alias != "None"):
        tables_in_database = (table_name, )
    for tbl_name in tables_in_database:
        cfg = ConfigManager(config, tbl_name)
        engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        TableClass = ClassManager.get_class_orm(tbl_name, engine)
        UserClass = type(tbl_name, (Record,), {})
        # Map to SQL orm
        mapper(UserClass, TableClass)
        # Display queried info for single table and break
        if not view and table_name == tbl_name:
            rl = RecordList(sess, UserClass, cfg, compute_metadata=True)
            if query != "None":
                rl.query(query)
            else:
                rl.query()
            if len(rl) != 1:
                print(rl.summarize())
            else:
                print(rl[0])
            break
        # Display column info for table
        elif query == "None" and view:
            rl = RecordList(sess, UserClass, cfg)
            # Do not need to query since only displaying columns
            print(rl.get_column_summary())
        elif write != "None":
            rl = RecordList(sess, UserClass, cfg)
            if query != "None":
                rl.query(query)
            else:
                rl.query()
            rl.write_records(write)
