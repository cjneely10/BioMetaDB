#!/usr/bin/env python3

from Accessories.arg_parse import ArgParse
from Accessories.program_caller import ProgramCaller
from DBOperations.create_table_in_existing_database import create_table_in_existing_database
from DBOperations.create_database import create_database
from DBOperations.delete_from_table import delete_from_table
from DBOperations.remove_columns_from_table import remove_columns_from_table
from DBOperations.remove_table_from_database import remove_table_from_database
from DBOperations.update_existing_table import update_existing_table
from Exceptions.config_manager_exceptions import TableNameNotFoundError


if __name__ == "__main__":
    args_list = [
        [["program"],
         {"help": "Program to run"}],
        [["-n", "--db_name"],
         {"help": "Name of database"}],
        [["-w", "--working_directory"],
         {"help": "Absolute path for initializing database directories"}],
        [["-t", "--table_name"],
         {"help": "Name of database table", "default": "None"}],
        [["-d", "--directory_name"],
         {"help": "Directory path with bio data (fasta or fastq)", "default": "None"}],
        [["-f", "--data_file"],
         {"help": ".tsv or .csv file to add", "default": "None"}],
        [["-l", "--list_file"],
         {"help": "Comma-separated list of files ids to remove", "default": "None"}],
        [["-r", "--retain"],
         {"help": "Retain files after deleting table (default True)", "default": True}],
        [["-c", "--config_file"],
         {"help": "Config file for loading database schema"}],
        [["-a", "--alias"],
         {"help": "Provide alias for locating and creating table class", "default": "None"}],
    ]
    programs = {
        "INIT":                     create_database,
        "UPDATE":                   update_existing_table,
        "CREATE":                   create_table_in_existing_database,
        "REMOVECOL":                remove_columns_from_table,
        "DELETE":                   delete_from_table,
        "REMOVE":                   remove_table_from_database,
    }
    flags = {
        "INIT":                 ("db_name", "table_name", "directory_name", "data_file", "working_directory", "alias"),
        "CREATE":               ("config_file", "table_name", "directory_name", "data_file", "alias"),
        "UPDATE":               ("config_file", "table_name", "directory_name", "data_file", "alias"),
        "REMOVECOL":            ("config_file", "table_name", "list_file", "alias"),
        "DELETE":               ("config_file", "table_name", "list_file", "alias"),
        "REMOVE":               ("config_file", "table_name", "alias"),
    }
    errors = {
        TableNameNotFoundError:     "Name of table not found",
    }
    _help = {
        "INIT":             "Initialize database with starting table, fasta directory, and/or data files",
        "CREATE":           "Create a new table in an existing database, optionally populate using data files",
        "UPDATE":           "Update values in existing table or add new sequences",
        "REMOVECOL":        "Remove list of columns (including data) from table",
        "DELETE":           "Delete list of ids from database tables, remove associated files",
        "REMOVE":           "Delete table and all associated data from database",
    }

    ap = ArgParse(args_list,
                  description=ArgParse.description_builder("dbdm:\tManaging database operations.",
                                                           _help, flags))

    pc = ProgramCaller(programs=programs, flags=flags, _help=_help, errors=errors)

    pc.run(ap.args, debug=True)
