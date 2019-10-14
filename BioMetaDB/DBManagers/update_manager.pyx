# cython: language_level=3
import os
import csv
import glob

from BioMetaDB.DBManagers.type_mapper import TypeMapper
from BioMetaDB.Models.functions import Record
from sqlalchemy.orm import mapper
from BioMetaDB.Accessories.ops import print_if_not_silent
from BioMetaDB.Serializers.count_table import CountTable


class UpdateManager:
    IGNORE = ("BaseData", "DataTypes", "FileLocations", "DBManager", "Base")
    MGMT_EXT = ".migrations.mgt"

    def __init__(self, object config_manager_object, dict class_as_dict, object session):
        self.cfg = config_manager_object
        self.class_as_dict = class_as_dict
        self.session = session

    def create_table_copy(self, str outfile_prefix, object DBClass, bint silent):
        """ Function writes a copy of data currently stored in the DB table

        :param silent:
        :param DBClass:
        :param outfile_prefix:
        :return:
        """
        print_if_not_silent(silent, " ..Creating deep copy of existing table")
        return self._write_to_file(*self._query_table(DBClass), outfile_prefix)

    @staticmethod
    def delete_old_table_and_populate(object engine, object TableClass, object UpdatedClass, object data_table, str table_name, object sess, bint silent,
                                      list ignore_fields=[]):
        print_if_not_silent(silent, " ..Deleting old table schema")
        TableClass.drop(engine)
        print_if_not_silent(silent, " ..Creating new table and filling with existing data")
        UpdatedClass.create(engine)
        records = UpdateManager.create_from_csv(data_table, {table_name: UpdatedClass}, ignore_fields)
        cdef object record
        for record in records[table_name]:
            sess.add(record)
        sess.commit()

    def _query_table(self, object DBClass):
        """ Queries single table in database based on class

        :param DBClass:
        :return: (Dict[str, List[db_objects]])      DB data
        """
        cdef list data = self.session.query(DBClass).all()
        # Return list of columns and dict with name of table as key and queried data as value
        try:
            return {self.cfg.table_name: [col for col in data[0].keys() if col != "_sa_instance_state"], }, \
                   {self.cfg.table_name: data, }
        except IndexError:
            return {self.cfg.table_name: self.class_as_dict.keys(), }, {
                self.cfg.table_name: data, }

    def _write_to_file(self, dict cols, dict data, str outfile_prefix):
        """ Protected method that writes or prints query data. Called when write_to_file or print_all is called.

        :param outfile_prefix: (str) Prefix to give stored data
        :param cols: columns output from cls.query_all(param)
        :param data: query_data output from cls.query_all(param)
        :return:
        """
        # Iterate over tables
        cdef str outfile_path = UpdateManager._check_migration_file_number(
            os.path.join(self.cfg.migrations_dir, outfile_prefix + UpdateManager.MGMT_EXT))
        cdef str table_name
        cdef object col_list
        cdef object record
        W = open(os.path.join(self.cfg.migrations_dir, outfile_path), "w")
        for table_name in data.keys():
            # List of columns in table
            col_list = cols[table_name]
            # Write name of table as first line
            W.write('"Record","' + table_name + '"' + "," + "\n")
            # Write comma-separated names of each column
            W.write(",".join(['"{}"'.format(col) for col in col_list]) + "\n")
            # Iterate over every entry
            for record in data[table_name]:
                # Write each entry by column
                # W.write(','.join(['"{}"'.format(entry[col]) for col in col_list]) + "\n")
                W.write(','.join([str(getattr(record, col)) for col in col_list]) + "\n")
                # W.write(','.join([str(ent) for ent in entry]) + "\n")
            W.write("\n")
        W.close()
        return W.name

    @staticmethod
    def _check_migration_file_number(str simple_migration_path):
        """ Protected method will determine the most recent migration and will write new copy

        :param simple_migration_path:   (str) template migration string as ########.migrations.mgt
        :return:
        """
        cdef str path_prefix
        cdef list possible_migrations
        if os.path.isfile(simple_migration_path):
            possible_migrations = sorted(glob.glob("%s*" % simple_migration_path.rstrip(UpdateManager.MGMT_EXT)))
            if len(possible_migrations) > 1:
                possible_migrations.pop(-1)
            if len(possible_migrations) == 1:
                path_prefix = os.path.basename(possible_migrations[0])
            else:
                path_prefix = os.path.basename(possible_migrations[-1])
            path_prefix = path_prefix.rstrip(UpdateManager.MGMT_EXT)
            # First rewrite:    #########.migrations.mgt
            if len(path_prefix) == 8:
                return path_prefix + ".001" + UpdateManager.MGMT_EXT
            # Second rewrite:   ########.###.migrations.mgt
            if len(path_prefix) == 12:
                path_prefix, current_version = path_prefix.split(".")
                return path_prefix + "." + "{:03d}".format(int(current_version) + 1) + UpdateManager.MGMT_EXT
        return simple_migration_path

    @staticmethod
    def _load_from_csv(str csv_file):
        """ Protected method to load csv data and dictionaries of columns and data

        :param csv_file:
        :return Tuple[Dict[str, List[str]], Dict[str, List[List[str]]]]:
        """
        cdef dict tables = {}
        cdef object _csv_file = open(csv_file, newline='')
        cdef object csv_reader = csv.reader(_csv_file, delimiter=",")
        cdef dict cols = {}
        cdef str dept
        # Load each table data into cols and tables variables
        for row in csv_reader:
            if row[0] == "Record":
                dept = row[1]
                tables[dept] = []
                row = next(csv_reader)
                cols[dept] = row
                row = next(csv_reader)
                while row != "\n" and row:
                    tables[dept].append(row)
                    row = next(csv_reader)
        return cols, tables

    @staticmethod
    def create_from_csv(object csv_file, dict tables, list ignore_fields):
        """ Create database objects using new schema.
        This is to be completed once all data has been backed up from the server

        :param ignore_fields:
        :param tables:
        :param csv_file:
        :return:
        """
        # Load data from .csv file
        cdef dict cols
        cdef dict csv_data
        cdef object db_object
        cdef int i
        cols, csv_data = UpdateManager._load_from_csv(csv_file)
        cdef dict db_objects = {}
        cdef str name
        cdef object Table
        for name, Table in tables.items():
            db_objects[name] = []
            # Create DB object using json data stored in file
            DBClass = type(name, (Record,), {})
            mapper(DBClass, Table)
            if name in csv_data.keys():
                # Skip certain fields
                # Useful for editing columns
                for entry in csv_data[name]:
                    db_object = DBClass()
                    for i in range(len(cols[name])):
                        if cols[name][i] not in ignore_fields:
                            setattr(db_object, cols[name][i], CountTable._try_return(entry[i]))
                    # Add to list of objects to commit
                    db_objects[name].append(db_object)
        return db_objects
