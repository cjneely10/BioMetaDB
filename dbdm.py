#!/usr/bin/env python3
from BioMetaDB.DBOperations.fix import fix
from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.DBOperations.move_project import move_project
from BioMetaDB.Accessories.program_caller import ProgramCaller
from BioMetaDB.DBOperations.integrity_check import integrity_check
from BioMetaDB.DBOperations.create_database import create_database
from BioMetaDB.DBOperations.delete_from_table import delete_from_table
from BioMetaDB.DBOperations.summarize_database import summarize_database
from BioMetaDB.DBOperations.update_existing_table import update_existing_table
from BioMetaDB.Exceptions.record_list_exceptions import ColumnNameNotFoundError
from BioMetaDB.Exceptions.config_manager_exceptions import TableNameNotFoundError, MultipleTablesFoundError, \
    ConfigFileNotFound
from BioMetaDB.DBOperations.remove_columns_from_table import remove_columns_from_table
from BioMetaDB.DBOperations.remove_table_from_database import remove_table_from_database
from BioMetaDB.Exceptions.remove_columns_from_table_exceptions import ListFileNotProvidedError
from BioMetaDB.DBOperations.create_table_in_existing_database import create_table_in_existing_database


def run():
    args_list = (
        (("program",),
         {"help": "Program to run"}),
        (("-n", "--db_name"),
         {"help": "Name of database"}),
        (("-t", "--table_name"),
         {"help": "Name of database table", "default": "None"}),
        (("-d", "--directory_name"),
         {"help": "Directory path with bio data (fasta or fastq)", "default": "None"}),
        (("-f", "--data_file"),
         {"help": ".tsv or .csv file to add, or .fix file to integrate", "default": "None"}),
        (("-l", "--list_file"),
         {"help": "File with list of items, typically ids or column names", "default": "None"}),
        (("-c", "--config_file"),
         {"help": "/path/to/BioMetaDB-project-directory - Can omit if no other BioMetaDB project present"}),
        (("-a", "--alias"),
         {"help": "Provide alias for locating and creating table class", "default": "None"}),
        (("-s", "--silent"),
         {"help": "Silence all standard output (Standard error still displays to screen)", "action": "store_true",
          "default": False}),
        (("-v", "--view"),
         {"help": "View (c)olumns or (t)ables with SUMMARIZE", "default": "None"}),
        (("-q", "--query"),
         {"help": "evaluation ~> genome; function -> gen; eval >> fxn; eval ~> fxn -> gen;", "default": "None"}),
        (("-u", "--unique"),
         {"help": "View unique values of column using SUMMARIZE", "default": "None"}),
        (("-i", "--integrity_cancel"),
         {"help": "Cancel integrity check", "default": False, "action": "store_true"}),
        (("-w", "--write"),
         {"help": "Write fastx records from SUMMARIZE to outfile", "default": "None"}),
        (("-x", "--write_tsv"),
         {"help": "Write table record metadata from SUMMARIZE to outfile", "default": "None"}),
        (("-p", "--path"),
         {"help": "New path for moving project in MOVE command", "default": "None"}),
        (("-r", "--truncate"),
         {"help": "Return only ID of annotation and not the complete description, excluding Prokka, default False",
          "default": False, "action": "store_true"}),
    )
    programs = {
        "INIT":                     create_database,
        "UPDATE":                   update_existing_table,
        "CREATE":                   create_table_in_existing_database,
        "REMOVECOL":                remove_columns_from_table,
        "DELETE":                   delete_from_table,
        "REMOVE":                   remove_table_from_database,
        "SUMMARIZE":                summarize_database,
        "MOVE":                     move_project,
        "INTEGRITY":                integrity_check,
        "FIX":                      fix,
    }
    flags = {
        "INIT":                 ("db_name", "table_name", "directory_name", "data_file", "alias", "silent", "integrity_cancel"),
        "CREATE":               ("config_file", "table_name", "directory_name", "data_file", "alias", "silent", "integrity_cancel"),
        "UPDATE":               ("config_file", "table_name", "directory_name", "data_file", "alias", "silent", "integrity_cancel"),
        "REMOVECOL":            ("config_file", "table_name", "list_file", "alias", "silent", "integrity_cancel"),
        "DELETE":               ("config_file", "table_name", "list_file", "alias", "silent", "integrity_cancel"),
        "REMOVE":               ("config_file", "table_name", "alias", "silent", "integrity_cancel"),
        "SUMMARIZE":            ("config_file", "view", "query", "table_name", "alias", "write", "write_tsv", "unique", "truncate"),
        "MOVE":                 ("config_file", "path", "integrity_cancel", "silent"),
        "INTEGRITY":            ("config_file", "table_name", "alias", "silent"),
        "FIX":                  ("config_file", "data_file", "silent", "integrity_cancel"),
    }
    errors = {
        TableNameNotFoundError:     "Name of table not found",
        ListFileNotProvidedError:   "List file not provided",
        ColumnNameNotFoundError:    "Column name not in table",
        MultipleTablesFoundError:   "Multiple projects located - specify with -c /path/to/BioMetaDB-project-directory",
        ConfigFileNotFound:         "Config file for project not found",
    }
    _help = {
        "INIT":             "Initialize database with starting table, fasta directory, and/or data files",
        "CREATE":           "Create a new table in an existing database, optionally populate using data files",
        "UPDATE":           "Update values in existing table or add new sequences",
        "REMOVECOL":        "Remove column list (including data) from table",
        "DELETE":           "Delete list of ids from database tables, remove associated files",
        "REMOVE":           "Remove table and all associated data from database",
        "SUMMARIZE":        "Summarize project and query data. Write records or metadata to file",
        "MOVE":             "Move project to new location",
        "INTEGRITY":        "Queries project database and structure to generate .fix file for possible issues",
        "FIX":              "Repairs errors in DB structure using .fix file",
    }

    ap = ArgParse(args_list,
                  description=ArgParse.description_builder("dbdm:\tManage BioMetaDB project",
                                                           _help, flags))

    pc = ProgramCaller(programs=programs, flags=flags, _help=_help, errors=errors)

    pc.run(ap.args, debug=True)


if __name__ == "__main__":
    run()
