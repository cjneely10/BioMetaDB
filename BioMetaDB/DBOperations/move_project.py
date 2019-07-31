import os
import shutil

from sqlalchemy.orm import mapper

from BioMetaDB import BaseData, Record
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Config.config_manager import ConfigManager
from BioMetaDB.Config.directory_manager import Directories
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBOperations.summarize_database import load_table_metadata
from BioMetaDB.Serializers.count_table import CountTable
from BioMetaDB.DBOperations.integrity_check import integrity_check

"""
Script holds functionality for UPDATE, which updates existing/adds new records to database
Handles new column generation and SQL migration 

"""


def _move_project_display_message_prelude(project_name, old_path, new_path):
    """ Summary for moving project

    :param old_path: (str)
    :param new_path: (str)
    :return:
    """
    print("MOVE:\tMove project to new location")
    print(" Old project root directory:\t%s" % old_path.replace(project_name, ""))
    print(" New project root directory:\t%s" % new_path)


def _move_project_display_message_epilogue():
    print("Move complete!", "\n")


def move_project(config_file, path, silent):
    """

    :param db_name:
    :param config_file:
    :param silent:
    :return:
    """
    config, config_file = ConfigManager.confirm_config_set(config_file)
    old_path = config[ConfigKeys.DATABASES][ConfigKeys.working_dir]
    assert os.path.dirname(old_path) != os.path.abspath(path), \
        "Project exists in directory, cancelling"
    assert os.path.exists(path), "Path does not exist, exiting"
    project_name = config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir]
    if not silent:
        _move_project_display_message_prelude(
            project_name,
            old_path,
            path),
    # Move directory from old location to new location
    shutil.move(old_path, path)
    # Update config file with new location
    abs_path_working_dir = os.path.abspath(os.path.join(path, project_name))
    db_name = project_name
    config[ConfigKeys.DATABASES] = {
        ConfigKeys.db_name: db_name,
        ConfigKeys.working_dir: abs_path_working_dir,
        ConfigKeys.rel_work_dir: db_name,
        ConfigKeys.migrations_dir: os.path.join(abs_path_working_dir, Directories.MIGRATIONS),
        ConfigKeys.config_dir: os.path.join(abs_path_working_dir, Directories.CONFIG),
        ConfigKeys.db_dir: os.path.join(abs_path_working_dir, Directories.DATABASE),
        ConfigKeys.rel_db_dir: os.path.join(db_name, Directories.DATABASE),
    }
    with open(os.path.join(path, project_name, Directories.CONFIG, os.path.basename(config_file)), "w") as W:
        config.write(W)
    # Update location for each record in each table
    tables_in_database = config[ConfigKeys.TABLES_TO_DB].keys()
    engine = BaseData.get_engine(
        os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.working_dir], Directories.DATABASE),
        config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir] + ".db"
    )
    sess = BaseData.get_session_from_engine(engine)
    for tbl_name in tables_in_database:
        TableClass = ClassManager.get_class_orm(tbl_name, engine)
        UserClass = type(tbl_name, (Record,), {})
        mapper(UserClass, TableClass)
        for record in sess.query(UserClass).all():
            record.location = path
        sess.commit()
    _move_project_display_message_epilogue()
