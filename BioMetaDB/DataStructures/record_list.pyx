# cython: language_level=3
import re
from math import sqrt
from sqlalchemy import text
from string import punctuation
from sqlalchemy.exc import OperationalError
from BioMetaDB.DBManagers.class_manager import ClassManager
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
        cdef str summary_string
        cdef list sorted_keys
        cdef str key
        cdef int longest_key
        sorted_keys = sorted(ClassManager.get_class_as_dict(self.cfg))
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string = ("*" * (longest_key + 30)) + "\n"
        summary_string += "\t\t{:>{longest_key}}\t{:<12s}\n\n".format("Record Name:", self.cfg.table_name, longest_key=longest_key)
        summary_string += "\t\t{:>{longest_key}s}\n\n".format("Column Name", longest_key=longest_key)
        # Get all columns
        for key in sorted_keys:
            summary_string += "\t\t{:>{longest_key}s}\n".format(key, longest_key=longest_key)
        summary_string += ("-" * (longest_key + 30) + "\n")
        return summary_string

    def columns(self):
        """ Returns dict of columns

        :return:
        """
        return ClassManager.get_class_as_dict(self.cfg).keys()

    def __str__(self):
        return self.summarize()

    def summarize(self):
        """ Returns metadata for list of records queried in list

        :return:
        """
        cdef str summary_string
        cdef list sorted_keys
        cdef str key, out_key
        cdef int longest_key
        if self._summary is None:
            self._summary, self.num_records, self.has_text = self._gather_metadata()
        sorted_keys = sorted(self.columns())
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string = ("*" * (longest_key + 60)) + "\n"
        # Display multiple records
        if self.num_records > 1:
            summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<10d}\n\n".format(
                "Table Name:",
                self.cfg.table_name,
                "Number of Records:",
                self.num_records,
                longest_key=longest_key)
        # Display single record
        elif self.num_records == 1:
            # Long name
            if len(self.results[0]._id) > 30:
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}...\n\t{:>{longest_key}}\t{:<12s}\n\n".format(
                    "Record Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    "Data Type:",
                    self.results[0].data_type,
                    longest_key=longest_key)
            else:
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}\n\t{:>{longest_key}}\t{:<12s}\n\n".format(
                    "Record Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    "Data Type:",
                    self.results[0].data_type,
                    longest_key=longest_key)
        # No records found
        else:
            summary_string += "\t{:>{longest_key}}".format("No records found", longest_key=longest_key)
            # Do not create summary info
            return summary_string
        # Metadata display column headers
        summary_string += "\t{:>{longest_key}}\t{:<20s}\t{:<12s}\n\n".format(
            "Column Name",
            "Average",
            "Std Dev",
            longest_key=longest_key
        )
        # Build summary string
        for key in sorted_keys:
            if type(self._summary[key]) == bool:
                summary_string += "\t{:>{longest_key}}\t{:<20s}\n".format(key, str(self._summary[key]), longest_key=longest_key)
            elif type(self._summary[key]) == list:
                summary_string += "\t{:>{longest_key}}\t{:<20.3f}\t{:<12.3f}\n".format(
                    key,
                    self._summary[key][0],
                    self._summary[key][3],
                longest_key=longest_key)
        summary_string += ("-" * (longest_key + 60)) + "\n"
        if self.has_text:
            summary_string += "\n\t{:>{longest_key}}\t{:<20s}\t{:<12s}\n\n".format(
                "Column Name",
                "Most Frequent",
                "Count Non-Null",
                longest_key=longest_key
            )
            for key in sorted_keys:
                if type(self._summary[key]) == dict:
                    out_key = max(self._summary[key].items(), key=lambda x : x[1])[0]
                    if len(out_key) > 16:
                        out_key = out_key[:17] + "..."
                    summary_string += "\t{:>{longest_key}}\t{:<20s}\t{:<12.0f}\n".format(key,
                                                                                         out_key,
                                                                                         self.num_records - self._summary[key].get("None", 0),
                                                                                         longest_key=longest_key)
            summary_string += ("-" * (longest_key + 60)) + "\n"
        return summary_string

    def _gather_metadata(self):
        """ Protected method to collect data, averages, and standard deviations

        :return:
        """
        cdef dict summary_data = {}, string_data = {}
        cdef int num_records, count
        cdef str column, val
        cdef list column_keys
        cdef object record
        cdef bint has_text = False
        if self.results is None:
             self.query()
        num_records = self.num_records
        column_keys = list(self.columns())
        for record in self.results:
            for column in column_keys:
                if column not in summary_data.keys():
                    if type(getattr(record, column)) != str:
                        summary_data[column] = []
                        # Gather portion for average calculation
                        summary_data[column].append(float(getattr(record, column)) / num_records)
                        # Gather portion for running sum
                        summary_data[column].append(float(getattr(record, column)))
                        # Gather portion for running sq sum
                        summary_data[column].append(float(getattr(record, column) ** 2))
                        summary_data[column].append(0.0)
                    else:
                        has_text = True
                        # Gather count
                        val = getattr(record, column)
                        summary_data[column] = {}
                        summary_data[column][(val if val != "" else "None")] = 0
                else:
                    if type(getattr(record, column)) != str:
                        # Gather portion for average calculation
                        summary_data[column][0] += float(getattr(record, column) / num_records)
                        # Gather portion for running sum
                        summary_data[column][1] += float(getattr(record, column))
                        # Gather portion for running sq sum
                        summary_data[column][2] += float(getattr(record, column) ** 2)
                    else:
                        # Gather count
                        val = getattr(record, column)
                        count = summary_data[column].get((val if val != "" else "None"), 0)
                        summary_data[column][(val if val != "" else "None")] = count + 1
        # Determine standard deviation values
        if num_records > 1:
            for column in self.columns():
                if type(summary_data[column]) != dict:
                # print(summary_data[column][1], summary_data[column][2])
                    try:
                        summary_data[column][3] = sqrt((summary_data[column][2] - ((summary_data[column][1] ** 2) / num_records)) / (num_records - 1))
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
        return self._regex_search(possible_column, list(self.columns()))

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

    def _regex_search(self, str possible_column, list search_list):
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
