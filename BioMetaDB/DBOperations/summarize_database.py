from sqlalchemy.orm import mapper
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.DataStructures.record_list import RecordList
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


def summarize_database(config_file, view, query, table_name, alias, write, write_tsv, unique, truncate):
    """ Function will query all tables listed in the config file, outputting simple
    metrics to the screen

    :param config_file:
    :param view:
    :param query:
    :param table_name:
    :param alias:
    :param write:
    :param write_tsv:
    :param truncate:
    :return:
    """
    if not view:
        # if query != "None": assert (query != "None" and (table_name != "None" or alias != "None")),
        # SummarizeDBAssertString.QUERY_AND_TABLE_SET assert not (table_name != "None" and alias != "None"),
        # SummarizeDBAssertString.ALIAS_OR_TABLE_ONLY
        if table_name != "None" and alias != "None":
            print(SummarizeDBAssertString.ALIAS_OR_TABLE_ONLY)
            exit(1)
    config, config_file = ConfigManager.confirm_config_set(config_file)
    if not view.lower()[0] == "t":
        _summarize_display_message_prelude(config[ConfigKeys.DATABASES][ConfigKeys.db_name])
    if alias != "None":
        table_name = ConfigManager.get_name_by_alias(alias, config)
    if table_name != "None" or alias != "None":
        tables_in_database = (table_name, )
    else:
        tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    if ("~>" in query) and ("->" in query):
        # assert table_name == 'None', "Query cannot contain '~>/->' statement with a table name"
        if table_name != 'None':
            print("Query cannot contain '~>/->' statement with a table name")
            exit(1)
        matching_records = []
        eval_sess, EvalClass, eval_cfg = load_table_metadata(config, "evaluation")
        eval_rl = RecordList(eval_sess, EvalClass, eval_cfg, compute_metadata=False, truncate=truncate)
        fxn_sess, FxnClass, fxn_cfg = load_table_metadata(config, "functions")
        fxn_rl = RecordList(fxn_sess, FxnClass, fxn_cfg, compute_metadata=False, truncate=truncate)
        evaluation_query, block_1 = query.split("~>")
        function_query, annotation_query = block_1.split("->")
        if evaluation_query.replace(" ", "") != '':
            eval_rl.query(evaluation_query)
        else:
            eval_rl.query()
        if function_query.replace(" ", "") != '':
            fxn_rl.query(function_query)
        else:
            fxn_rl.query()
        for record in eval_rl:
            if record in fxn_rl:
                record_id = record._id.split(".")[0]
                sess, UserClass, cfg = load_table_metadata(config, record_id)
                annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=False, truncate=truncate)
                _handle_query(annot_rl, annotation_query)
                if write_tsv != 'None':
                    annot_rl.write_tsv(record_id + "." + write_tsv.replace(".tsv", "") + ".tsv")
                for record_2 in annot_rl:
                    matching_records.append(record_2)
                if write_tsv == 'None' and write == 'None':
                    annot_rl.summarize()
        if matching_records and write != "None":
            rl = RecordList(compute_metadata=False, records_list=matching_records, truncate=truncate)
            rl.write_records(write)
        exit()
    if "~>" in query:
        # assert table_name == 'None', "Query cannot contain a '~>' statement with a table name"
        if table_name != 'None':
            print("Query cannot contain '~>' statement with a table name")
            exit(1)
        matching_records = []
        eval_sess, EvalClass, eval_cfg = load_table_metadata(config, "evaluation")
        eval_rl = RecordList(eval_sess, EvalClass, eval_cfg, compute_metadata=False, truncate=truncate)
        evaluation_query, annotation_query = query.split("~>")
        if evaluation_query.replace(" ", "") != '':
            eval_rl.query(evaluation_query)
        else:
            eval_rl.query()
        for record in eval_rl:
            record_id = record._id.split(".")[0]
            sess, UserClass, cfg = load_table_metadata(config, record_id)
            annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=False, truncate=truncate)
            _handle_query(annot_rl, annotation_query)
            if write_tsv != 'None':
                annot_rl.write_tsv(record_id + "." + write_tsv.replace(".tsv", "") + ".tsv")
            for record_2 in annot_rl:
                matching_records.append(record_2)
            if write_tsv == 'None' and write == 'None':
                annot_rl.summarize()
        if matching_records and write != "None":
            rl = RecordList(compute_metadata=False, records_list=matching_records, truncate=truncate)
            rl.write_records(write)
        exit()
    if "->" in query:
        # assert table_name == 'None', "Query cannot contain a '->' statement with a table name"
        if table_name != 'None':
            print("Query cannot contain '->' statement with a table name")
            exit(1)
        matching_records = []
        eval_sess, EvalClass, eval_cfg = load_table_metadata(config, "functions")
        eval_rl = RecordList(eval_sess, EvalClass, eval_cfg, compute_metadata=False, truncate=truncate)
        evaluation_query, annotation_query = query.split("->")
        if evaluation_query.replace(" ", "") != '':
            eval_rl.query(evaluation_query)
        else:
            eval_rl.query()
        for record in eval_rl:
            record_id = record._id.split(".")[0]
            sess, UserClass, cfg = load_table_metadata(config, record_id)
            annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=False, truncate=truncate)
            _handle_query(annot_rl, annotation_query)
            if write_tsv != 'None':
                annot_rl.write_tsv(record_id + "." + write_tsv.replace(".tsv", "") + ".tsv")
            for record_2 in annot_rl:
                matching_records.append(record_2)
            if write_tsv == 'None' and write == 'None':
                annot_rl.summarize()
        if matching_records and write != "None":
            rl = RecordList(compute_metadata=False, records_list=matching_records, truncate=truncate)
            rl.write_records(write)
        exit()
    if ">>" in query:
        # assert table_name == 'None', "Query cannot contain a '>>' statement with a table name"
        if table_name != 'None':
            print("Query cannot contain '>>' statement with a table name")
            exit(1)
        eval_sess, EvalClass, eval_cfg = load_table_metadata(config, "evaluation")
        eval_rl = RecordList(eval_sess, EvalClass, eval_cfg, compute_metadata=False, truncate=truncate)
        evaluation_query, annotation_query = query.split(">>")
        if evaluation_query.replace(" ", "") != '':
            eval_rl.query(evaluation_query)
        else:
            eval_rl.query()
        sess, UserClass, cfg = load_table_metadata(config, "functions")
        if len(eval_rl) > 0:
            in_query = ""
            for record in eval_rl:
                in_query += "_id == '%s' OR " % record._id
            annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=False, truncate=truncate)
            if annotation_query.replace(" ", "") != '':
                annot_rl.query(annotation_query + " AND " + in_query[:-4])
            else:
                annot_rl.query(in_query[:-4])
            if annot_rl is not None:
                if write != "None":
                    annot_rl.write_records(write)
                if write_tsv != "None":
                    annot_rl.write_tsv(write_tsv.replace(".tsv", "") + ".tsv")
                if write_tsv == 'None' and write == 'None':
                    annot_rl.summarize()
        else:
            eval_rl.summarize()
        exit()
    if view == "None" and unique == 'None' and write == "None" and write_tsv == "None":
        for tbl_name in tables_in_database:
            # Display queried info for single table and break
            if table_name == 'None' or table_name == tbl_name:
                sess, UserClass, cfg = load_table_metadata(config, tbl_name)
                annot_rl = RecordList(sess, UserClass, cfg, compute_metadata=True, truncate=truncate)
                _handle_query(annot_rl, query)
                if len(annot_rl) > 1:
                    annot_rl.summarize()
                elif len(annot_rl) == 1:
                    print(annot_rl[0])
    else:
        for tbl_name in tables_in_database:
            if table_name == tbl_name:
                sess, UserClass, cfg = load_table_metadata(config, tbl_name)
                annot_rl = RecordList(sess, UserClass, cfg, truncate=truncate)
                # Display column info for table
                if view.lower()[0] == "c":
                    # Display queried info for single table and break
                    # Do not need to query since only displaying columns
                    annot_rl.columns_summary()
                elif view.lower()[0] == "t":
                    # Display queried info for single table and break
                    # Do not need to query since only displaying columns
                    annot_rl.table_name_summary()
                if write != "None":
                    _handle_query(annot_rl, query)
                    annot_rl.write_records(write)
                if write_tsv != "None":
                    _handle_query(annot_rl, query)
                    annot_rl.write_tsv(write_tsv)
                if unique != 'None':
                    _handle_query(annot_rl)
                    col_vals = set()
                    for record in annot_rl:
                        val = getattr(record, unique, "None")
                        if val:
                            col_vals.add(val)
                    col_vals = sorted(col_vals)
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
