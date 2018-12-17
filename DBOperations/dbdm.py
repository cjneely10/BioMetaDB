#!/usr/bin/env python3

from Accessories.arg_parse import ArgParse
from Accessories.program_caller import ProgramCaller
from DBOperations.create_table import create_table
from DBOperations.update_table import update_table
from DBOperations.create_database import create_database
from DBOperations.delete_from_table import delete_from_table
from DBOperations.remove_columns_from_table import remove_columns_from_table
from DBOperations.remove_table_from_database import remove_table_from_database


if __name__ == "__main__":
    args_list = [
        [["program"],
         {"help": "Program to run"}],
        [["-n", "--db_name"],
         {"help": "Name of database"}],
        [["-w", "--working_directory"],
         {"help": "Absolute path for initializing database directories"}],
        [["-t", "--table_name"],
         {"help": "Name of database table"}],
        [["-d", "--directory_name"],
         {"help": "Directory path with genomic sequences", "default": "None"}],
        [["-m", "--data_file"],
         {"help": "Comma-separated list of .tsv or .csv files", "default": "None"}],
        [["-l", "--list_file"],
         {"help": "Comma-separated list of files ids to remove", "default": "None"}],
        [["-r", "--retain"],
         {"help": "Retain files after deleting table (default True)", "default": "None"}]

    ]
    programs = {
        "INIT":                     create_database,
        "CREATE":                   create_table,
        "UPDATE":                   update_table,
        "REMOVECOL":                remove_columns_from_table,
        "DELETE":                   delete_from_table,
        "REMOVE":                   remove_table_from_database,
    }
    flags = {
        "INIT":                 ("db_name", "table_name", "directory_name", "data_file", "working_directory"),
        "CREATE":               ("db_name", "table_name", "directory_name", "data_file"),
        "UPDATE":               ("db_name", "table_name", "directory_name", "data_file"),
        "REMOVECOL":            ("db_name", "table_name", "list_file"),
        "DELETE":               ("db_name", "table_name", "list_file"),
        "REMOVE":               ("db_name", "table_name"),
    }
    errors = {

    }
    _help = {
        "INIT":             "Initialize database with starting table, fasta directory, and/or data files",
        "CREATE":           "Create a new table in an existing database, optionally populate using data files",
        "UPDATE":           "Update values in existing table or add new sequences",
        "REMOVECOL":        "Remove list of columns (including data) from table",
        "DELETE":           "Delete list of genome ids from database tables (including those linked by foreign keys)",
        "REMOVE":           "Delete table from database",
    }

    ap = ArgParse(args_list,
                  description=ArgParse.description_builder("dbdm:\tManaging database operations.",
                                                           _help, flags))

    pc = ProgramCaller(programs=programs, flags=flags, _help=_help, errors=errors)

    pc.run(ap.args)
