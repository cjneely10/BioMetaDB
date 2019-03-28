#!/usr/bin/env python3

import os
import shutil
import sqlite3
import sqlalchemy
from Models.models import BaseData
from examples.planctomycetes import Planctomycetes
from Accessories.arg_parse import ArgParse
from Accessories.program_caller import ProgramCaller, db_validate

"""
Script handles database management operations

"""


@db_validate
def add_file(class_name, file_path, seq_type, *args, **kwargs):
    """ Primary method for adding a file not located in db directory to the directory
    Stored metadata to database

    :param class_name: (str)	Name of database class
    :param file_path: (str)	file to add to database
    :param seq_type: (str)	Determines location for moving file, referenced from .FileLocations of class
    """
    # Get table class as class and create database session
    table_class, sess = get_class(class_name)
    # Get file metadata from name
    _, path_and_file = os.path.splitdrive(file_path)
    _, file = os.path.split(path_and_file)
    file = file.split(".")
    # Correct datatype based on file extension
    if file[-1] == "fasta" or file[-1] == "fa":
        file[-1] = "fna"
    elif file[-1] == "fastq":
        file[-1] = "fq"
    elif "protein" in file:
        file[-1] = "faa"
    # Instantiate object using id from file name, location based on passed class,
    # and subfolder based on seq_type
    gen_id = ".".join(file[:-1])
    db_object = table_class(genome_id=gen_id, location=getattr(table_class.FileLocations, seq_type), data_type=file[-1])
    # Add to database and copy file to new path
    if input(
            "Add {} to database {} in {}? ".format(gen_id, table_class.__tablename__, table_class.db_name)).upper() in (
    "Y", "YES"):
        sess.add(db_object)
        shutil.copy(path_and_file, db_object.full_path())
        sess.commit()
        exit(0)


@db_validate
def remove_file(class_name, genome_id):
    """ Primary method for removing file and metadata from db

    :param class_name: (str)	Name of class to get from dictionary
    :param genome_id: (str)		Genome ID as stored in database
    """
    table_class, sess = get_class(class_name)
    if input("Are you sure you want to delete this file?\nWARNING: THIS CANNOT BE UNDONE: ").upper() in ("Y", "YES"):
        db_object = sess.query(table_class).filter(table_class.genome_id == genome_id).first()
        if db_object:
            os.remove(db_object.full_path())
            sess.delete(db_object)
            sess.commit()
            print("{} successfully deleted from {}!".format(genome_id, class_name))
        else:
            print("{} does not exist in {} within {}".format(genome_id, table_class.__tablename__, table_class.db_name))


def get_class(class_name):
    """ Returns class based on dictionary mapping and instantiated session object

    :param class_name: (str)	User-passed name of class
    :return Tuple[class, dbObject]:
    """
    table_class = classes[class_name]
    sess = BaseData.get_session(table_class.db_name)
    return table_class, sess


if __name__ == "__main__":
    args_list = [
        [["program"],
         {"help": "Select program"}],
        [["-f", "--file_path"],
         {"help": ".faa, .fna, or .fq file"}],
        [["-c", "--class_name"],
         {"help": "Name of Record"}],
        [["-s", "--seq_type"],
         {"help": "Sequence type (example GEN)"}],
        [["-g", "--genome_id"],
         {"help": "Genome ID"}]
    ]

    ap = ArgParse(args_list,
                  description="dbdm:\tProgram for managing database operations.\n\nAvailable Programs:\n\nADD: Add "
                              "file to database and move to directory\n\t(Req: -f, -c, -s)\n\nREMOVE: Remove sequence "
                              "from database and delete from directory\n\t(Req: -c, -g)")

    classes = {
        "Planctomycetes": Planctomycetes,
        "Plancto": Planctomycetes,
    }

    programs = {
        "ADD": add_file,
        "REMOVE": remove_file,
    }

    flags = {
        "ADD": ("file_path", "seq_type", "class_name"),
        "REMOVE": ("genome_id", "class_name")
    }

    errors = {
        IOError: "Error moving file to location, rolling back changes",
        AttributeError: "Database name not found",
        KeyError: "Record name not found",
        sqlite3.IntegrityError: "Sequence exists in database matching file's genome id, exiting",
        sqlalchemy.exc.IntegrityError: "Sequence exists in database matching file's genome id, exiting",
    }

    _help = {
        "ADD": "Adds file to database and copy file to database folder",
        "REMOVE": "Remove file from database and remove from database folder",
    }

    pc = ProgramCaller(flags=flags, programs=programs, classes=classes, errors=errors, _help=_help)

    pc.run(ap.args)
