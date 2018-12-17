import os
import sys
import json
import types
import shutil
from sqlalchemy import Column, Table, Integer, String, MetaData
from sqlalchemy.orm import mapper
from Models.models import BaseData
from Config.directory_manager import Directories
from Models.functions import accessing_functions
from DBClassManager.type_mapper import TypeMapper
from Accessories.bio_ops import BioOps


class ClassManager:

    @staticmethod
    def create_db_and_initial_table(db_name, working_dir, table_name, data_types):
        """ Creates initial database and tables

        :param db_name: (str)       Name of database to create
        :param working_dir: (str)   Path to project folder
        :param table_name: (str)    Name of table to create
        :param data_types: (Dict[str, str) Attributes of class as dictionary
        :return:
        """
        db_dir = os.path.join(working_dir, Directories.DATABASE)
        table_dir = os.path.join(db_dir, table_name)
        classes_dir = os.path.join(working_dir, Directories.CLASSES)
        print("..Generating table class from data file")
        t, metadata = ClassManager._generate_class(table_name, data_types, db_dir, db_name, table_dir)
        # Add functions for accessing to table
        print("..Creating tables")
        metadata.create_all()
        classes_out_file = os.path.join(classes_dir, table_name + ".json")
        print("..Dumping object data as JSON to %s" % classes_out_file)
        ClassManager.write_class(data_types, classes_out_file)

    @staticmethod
    def populate_data_to_existing_table(table_name, count_table_object, config, genome_files_to_add, directory_name):
        """ Method will load data from CountTable into database

        :param genome_files_to_add:
        :param count_table_object:
        :param table_name:
        :param config:
        :return:
        """
        print("..Loading newly created database")
        sess = BaseData.get_session_from_engine(BaseData.get_engine(config.db_dir, config.db_name + ".db"))
        print("..Collecting class data")
        TableClass = ClassManager.get_class(config, table_name)
        print("..Determining updates")
        ids_to_add = set(count_table_object.file_contents.keys()) | set(genome_files_to_add)
        table_class_attrs = list(ClassManager._get_class_as_dict(config).keys())
        to_add = []
        print("..Copying files from %s to new database directory %s" % (directory_name, config.rel_db_dir))
        for _id_ in ids_to_add:
            print("...Checking for record %s" % _id_)
            record = sess.query(TableClass).first()
            if record:
                print("...Record exists, updating with new values")
                for attr in table_class_attrs:
                    setattr(record, attr, count_table_object.get(_id_, count_table_object.header.index(attr)))
            else:
                print("...Moving new record from %s to %s" % (directory_name, config.rel_db_dir))
                shutil.copy(os.path.join(directory_name, _id_), os.path.join(config.table_dir, _id_))
                db_object = TableClass()
                setattr(db_object, "_id", _id_)
                setattr(db_object, "location", os.path.join(config.db_dir, table_name))
                setattr(db_object, "data_type", BioOps.get_type(_id_))
                for attr in table_class_attrs:
                    setattr(db_object, attr, count_table_object.get_at(_id_, count_table_object.header.index(attr) - 1))
                to_add.append(db_object)
        for val in to_add:
            sess.add(val)
        sess.commit()
        print("Complete!")

    @staticmethod
    def write_class(data_types, class_output_file):
        """ Member writes python class as json object to file for loading

        :param data_types:
        :param class_output_file:
        :return:
        """
        with open(class_output_file, "w") as W:
            json.dump(data_types, W)

    @staticmethod
    def _get_class_as_dict(cfg):
        """ Primary method for loading a class from the database

        :param cfg:
        :return:
        """
        with open(cfg.table_file, "r") as json_data:
            class_as_dict = dict(json.load(json_data))
        return class_as_dict

    @staticmethod
    def get_class(cfg, table_name):
        """ Primary method for loading a class from the database

        :param cfg:
        :param table_name:
        :return:
        """
        metadata = MetaData(bind=BaseData.get_engine(cfg.db_dir, cfg.db_name + ".db"), reflect=True)
        UserClass = type(table_name, (), {})
        mapper(UserClass, metadata.tables[table_name])
        return UserClass

    @staticmethod
    def _generate_class(table_name, class_as_dict, db_dir, db_name, table_dir):
        """ Method generates class from dictionary and returns class

        :param table_name: (str)    Name of db table
        :param class_as_dict: (Dict[str, str) Attributes of class as dictionary
        :param db_dir: (str)    Path to database directory
        :param db_name: (str)   Name of database
        :param table_dir: (str) Path to folder holding table/class files
        :return:
        """
        default_data = {
            "Float": 0.0,
            "Integer": 0,
            "String": "",
            "Boolean": False,
        }
        metadata = MetaData(bind=BaseData.get_engine(db_dir, db_name), reflect=True)
        t = Table(table_name, metadata, Column('id', Integer, primary_key=True),
                  Column("_id", String, unique=True, index=True),
                  Column("data_type", String, index=True),
                  Column("location", String, index=True),
                  *(Column(key, TypeMapper.string_to_loaded_sql_type[value], index=True, default=default_data[value]) for
                    key, value in class_as_dict.items()))
        setattr(t, "basedir", table_dir)
        for fxn in accessing_functions.keys():
            setattr(t, fxn, types.MethodType(accessing_functions[fxn], t))
        UserClass = type(table_name, (), {})
        mapper(UserClass, t)
        return UserClass, metadata
