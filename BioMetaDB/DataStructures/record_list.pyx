import re
from math import sqrt
from string import punctuation
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from BioMetaDB.DBManagers.class_manager import ClassManager
from BioMetaDB.Exceptions.record_list_exceptions import ColumnNameNotFoundError

"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


cdef class RecordList:

    def __init__(self, db_session, table_class, cfg, bint compute_metadata=False, str query=None):
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
        if compute_metadata and query:
            self.query(query)
            self._summary, self.num_records = self._gather_metadata()
        elif query:
            self.query(query)

    def get_column_summary(self):
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
        summary_string += "\t\t{:>{longest_key}}\t{:<12s}\n\n".format("Table Name:", self.cfg.table_name, longest_key=longest_key)
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

    def summarize(self):
        """ Returns metadata for list of records queried in list

        :return:
        """
        cdef str summary_string
        cdef list sorted_keys
        cdef str key
        cdef int longest_key
        if self._summary is None:
            self._summary, self.num_records = self._gather_metadata()
        sorted_keys = sorted(self.columns())
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string = ("*" * (longest_key + 50)) + "\n"
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
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}...\n\n".format(
                    "Table Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    longest_key=longest_key)
            else:
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<25.30s}\n\n".format(
                    "Table Name:",
                    self.cfg.table_name,
                    "ID:",
                    self.results[0]._id,
                    longest_key=longest_key)
        # No records found
        else:
            summary_string += "\t{:>{longest_key}}".format("No records found", longest_key=longest_key)
            # Do not create summary info
            return summary_string
        # Metadata display column headers
        summary_string += "\t{:>{longest_key}}\t{:<12s}\t{:<10s}\n\n".format(
            "Column Name",
            "Average",
            "Std Dev",
            longest_key=longest_key
        )
        # Build summary string
        for key in sorted_keys:
            if type(self._summary[key]) == str:
                summary_string += "\t{:>{longest_key}}\n".format("Text entry", longest_key=longest_key)
            else:
                summary_string += "\t{:>{longest_key}}\t{:<12.3f}\t{:<12.3f}\n".format(
                    key,
                    self._summary[key][0],
                    self._summary[key][3],
                longest_key=longest_key)
        summary_string += ("-" * (longest_key + 50)) + "\n"
        return summary_string

    def _gather_metadata(self):
        """ Protected method to collect data, averages, and standard deviations

        :return:
        """
        cdef dict summary_data
        cdef int num_records
        cdef str column
        cdef list column_keys
        cdef object record
        summary_data = {}
        if self.results is None:
             self.results = self.query()
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
                        summary_data[column] = "s"
                else:
                    if type(getattr(record, column)) != str:
                        # Gather portion for average calculation
                        summary_data[column][0] += float(getattr(record, column) / num_records)
                        # Gather portion for running sum
                        summary_data[column][1] += float(getattr(record, column))
                        # Gather portion for running sq sum
                        summary_data[column][2] += float(getattr(record, column) ** 2)
        # Determine standard deviation values
        if num_records > 1:
            for record in self.results:
                for column in self.columns():
                    # print(summary_data[column][1], summary_data[column][2])
                    summary_data[column][3] = sqrt((summary_data[column][2] -
                                                    ((summary_data[column][1] ** 2) / num_records)) / (num_records - 1))
        return summary_data, num_records

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
            # Column name not founc
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
        cdef object r
        cdef set possible_columns
        cdef set cols_in_db = set(self.columns())
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
            db_cols = {col.replace(punct, ""): col for col in cols_in_db}
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
        elif type(item) == str:
            for record in self:
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
        return [record._id for record in self]

    def values(self):
        """ Returns list of records

        :return:
        """
        cdef object record
        return [record for record in self]

    def items(self):
        """ Returns tuple of (key, value) pairs

        :return:
        """
        cdef object record
        return [(record._id, record) for record in self]

    def save(self):
        """ Calls the session's commit function to store changes

        :return:
        """
        self.sess.commit()
