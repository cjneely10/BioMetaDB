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


def summarize_database(config_file, view, query, table_name, alias, write, write_tsv, unique):
    """ Function will query all tables listed in the config file, outputting simple
    metrics to the screen

    :param config_file:
    :param view:
    :param query:
    :param table_name:
    :param alias:
    :param write:
    :param write_tsv:
    :return:
    """
    annot_rl = None
    if not view:
        if query != "None":
            assert (query != "None" and (table_name != "None" or alias != "None")), SummarizeDBAssertString.QUERY_AND_TABLE_SET
        assert not (table_name != "None" and alias != "None"), SummarizeDBAssertString.ALIAS_OR_TABLE_ONLY
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if not view.lower()[0] == "t":
        _summarize_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name])
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
    if query == "None" and (table_name != "None" or alias != "None"):
        tables_in_database = (table_name, )
    if table_name != "None" and ("~>" in query or "<~" in query):
        matching_records = []
        sess, UserClass, cfg = load_table_metadata(config, table_name)
        eval_sess, EvalClass, eval_cfg = load_table_metadata(config, "evaluation")
        annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=True)
        eval_rl = RecordList(eval_sess, EvalClass, eval_cfg, compute_metadata=True)
        if "~>" in query:
            evaluation_query, annotation_query = query.split("~>")[0:1]
        elif "<~" in query:
            annotation_query, evaluation_query = query.split("<~")[0:1]
        annot_rl.query(annotation_query)
        eval_rl.query(evaluation_query)
        eval_keys = [key.split(".")[0].lower() for key in eval_rl.keys()]
        for record in annot_rl:
            if record._id.split(".")[0].lower() in eval_keys:
                matching_records.append(record)
        annot_rl = RecordList(sess, UserClass, cfg, records_list=matching_records)
    for tbl_name in tables_in_database:
        sess, UserClass, cfg = load_table_metadata(config, tbl_name)
        if view == "None" and ((table_name != "None" and table_name == tbl_name) or (table_name == "None")) and write == "None":
            # Display queried info for single table and break
            if not annot_rl:
                annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=True)
                _handle_query(annot_rl, query)
            if len(annot_rl) != 1:
                print(annot_rl.summarize())
            else:
                print(annot_rl[0])
        annot_rl = RecordList(sess, UserClass, cfg)
        # Display column info for table
        if view.lower()[0] == "c":
            # Display queried info for single table and break
            # Do not need to query since only displaying columns
            print(annot_rl.columns_summary())
        elif view.lower()[0] == "t":
            # Display queried info for single table and break
            # Do not need to query since only displaying columns
            print(annot_rl.table_name_summary())
        if write != "None" and table_name == tbl_name:
            if not annot_rl:
                _handle_query(annot_rl, query)
            annot_rl.write_records(write)
        elif write_tsv != "None" and table_name == tbl_name:
            if not annot_rl:
                _handle_query(annot_rl, query)
            annot_rl.write_tsv(write_tsv)
        if unique != 'None' and table_name == tbl_name:
            if not annot_rl:
                _handle_query(annot_rl)
            col_vals = set()
            for record in annot_rl:
                col_vals.add(getattr(record, unique, "None"))
            col_vals = sorted([col_vals])
            for val in col_vals:
                print(val)


def load_table_metadata(config, tbl_name):
    cfg = ConfigManager(config, tbl_name)
    engine = BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db")
    sess = BaseData.get_session_from_engine(engine)
    TableClass = ClassManager.get_class_orm(tbl_name, engine)
    UserClass = type(tbl_name, (Record,), {})
    # Map to SQL orm
    mapper(UserClass, TableClass)
    # Display queried info for single table and break
    return sess, UserClass, cfg


def _handle_query(rl, query="None"):
    if query != "None":
        rl.query(query)
    else:
        rl.query()
