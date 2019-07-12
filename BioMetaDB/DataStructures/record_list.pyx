# cython: language_level=3
import re
from math import sqrt
from io import StringIO
from sqlalchemy import text
from string import punctuation
from sqlalchemy.exc import OperationalError
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.DBManagers.type_mapper import TypeMapper
from BioMetaDB.Exceptions.record_list_exceptions import ColumnNameNotFoundError

"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


cdef class RecordList:

    def __init__(self, object db_session, object table_class, object cfg, bint compute_metadata=False, str query=None):
        """ Class for handling (mostly) user interfacing to inner classes

        :param db_session:
        :param table_class:
        :param compute_metadata:
        """
        self.sess = db_session
        self.TableClass = table_class
        self.cfg = cfg
        self._summary = None
        self.num_records = 0
        self.results = None
        self.has_text = False
        if compute_metadata and query:
            self.query(query)
            self._summary, self.num_records, self.has_text = self._gather_metadata()
        elif query:
            self.query(query)

    def columns_summary(self):
        """ Wrapper for returning columns in class as simple dictionary Name: SQLType

        :return:
        """
        cdef object summary_string = StringIO()
        cdef list sorted_keys
        cdef str key
        cdef int longest_key
        sorted_keys = sorted(ClassManager.get_class_as_dict(self.cfg).keys())
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string.write(("*" * (longest_key + 30)) + "\n")
        summary_string.write("\t\t{:>{longest_key}}\t{:<12s}\n\n".format("Record Name:", self.cfg.table_name,
                                                                         longest_key=longest_key))
        summary_string.write("\t\t{:>{longest_key}s}\n\n".format("Column Name", longest_key=longest_key))
        # Get all columns
        for key in sorted_keys:
            summary_string.write("\t\t{:>{longest_key}s}\n".format(key, longest_key=longest_key))
        summary_string.write(("-" * (longest_key + 30) + "\n"))
        return summary_string.getvalue()

    def columns(self):
        """ Returns dict of columns

        :return:
        """
        return ClassManager.get_class_as_dict(self.cfg).keys()

    def __str__(self):
        return self.summarize()

    def __repr__(self):
        return self.summarize()

    def summarize(self):
        """ Returns metadata for list of records queried in list

        :return:
        """
        cdef object summary_string = StringIO()
        cdef list sorted_keys
        cdef str key, out_key, _out_key
        cdef int longest_key, num_none
        cdef object val
        if self._summary is None:
            self._summary, self.num_records, self.has_text = self._gather_metadata()
        sorted_keys = sorted(self.columns())
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string.write(("*" * (longest_key + 75)) + "\n")
        # Display multiple records
        if self.num_records > 1:
            summary_string.write("\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<10d}\n\n".format(
                "Table Name:",
                self.cfg.table_name,
                "Number of Records:",
                self.num_records,
                longest_key=longest_key))
        # Display single record
        elif self.num_records == 1:
            # Long name
            if len(self.results[0]._id) > 30:
                summary_string.write("\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}...\n\t{:>{longest_key}}\t{:<12s}\n\n".format(
                    "Record Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    "Data Type:",
                    self.results[0].data_type,
                    longest_key=longest_key))
            else:
                summary_string.write("\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}\n\t{:>{longest_key}}\t{:<12s}\n\n".format(
                    "Record Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    "Data Type:",
                    self.results[0].data_type,
                    longest_key=longest_key))
        # No records found
        else:
            summary_string.write("\t{:>{longest_key}}".format("No records found", longest_key=longest_key))
            # Do not create summary info
            return summary_string.getvalue()
        # Metadata display column headers
        summary_string.write("\t{:>{longest_key}}\t{:<20s}\t{:<12s}\n\n".format(
            "Column Name",
            "Average",
            "Std Dev",
            longest_key=longest_key
        ))
        # Build summary string
        for key in sorted_keys:
            if key in self._summary.keys():
                if type(self._summary[key]) == list:
                    summary_string.write("\t{:>{longest_key}}\t{:<20.3f}\t{:<12.3f}\n".format(
                        key,
                        self._summary[key][0],
                        self._summary[key][3],
                    longest_key=longest_key))
        summary_string.write(("-" * (longest_key + 75)) + "\n")
        if self.has_text:
            longest_key = max([len(key) for key in sorted_keys if key in self._summary.keys() and type(self._summary[key]) == dict])
            summary_string.write("\n\t{:>{longest_key}}\t{:<20s}\t{:<10s}\t{:<12s}\n\n".format(
                "Column Name",
                "Most Frequent",
                "Frequency",
                "Total Count",
                longest_key=longest_key
            ))
            for key in sorted_keys:
                if key in self._summary.keys() and type(self._summary[key]) == dict:
                    num_none = self._summary[key].get("None", 0)
                    if num_none > 0:
                        del self._summary[key]["None"]
                    out_key = _out_key = max((self._summary[key].items() or {"111111111":0}.items()),
                                             key=lambda x : x[1])[0]
                    if out_key and len(out_key) > 16:
                        out_key = out_key[:17] + "..."
                    val = self._summary[key].get(_out_key, None)
                    summary_string.write("\t{:>{longest_key}}\t{:<20s}\t{:<10d}\t{:<12.0f}\n".format(
                        str(key), (out_key if self.num_records == 1 or (out_key != "111111111" and val != 1) else 'nil'),
                        (val if val and val != 1 else  1), self.num_records - num_none, longest_key=longest_key))
            summary_string.write(("-" * (longest_key + 75)) + "\n")
        return summary_string.getvalue()

    def _gather_metadata(self):
        """ Protected method to collect data, averages, and standard deviations

        :return:
        """
        cdef dict summary_data = {}, string_data = {}
        cdef int num_records, count
        cdef str column, val
        cdef list column_keys, vals
        cdef object record
        cdef bint has_text = False
        cdef object found_type, obj
        cdef dict data_types = {_k: TypeMapper.string_to_py_type[v]
                                for _k,v in ClassManager.get_class_as_dict(self.cfg).items()}
        if self.results is None:
             self.query()
        num_records = self.num_records
        column_keys = list(self.columns())
        for record in self.results:
            for column in column_keys:
                found_type = data_types[column]
                obj = getattr(record, column, None)
                if column not in summary_data.keys():
                    if obj is not None and obj != "None" and found_type in (int, float):
                        summary_data[column] = []
                        # Gather portion for average calculation
                        summary_data[column].append(float(float(obj) / num_records))
                        # Gather portion for running sum
                        summary_data[column].append(float(obj))
                        # Gather portion for running sq sum
                        summary_data[column].append(float(obj ** 2))
                        summary_data[column].append(0.0)
                    elif found_type in (str, bool):
                        has_text = True
                        # Gather count
                        val = str(getattr(record, column))
                        vals = RecordList._correct_value((val if val != '' else "None"))
                        summary_data[column] = {}
                        for _v in vals:
                            summary_data[column][_v] = 1
                else:
                    if obj is not None and obj != "None" and found_type in (int, float):
                        # Gather portion for average calculation
                        summary_data[column][0] += float(float(obj) / num_records)
                        # Gather portion for running sum
                        summary_data[column][1] += float(float(obj) / num_records)
                        # Gather portion for running sq sum
                        summary_data[column][2] += float(float(obj) ** 2)
                    elif found_type in (str, bool):
                        # Gather count
                        val = str(getattr(record, column))
                        vals = RecordList._correct_value((val if val != '' else "None"))
                        for _v in vals:
                            count = summary_data[column].get(_v, 0)
                            summary_data[column][_v] = count + 1
        # Determine standard deviation values
        if num_records > 1:
            for column in summary_data.keys():
                if type(summary_data[column]) != dict:
                # print(summary_data[column][1], summary_data[column][2])
                    try:
                        summary_data[column][3] = sqrt((summary_data[column][2] -
                                                        ((summary_data[column][1] ** 2) / num_records)) / (num_records - 1))
                    except ValueError:
                        summary_data[column][3] = -1
        return summary_data, num_records, has_text

    def query(self, *args):
        """ Wrapper function for querying database. Converts text argument to query statement

        :param args:
        :return:
        """
        self._clear_prior_metadata()
        # Query passed
        if len(args) > 0:
            # Attempt query
            try:
                self.results = self.sess.query(self.TableClass).filter(text(*args)).all()
            # Column name not found
            except OperationalError:
                raise ColumnNameNotFoundError
        # Default get all
        else:
            self.results = self.sess.query(self.TableClass).all()
        self.num_records = len(self.results)
        return self

    def join(self, RecordList other):
        """ Method will create view of final

        :param other:
        :return:
        """
        try:
            self.results = self.sess.query(self.TableClass).join(other.TableClass).all()
        # Column name not found
        except OperationalError:
            raise ColumnNameNotFoundError
        return self

    def _clear_prior_metadata(self):
        """ Protected member will clear existing data
        To be called with query()

        :return:
        """
        self._summary, self.num_records = None, 0

    def find_column(self, str possible_column):
        """ Searches available columns for user-passed value
        Will attempt to look for values that may result from punctuation changes

        :return:
        """
        return RecordList._regex_search(possible_column, list(self.columns()))

    def __next__(self):
        """ Returns self as iterator

        :return:
        """
        return self

    def __iter__(self):
        """ Iterator yields next value in self.results

        :return:
        """
        cdef int i
        for i in range(self.num_records):
            yield self.results[i]

    def __getitem__(self, item):
        """ Allows class to be indexed and searched

        :param item:
        :return:
        """
        cdef object record
        if type(item) == int:
            assert item < self.num_records, "Index must be less than length"
            return self.results[item]
        elif type(item) == slice:
            return self.results[item.start : item.stop : item.step]
        elif type(item) == str:
            for record in self.results:
                if record._id == item:
                    return record
        return None

    def __len__(self):
        """ Accessible through len()

        :return:
        """
        return self.num_records

    def keys(self):
        """ Returns list of ids

        :return:
        """
        cdef object record
        if self.results:
            return [record._id for record in self.results]
        return None

    def values(self):
        """ Returns list of records

        :return:
        """
        cdef object record
        return [record for record in self.results]

    def items(self):
        """ Returns tuple of (key, value) pairs

        :return:
        """
        cdef object record
        return [(record._id, record) for record in self.results]

    def save(self):
        """ Calls the session's commit function to store changes

        :return:
        """
        self.sess.commit()
        return self

    def write_records(self, str output_file):
        """ Method will write all records that are in the current db view to a user-provided
         output file

        :return:
        """
        cdef object R, W = open(output_file, "wb")
        cdef object record
        for record in self.results:
            R = open(record.full_path(), "rb")
            W.write(R.read())
            R.close()
        W.close()

    @staticmethod
    def _regex_search(str possible_column, list search_list):
        """ Protected method to search a list of values for a given string

        :param possible_column:
        :param search_list:
        :return:
        """
        cdef object r
        cdef set possible_columns
        cdef set cols_in_db = set(search_list)
        cdef dict db_cols = {col: col for col in cols_in_db}
        cdef set unusable_punctuation = set(punctuation) - set("_")
        cdef str punct
        cdef str tmp = possible_column
        r = re.compile(r"%s" % possible_column)
        # Exact matches
        possible_columns = set(filter(r.findall, cols_in_db))
        # Stored column name has punctuation, user value does not
        for punct in punctuation:
            db_cols = {col.replace(punct, ""): col for col in cols_in_db}
            possible_columns = possible_columns.union(set(db_cols[col] for col in filter(r.findall, db_cols.keys())))
            db_cols = {col.replace(punct, "_"): col for col in cols_in_db}
            possible_columns = possible_columns.union(set(db_cols[col] for col in filter(r.findall, db_cols.keys())))
        # User value has punctuation, stored column name does not
        for punct in unusable_punctuation:
            tmp = possible_column.replace(punct, "")
            r = re.compile(tmp)
            possible_columns = possible_columns.union(set(filter(r.findall, cols_in_db)))
            tmp = possible_column.replace(punct, "_")
            r = re.compile(tmp)
            possible_columns = possible_columns.union(set(filter(r.findall, cols_in_db)))
        # Return all possible values
        return list(possible_columns)

    @staticmethod
    def _correct_value(str value):
        """ Protected member function will split off annotation from %s-%s:%s paradigm

        :param value:
        :return:
        """
        cdef list return_list = [], vals
        cdef str val, _v
        if ";;;" in value:
            vals = [_v for _v in value.split(";;;") if _v != '']
            for val in vals:
                if ":::" in val:
                    _v = val.split(":::")[1]
                    if _v != '':
                        return_list.append(_v)
                else:
                    return_list.append(val)
            return return_list
        return [value,]
