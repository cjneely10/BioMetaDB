import os
import json
import shutil
from datetime import datetime
from string import punctuation
from sqlalchemy.orm import mapper
from sqlalchemy import Column, Table, Integer, String, MetaData
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Accessories.bio_ops import BioOps
from BioMetaDB.Models.functions import DBUserClass
from BioMetaDB.DBManagers.type_mapper import TypeMapper
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Config.directory_manager import Directories
from BioMetaDB.DBManagers.update_manager import UpdateManager

"""
Script holds ClassManager, which links together database class generation,
table creation, and class loading

"""

unusable_punctuation = set(punctuation) - set("_")


class ClassManager:
    default_data = {
        "Float": 0.0,
        "Integer": 0,
        "String": "",
        "VARCHAR": "",
        "Boolean": False,
    }

    @staticmethod
    def create_initial_table_in_db(db_name, working_dir, table_name, data_types, silent, initial=True):
        """ Creates initial database and tables

        :param initial: (bool)      Initial table or not
        :param db_name: (str)       Name of database to create
        :param working_dir: (str)   Path to project folder
        :param table_name: (str)    Name of table to create
        :param data_types: (Dict[str, str) Attributes of class as dictionary
        :return:
        """
        db_dir = os.path.join(working_dir, Directories.DATABASE)
        table_dir = os.path.join(db_dir, table_name)
        classes_dir = os.path.join(working_dir, Directories.CLASSES)
        print_if_not_silent(silent, " ..Generating table class from data file")
        data_types = ClassManager.correct_dict(data_types)
        engine = None
        if not initial:
            engine = BaseData.get_engine(db_dir, db_name + ".db")
        t, metadata = ClassManager.generate_class(table_name, data_types, db_dir, db_name, table_dir, engine=engine)
        # Add functions for accessing to table
        print_if_not_silent(silent, " ..Creating tables")
        if not initial:
            t.create(bind=engine)
        else:
            metadata.create_all()
        classes_out_file = os.path.join(classes_dir, table_name + ".json")
        print_if_not_silent(silent, " ..Saving table data as JSON to %s" % classes_out_file)
        ClassManager.write_class(data_types, classes_out_file)

    @staticmethod
    def populate_data_to_existing_table(table_name, count_table_object, config, genome_files_to_add, directory_name,
                                        silent, alias=None):
        """ Method will load data from CountTable into database

        :param silent:
        :param directory_name:
        :param alias:
        :param genome_files_to_add:
        :param count_table_object:
        :param table_name:
        :param config: (object)  ConfigManager object
        :return:
        """
        print_if_not_silent(silent, "\nPopulating schema")
        print_if_not_silent(silent, " ..Loading database")
        engine = BaseData.get_engine(config.db_dir, config.db_name + ".db")
        sess = BaseData.get_session_from_engine(engine)
        print_if_not_silent(silent, " ..Collecting class data")
        TableClass = ClassManager.get_class_orm(table_name, engine)
        print_if_not_silent(silent, " ..Determining updates")
        # Or operation on sets to get all ids to add
        try:
            ids_to_add = set(count_table_object.file_contents.keys()) | set(genome_files_to_add)
        except AttributeError:
            ids_to_add = set(genome_files_to_add)
        table_class_attrs_keys = set(ClassManager.correct_iterable(ClassManager.get_class_as_dict(config).keys()))
        if count_table_object is not None:
            data_file_attrs_keys = set(ClassManager.correct_iterable(
                key for key in count_table_object.header if key not in ("", " ", "#")))
        else:
            data_file_attrs_keys = set()
        # Get combined values for writing to final JSON file
        try:
            combined_attrs = {**ClassManager.correct_dict(ClassManager.get_class_as_dict(config)),
                              **ClassManager.correct_dict(TypeMapper.get_translated_types(count_table_object,
                                                                                          TypeMapper.py_type_to_string))}
        except AttributeError:
            combined_attrs = ClassManager.correct_dict(ClassManager.get_class_as_dict(config))
        # Update manager
        # Initialize with DB class name, ConfigManager instance
        # Will create csv file of all existing data,
        # If differences found between what is in database table and what is in datafile
        if len(table_class_attrs_keys - data_file_attrs_keys) > 1:
            print_if_not_silent(silent, "\n!! New column data detected, calling update manager !!")
            update_manager = UpdateManager(config, ClassManager.get_class_as_dict(config), sess)
            table_copy_csv = update_manager.create_table_copy(datetime.today().strftime("%Y%m%d"), TableClass, silent)
            print_if_not_silent(silent, " ..Combining existing columns with new headers")
            UpdatedDBClass, metadata = ClassManager.generate_class(config.table_name,
                                                                   {key: value
                                                                    for key, value in
                                                                    combined_attrs.items()},
                                                                   config.db_dir,
                                                                   config.db_name,
                                                                   config.table_dir)
            ClassManager.write_class(combined_attrs, config.classes_file)
            # config.update_config_file(table_name)
            UpdateManager.delete_old_table_and_populate(engine, TableClass, UpdatedDBClass, table_copy_csv, table_name,
                                                         sess, silent)
            TableClass = UpdatedDBClass
            print_if_not_silent(silent, " ..Complete!\n")
        to_add = []
        UserClass = type(alias or table_name, (DBUserClass,), {})
        mapper(UserClass, TableClass)
        try:
            corrected_header = ClassManager.correct_iterable(count_table_object.header)
        except AttributeError:
            corrected_header = None
        existing_records = 0
        new_records = 0
        new_records_no_files = 0
        print_if_not_silent(silent, "\nGathering data by record:")
        if '' in ids_to_add:
            ids_to_add.remove('')
        for _id_ in ids_to_add:
            print_if_not_silent(silent, " ...Checking for record %s" % _id_)
            record = sess.query(UserClass).filter_by(_id=_id_).first()
            if record:
                print_if_not_silent(silent, " ....Record exists, updating with new values\n")
                existing_records += 1
                # Add values in the table that are already in the database class
                if corrected_header:
                    for attr in corrected_header:
                        try:
                            setattr(record, attr, count_table_object.get_at(_id_, corrected_header.index(attr)))
                        except KeyError:
                            continue
            else:
                if directory_name != "None":
                    print_if_not_silent(silent, " ....Moving new record from %s to %s" % (directory_name,
                                                                                          config.rel_db_dir))
                    try:
                        shutil.copy(os.path.join(directory_name, _id_),
                                    os.path.join(config.table_dir, _id_))
                        new_records += 1
                    except FileNotFoundError:
                        new_records_no_files += 1
                else:
                    new_records_no_files += 1
                db_object = UserClass()
                print_if_not_silent(silent, " ....Setting values for record %s in database\n" % _id_)
                setattr(db_object, "_id", _id_)
                setattr(db_object, "location", os.path.join(config.db_dir, table_name))
                try:
                    setattr(db_object, "data_type", BioOps.get_type(_id_))
                except KeyError:
                    setattr(db_object, "data_type", "unknown")
                try:
                    if corrected_header:
                        for attr in corrected_header:
                            setattr(db_object, attr, count_table_object.get_at(_id_, corrected_header.index(attr)))
                except KeyError:
                    continue
                to_add.append(db_object)
        for val in to_add:
            sess.add(val)
        sess.commit()
        print_if_not_silent(silent, " %i existing records updated" % existing_records)
        print_if_not_silent(silent, " %i new records added" % new_records)
        print_if_not_silent(silent, " %i new records without data files added\n" % new_records_no_files)
        print_if_not_silent(silent, "Complete!\n")
        return combined_attrs

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
    def get_class_as_dict(cfg):
        """ Primary method for loading a class from the database

        :param cfg:
        :return:
        """
        with open(cfg.classes_file, "r") as json_data:
            class_as_dict = dict(json.load(json_data))
        return class_as_dict

    @staticmethod
    def get_class_orm(table_name, engine):
        """ Method for loading a class' ORM from the database

        :param engine:
        :param table_name:
        :return:
        """
        metadata = MetaData(bind=engine, reflect=True)
        return metadata.tables[table_name]

    @staticmethod
    def get_class(table_name, engine):
        """ Primary method for loading a class from the database

        :param alias:
        :param engine:
        :param table_name:
        :return:
        """
        metadata = MetaData(bind=engine, reflect=True)
        UserClass = type(table_name, (DBUserClass,), {})
        mapper(UserClass, metadata.tables[table_name])
        return UserClass

    @staticmethod
    def generate_class(table_name, class_as_dict, db_dir, db_name, table_dir, metadata=None, engine=None):
        """ Method generates class from dictionary and returns class

        :param metadata:
        :param table_name: (str)    Name of db table
        :param class_as_dict: (Dict[str, str]) Attributes of class as dictionary
        :param db_dir: (str)    Path to database directory
        :param db_name: (str)   Name of database
        :param table_dir: (str) Path to folder holding table/class files
        :return:
        """
        metadata = metadata or MetaData(bind=engine or BaseData.get_engine(db_dir, db_name), reflect=True)
        t = Table(table_name, metadata, Column('id', Integer, primary_key=True),
                  Column("_id", String, unique=True, index=True),
                  Column("data_type", String, index=True),
                  Column("location", String, index=True),
                  *(Column(key, TypeMapper.string_to_loaded_sql_type[value], index=True,
                           default=ClassManager.default_data[value]) for
                    key, value in class_as_dict.items() if key not in ("_id", "data_type", "location")))
        setattr(t, "basedir", table_dir)
        # for fxn in accessing_functions.keys():
        #     setattr(t, fxn, types.MethodType(accessing_functions[fxn], t))
        return t, metadata

    @staticmethod
    def correct_dict(class_as_dict):
        """

        :param class_as_dict:
        :return:
        """
        corrected_dict = {}
        for key in class_as_dict.keys():
            new_key = str(key).lower()
            for bad_char in unusable_punctuation:
                new_key = new_key.replace(bad_char, "")
            new_key = new_key.replace(" ", "_")
            corrected_dict[new_key] = class_as_dict[key]
        return corrected_dict

    @staticmethod
    def correct_iterable(iterable):
        """ Method will make each value in iterable SQL-safe

        :param iterable:
        :return:
        """
        new_iter = []

        for _iter in iterable:
            new_val = _iter.lower()
            for bad_char in unusable_punctuation:
                new_val = new_val.replace(bad_char, "")
            new_val = new_val.replace(" ", "_")
            new_iter.append(new_val)
        return new_iter
