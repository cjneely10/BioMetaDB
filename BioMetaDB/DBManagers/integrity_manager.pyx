# cython: language_level=3
import os
import shutil
from sys import exit
from sqlalchemy.orm import mapper
from sqlalchemy import text
from BioMetaDB.Accessories.ops cimport to_cstring_array, free_cstring_array
from BioMetaDB.Models.models import BaseData
from BioMetaDB.Models.functions import Record
from BioMetaDB.Config.config_manager import ConfigKeys
from BioMetaDB.Config.directory_manager import Directories
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Exceptions.fix_exceptions import FixAssertString


def record_bad_location_none(**kwargs):
    """ Function will announce that no changes were made for the given record's file location

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id")
    return "No changes to location info for %s" % kwargs["_id"]

def record_bad_location_file(**kwargs):
    """ Function will handle issues in which a record in the database does not have a valid file

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id", "sess", "UserClass", "fix_data", "config", "table_name")
    try:
        shutil.copy(
            kwargs["fix_data"],
            os.path.join(kwargs["config"][ConfigKeys.DATABASES][ConfigKeys.db_dir], kwargs["table_name"])
        )
    except FileNotFoundError:
        return "Unable to set location for %s" % kwargs["_id"]
    except shutil.SameFileError:
        return "File in location"
    record = (kwargs["sess"]).query(kwargs["UserClass"]).filter(text("_id == '%s'" % kwargs["_id"])).first()
    setattr(record, "location", os.path.join(kwargs["config"][ConfigKeys.DATABASES][ConfigKeys.db_dir], kwargs["table_name"]))
    setattr(record, "_id", os.path.basename(kwargs['fix_data']))
    return "Info <location> set to %s for %s" % (kwargs["fix_data"], kwargs["_id"])

def file_bad_record_delete(**kwargs):
    """ Function will announce that the improperly located file was deleted

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id")
    if os.path.exists(kwargs["_id"]):
        os.remove(kwargs["_id"])
    return "File %s was deleted" % kwargs["_id"]

def file_bad_record_record(**kwargs):
    """ Function will use passed info in fix_data to assign _id to a given record in the table directory

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id", "sess", "UserClass", "fix_data")
    record = (kwargs["sess"]).query(kwargs["UserClass"]).filter(text("_id == '%s'" % kwargs["fix_data"])).first()
    setattr(record, "location", kwargs["_id"])
    return "Info <_id> set to %s for %s" % (kwargs["fix_data"], kwargs["_id"])

def record_bad_type_none(**kwargs):
    """ Function will make no changes to data_type of passed _id

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id")
    return "No changes to data_type info for %s" % kwargs["_id"]

def record_bad_type_set(**kwargs):
    """ Function will set the data_type variable for the given record to match the value passed
    in the .fix file

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id", "sess", "UserClass", "fix_data")
    record = (kwargs["sess"]).query(kwargs["UserClass"]).filter(text("_id == '%s'" % kwargs["_id"])).first()
    setattr(record, "data_type", kwargs["fix_data"])
    return "Info <data_type> set to %s for %s" % (kwargs["fix_data"], kwargs["_id"])

# def table_bad_table_delete(**kwargs):
#     return 1
#
# def table_bad_table_tsv(**kwargs):
#     return 1
#
#
# def table_bad_table_mgt(**kwargs):
#     return 1


