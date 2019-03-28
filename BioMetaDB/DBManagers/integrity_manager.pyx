import os
from libc.stdio cimport printf
from sqlalchemy import MetaData
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Accessories.ops cimport to_cstring
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Accessories.ops cimport to_cstring_array, free_cstring_array
from BioMetaDB.Accessories.ops cimport stringarray_contains


cdef int record_bad_file_delete(char* arg, void* sess, void* UserClass):
    return 1

cdef int record_bad_file_file(char* arg, void* sess, void* UserClass):
    return 1

cdef int file_bad_record_delete(char* arg, void* sess, void* UserClass):
    return 1

cdef int file_bad_record_record(char* arg, void* sess, void* UserClass):
    return 1

cdef int record_bad_type_none(char* arg, void* sess, void* UserClass):
    return 1

cdef int record_bad_type_set(char* arg, void* sess, void* UserClass):
    return 1

cdef int table_bad_table_delete(char* arg, void* sess, void* UserClass):
    return 1

cdef int table_bad_table_tsv(char* arg, void* sess, void* UserClass):
    return 1

cdef int table_bad_table_mgt(char* arg, void* sess, void* UserClass):
    return 1

cdef int project_invalid_path_none(char* arg, void* sess, void* UserClass):
    return 1

cdef int project_invalid_path_path(char* arg, void* sess, void* UserClass):
    return 1


cdef class IntegrityManager:
    def __init__(self, object config, str fix_file_name, list tables=["ALL",]):
        """ IntegrityManager will check project, table, and record-level inconsistencies
        within the project structure

        :param config:
        :param fix_file_name:
        :param tables:
        """
        self.config = config
        self.function_hash = self._create_function_hash()
        self.tables = to_cstring_array(tables)
        self.issues_found = 0
        self.fix_file = FixFile(to_cstring(fix_file_name))

    def __del__(self):
        """ Free all allocated memory

        :return:
        """
        free_cstring_array(self.tables)

    def initial_project_check(self):
        """ Initial check to ensure that the project path is properly set in the config file
        Exits program if failed
        
        :return: 
        """
        self.fix_file.initialize_file()
        cdef str key
        cdef str value
        if not os.path.exists(self.config[ConfigKeys.DATABASES][ConfigKeys.working_dir]):
            self.fix_file.write_issue(
                to_cstring(self.config[ConfigKeys.DATABASES][ConfigKeys.db_name]),
                "PROJECT",
                "INVALID_PATH",
                "DELETE"
            )
            printf("Error in locating path directory, canceling remaining checks - see %s\n", self.fix_file.file_name)
            exit(1)

    def table_check(self):
        """ Method checks if config tables have directory and presence in sql tables

        :return:
        """
        cdef set standard_config_keys = {
            ConfigKeys.DATABASES.lower(),
            ConfigKeys.TABLES_TO_DB.lower(),
            ConfigKeys.TABLES_TO_ALIAS.lower(),
            "default",
        }
        cdef str key
        cdef object value
        cdef object engine
        cdef object tables_in_db = MetaData(
            bind=BaseData.get_engine(
                self.config[ConfigKeys.DATABASES][ConfigKeys.db_dir],
                self.config[ConfigKeys.DATABASES][ConfigKeys.db_name] + ".db"
            ),
            reflect=True).tables
        for key, value in self.config.items():
            if key.lower() not in standard_config_keys and stringarray_contains(self.tables, to_cstring(key.lower())) == 0:
                # Check that config classes exist as directories
                if not os.path.exists(os.path.join(value[ConfigKeys.class_dir], "%s.json" % key)):
                    self.fix_file.write_issue(to_cstring(key), "TABLE", "BAD_TABLE", "DELETE")
                    self.issues_found = 1
                # Check that config classes exist in database
                if not key.lower() in tables_in_db:
                    self.fix_file.write_issue(to_cstring(key), "TABLE", "BAD_TABLE", "DELETE")
                    self.issues_found = 1

    def record_check(self, object sess, object UserClass, str table_name):
        """ Method will check consistency of each individual record

        :param table_name:
        :param sess:
        :param UserClass:
        :return:
        """
        cdef object record
        cdef list all_records = sess.query(UserClass).all()
        cdef set records_in_table_dir = set([os.path.basename(val) for val in os.listdir(
            os.path.join(self.config[ConfigKeys.DATABASES][ConfigKeys.db_dir],
                         table_name))])
        cdef str record_full_path
        cdef str _file
        cdef set record_paths = set()
        for record in all_records:
            record_full_path = record.full_path()
            if record_full_path is not None:
                record_paths.add(os.path.basename(record_full_path))
            # Data type of record is not known
            if record.data_type == "unknown":
                self.fix_file.write_issue(to_cstring(record._id), "RECORD", "BAD_TYPE", "NONE")
                self.issues_found = 1
            # File for record, as stored in db, does not exist
            elif record_full_path is None or not os.path.exists(record_full_path):
                self.fix_file.write_issue(to_cstring(record._id), "RECORD", "BAD_FILE", "DELETE")
                self.issues_found = 1
        for _file in records_in_table_dir.difference(record_paths):
            # File is in db directory but not in database table
            self.fix_file.write_issue(to_cstring(_file), "FILE", "BAD_RECORD", "DELETE")
            self.issues_found = 1

    cdef FunctionHash _create_function_hash(self):
        cdef FunctionHash function_hash = FunctionHash(11)
        function_hash.add_item("RECORD|BAD_FILE|DELETE", record_bad_file_delete)
        function_hash.add_item("RECORD|BAD_FILE|FILE", record_bad_file_file)
        function_hash.add_item("FILE|BAD_RECORD|DELETE", file_bad_record_delete)
        function_hash.add_item("FILE|BAD_RECORD|RECORD", file_bad_record_record)
        function_hash.add_item("RECORD|BAD_TYPE|NONE", record_bad_type_none)
        function_hash.add_item("RECORD|BAD_TYPE|SET", record_bad_type_set)
        function_hash.add_item("TABLE|BAD_TABLE|DELETE", table_bad_table_delete)
        function_hash.add_item("TABLE|BAD_TABLE|TSV", table_bad_table_tsv)
        function_hash.add_item("TABLE|BAD_TABLE|MGT", table_bad_table_mgt)
        function_hash.add_item("PROJECT|INVALID_PATH|NONE", project_invalid_path_none)
        function_hash.add_item("PROJECT|INVALID_PATH|PATH", project_invalid_path_path)
        return function_hash
