#!/usr/bin/env python3

from BioMetaDB.DBOperations.fix import fix
from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.Accessories.program_caller import ProgramCaller
from BioMetaDB.DBOperations.integrity_check import integrity_check
from BioMetaDB.DBOperations.create_database import create_database
from BioMetaDB.DBOperations.delete_from_table import delete_from_table
from BioMetaDB.DBOperations.summarize_database import summarize_database
from BioMetaDB.DBOperations.update_existing_table import update_existing_table
from BioMetaDB.Exceptions.config_manager_exceptions import TableNameNotFoundError
from BioMetaDB.DBOperations.remove_columns_from_table import remove_columns_from_table
from BioMetaDB.DBOperations.remove_table_from_database import remove_table_from_database
from BioMetaDB.Exceptions.remove_columns_from_table_exceptions import ListFileNotProvidedError
from BioMetaDB.DBOperations.create_table_in_existing_database import create_table_in_existing_database


if __name__ == "__main__":
    args_list = (
        (("program",),
         {"help": "Program to run"}),
        (("-n", "--db_name"),
         {"help": "Name of database"}),
        (("-w", "--working_directory"),
         {"help": "Absolute path for initializing database directories"}),
        (("-t", "--table_name"),
         {"help": "Name of database table", "default": "None"}),
        (("-d", "--directory_name"),
         {"help": "Directory path with bio data (fasta or fastq)", "default": "None"}),
        (("-f", "--data_file"),
         {"help": ".tsv or .csv file to add", "default": "None"}),
        (("-l", "--list_file"),
         {"help": "Comma-separated list of files ids to remove", "default": "None"}),
        (("-c", "--config_file"),
         {"help": "Config file for loading database schema"}),
        (("-a", "--alias"),
         {"help": "Provide alias for locating and creating table class", "default": "None"}),
        (("-s", "--silent"),
         {"help": "Silence all standard output (Standard error still displays to screen)", "action": "store_true",
          "default": False}),
    )
    programs = {
        "INIT":                     create_database,
        "UPDATE":                   update_existing_table,
        "CREATE":                   create_table_in_existing_database,
        "REMOVECOL":                remove_columns_from_table,
        "DELETE":                   delete_from_table,
        "REMOVE":                   remove_table_from_database,
        "SUMMARIZE":                summarize_database,
        "INTEGRITY":                integrity_check,
        "FIX":                      fix,
    }
    flags = {
        "INIT":                 ("db_name", "table_name", "directory_name", "data_file", "working_directory", "alias",
                                 "silent"),
        "CREATE":               ("config_file", "table_name", "directory_name", "data_file", "alias", "silent"),
        "UPDATE":               ("config_file", "table_name", "directory_name", "data_file", "alias", "silent"),
        "REMOVECOL":            ("config_file", "table_name", "list_file", "alias", "silent"),
        "DELETE":               ("config_file", "table_name", "list_file", "alias", "silent"),
        "REMOVE":               ("config_file", "table_name", "alias", "silent"),
        "SUMMARIZE":            ("config_file",),
        "INTEGRITY":            ("config_file",),
        "FIX":                  ("data_file",),
    }
    errors = {
        TableNameNotFoundError:     "Name of table not found",
        ListFileNotProvidedError:   "List file not provided",
    }
    _help = {
        "INIT":             "Initialize database with starting table, fasta directory, and/or data files",
        "CREATE":           "Create a new table in an existing database, optionally populate using data files",
        "UPDATE":           "Update values in existing table or add new sequences",
        "REMOVECOL":        "Remove column list (including data) from table",
        "DELETE":           "Delete list of ids from database tables, remove associated files",
        "REMOVE":           "Remove table and all associated data from database",
        "SUMMARIZE":        "Quick summary of project",
        "INTEGRITY":        "Queries project database and structure to generate .fix file for possible issues",
        "FIX":              "Repairs errors in DB structure using .fix file",
    }

    ap = ArgParse(args_list,
                  description=ArgParse.description_builder("dbdm:\tManage BioMetaDB project",
                                                           _help, flags))

    pc = ProgramCaller(programs=programs, flags=flags, _help=_help, errors=errors)

    pc.run(ap.args, debug=True)