def project_invalid_path_none(**kwargs):
    """ Function displays message that no changes were done to the invalid project path

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id")
    return "No changes to project location info for %s" % kwargs["_id"]


def project_invalid_path_path(**kwargs):
    """ Function will reset all directories stored in the config folder based on the
    working directory passed in the .fix file

    :param kwargs:
    :return:
    """
    assert_kwargs_loaded(kwargs, "_id", "config", "fix_data")
    assert os.path.exists(kwargs["fix_data"]), FixAssertString.BAD_PROJECT_DIR
    config = kwargs["config"]
    # Set new working_dir and remaining config directories
    config[ConfigKeys.DATABASES][ConfigKeys.working_dir] = kwargs["fix_data"]
    config[ConfigKeys.DATABASES][ConfigKeys.db_dir] = os.path.join(kwargs["fix_data"], "db")
    config[ConfigKeys.DATABASES][ConfigKeys.config_dir] = os.path.join(kwargs["fix_data"], "config")
    config[ConfigKeys.DATABASES][ConfigKeys.rel_work_dir] = os.path.basename(kwargs["fix_data"])
    config[ConfigKeys.DATABASES][ConfigKeys.migrations_dir] = os.path.join(kwargs["fix_data"], "migrations")
    config[ConfigKeys.DATABASES][ConfigKeys.rel_db_dir] = os.path.join(os.path.basename(kwargs["fix_data"]), "db")
    config[ConfigKeys.DATABASES][ConfigKeys.db_name] = os.path.basename(kwargs["fix_data"])
    with open(os.path.join(os.path.join(config[ConfigKeys.DATABASES][ConfigKeys.working_dir], Directories.CONFIG),
                           config[ConfigKeys.DATABASES][ConfigKeys.db_name] + ".ini"), "w") as W:
        config.write(W)
    return "Info <project location> set to %s for %s" % (kwargs["fix_data"], kwargs["_id"])


def assert_kwargs_loaded(dict kwargs_dict, *args):
    """ Check that needed kwargs were passed from calling function
    
    :param kwargs_dict: 
    :param args: 
    :return: 
    """
    cdef set needed_kwargs = set(args)
    cdef set passed_args = set(kwargs_dict.keys())
    cdef str arg
    for arg in needed_kwargs:
        assert arg in passed_args, FixAssertString.INTERNAL_BAD_KWARGS


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
        self.fix_file = FixFile(fix_file_name)
        self.issues_found = 0

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
        cdef str key
        cdef str value
        if not os.path.exists(self.config[ConfigKeys.DATABASES][ConfigKeys.working_dir]):
            self.fix_file.write_issue(
                self.config[ConfigKeys.DATABASES][ConfigKeys.db_name],
                "PROJECT",
                "INVALID_PATH",
                "NONE"
            )
            print("Error in locating path directory, canceling remaining checks - see .fix file\n")
            exit(1)
    #
    # def table_check(self):
    #     """ Method checks if config tables have directory and presence in sql tables
    #
    #     :return:
    #     """
    #     cdef set standard_config_keys = {
    #         ConfigKeys.DATABASES.lower(),
    #         ConfigKeys.TABLES_TO_DB.lower(),
    #         ConfigKeys.TABLES_TO_ALIAS.lower(),
    #         "default",
    #     }
    #     cdef str key
    #     cdef object value
    #     cdef object engine
    #     cdef object tables_in_db = MetaData(
    #         bind=BaseData.get_engine(
    #             self.config[ConfigKeys.DATABASES][ConfigKeys.db_dir],
    #             self.config[ConfigKeys.DATABASES][ConfigKeys.db_name] + ".db"
    #         ),
    #         reflect=True).tables
    #     for key, value in self.config.items():
    #         if key.lower() not in standard_config_keys and \
    #                 stringarray_contains(self.tables, to_cstring(key.lower())) == 0:
    #             # Check that config classes exist as directories
    #             if not os.path.exists(os.path.join(
    #                     self.config[ConfigKeys.DATABASES][ConfigKeys.working_dir],
    #                     "classes",
    #                     "%s.json" % key)):
    #                 self.fix_file.write_issue(key, "TABLE", "BAD_TABLE", "DELETE")
    #                 self.issues_found = 1
    #             # Check that config classes exist in database
    #             if not key.lower() in tables_in_db:
    #                 self.fix_file.write_issue(key, "TABLE", "BAD_TABLE", "DELETE")
    #                 self.issues_found = 1

    def initialize_fix_file(self):
        self.fix_file.initialize_file()

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
                self.fix_file.write_issue_with_location(
                    record._id, "RECORD", "BAD_TYPE", "NONE", table_name)
                self.issues_found = 1
            # File for record, as stored in db, does not exist
            if record_full_path is None or not os.path.exists(record_full_path):
                self.fix_file.write_issue_with_location(
                    record._id, "RECORD", "BAD_LOCATION", "NONE", table_name)
                self.issues_found = 1
        for _file in records_in_table_dir.difference(record_paths):
            # File is in db directory but not in database table
            self.fix_file.write_issue_with_location(
                _file, "FILE", "BAD_RECORD", "DELETE", table_name)
            self.issues_found = 1

    def parse_and_fix(self, bint silent):
        """ Reads .fix file and calls function for all valid issues

        :return:
        """
        self.fix_file.load_file()
        self.fix_file.read_issue()
        cdef list issues = self.fix_file.issues
        cdef int i
        cdef object return_val = ""
        cdef object sess = None, UserClass = None, engine = None, TableClass = None
        cdef str current_table_name
        engine = BaseData.get_engine(self.config[ConfigKeys.DATABASES][ConfigKeys.db_dir],
                                     self.config[ConfigKeys.DATABASES][ConfigKeys.db_name] + ".db")
        sess = BaseData.get_session_from_engine(engine)
        # Generate table class and name based on presence of alias
        # Issues are in format (_id, location, parsed_issue, fix_data)
        current_table_name = issues[0][1]
        if current_table_name != "NONE":
            TableClass = ClassManager.get_class_orm(current_table_name, engine)
            UserClass = type(current_table_name, (Record,), {})
            mapper(UserClass, TableClass)
        cdef set possible_functions = set(self.function_hash.keys())
        for i in range(self.fix_file.num_issues):
            # Only re-generate table information if needed
            current_table_name = issues[i][1]
            if current_table_name != "NONE" and issues[i][1] != current_table_name:
                current_table_name = issues[i][1]
                TableClass = ClassManager.get_class_orm(current_table_name, engine)
                UserClass = type(current_table_name, (Record,), {})
                mapper(UserClass, TableClass)
            # Clear info as needed
            elif issues[i][1] == "NONE":
                current_table_name = "NONE"
                TableClass = None
                UserClass = None
            # Run fixing function if valid
            if issues[i][2] in possible_functions:
                return_val = self.function_hash[issues[i][2]](_id=issues[i][0],
                                                              location=issues[i][1],
                                                              sess=sess,
                                                              UserClass=UserClass,
                                                              TableClass=TableClass,
                                                              config=self.config,
                                                              fix_data=issues[i][3],
                                                              engine=engine,
                                                              cfg=self.config,
                                                              silent=silent,
                                                              table_name=current_table_name)
            else:
                print("Invalid fix data passed for %s" % issues[i][0])
            # Print results of each fix
            if return_val and not silent:
                print(return_val, "\n")
        # Commit all changes to the database
        sess.commit()

    cdef dict _create_function_hash(self):
        cdef dict function_hash = {}
        function_hash["RECORD|BAD_LOCATION|NONE"] = record_bad_location_none
        function_hash["RECORD|BAD_LOCATION|FILE"] = record_bad_location_file
        function_hash["FILE|BAD_RECORD|DELETE"] = file_bad_record_delete
        function_hash["FILE|BAD_RECORD|RECORD"] = file_bad_record_record
        function_hash["RECORD|BAD_TYPE|NONE"] = record_bad_type_none
        function_hash["RECORD|BAD_TYPE|SET"] = record_bad_type_set
        # function_hash["TABLE|BAD_TABLE|DELETE"] = table_bad_table_delete
        # function_hash["TABLE|BAD_TABLE|TSV"] = table_bad_table_tsv
        # function_hash["TABLE|BAD_TABLE|MGT"] = table_bad_table_mgt
        function_hash["PROJECT|INVALID_PATH|NONE"] = project_invalid_path_none
        function_hash["PROJECT|INVALID_PATH|PATH"] = project_invalid_path_path
        return function_hash
