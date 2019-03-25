from BioMetaDB.DBManagers.class_manager import ClassManager
from sqlalchemy import text
from math import sqrt

"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


class RecordList:
    def __init__(self, db_session, table_class, cfg, compute_metadata=False, query=None):
        """ Class for handling (mostly) user interfacing to inner classes

        :param db_session:
        :param table_class:
        :param compute_metadata:
        """
        self.sess = db_session
        self.TableClass = table_class
        self.cfg = cfg
        self._summary = None
        self._data = None
        self.num_records = 0
        self.results = None
        if compute_metadata and query:
            self.query(query)
            self._summary, self._data, self.num_records = self._gather_metadata()
        elif query:
            self.query(query)

    def get_columns(self):
        """ Wrapper for returning columns in class as simple dictionary Name: SQLType

        :return:
        """
        cdef str summary_string
        cdef list sorted_keys
        cdef str key
        cdef int longest_key
        sorted_keys = sorted(ClassManager.get_class_as_dict(self.cfg))
        longest_key = max([len(key) for key in sorted_keys])
        summary_string = ("*" * (longest_key + 30)) + "\n"
        summary_string += "\t\t{:>{longest_key}}\t{:<12s}\n\n".format("Table Name:", self.cfg.table_name, longest_key=longest_key)
        summary_string += "\t\t{:>{longest_key}s}\n\n".format("Column Name", longest_key=longest_key)
        for key in sorted_keys:
            summary_string += "\t\t{:>{longest_key}s}\n".format(key, longest_key=longest_key)
        summary_string += ("-" * (longest_key + 30) + "\n")
        return summary_string

    def columns(self):
        """ Returns dict of columns

        :return:
        """
        return ClassManager.get_class_as_dict(self.cfg)

    def summarize(self):
        """ Returns metadata for list of records queried in list

        :return:
        """
        cdef str summary_string
        cdef list sorted_keys
        cdef str key
        cdef int longest_key
        if self._summary is None or self._data is None:
            self._summary, self._data, self.num_records = self._gather_metadata()
        sorted_keys = sorted(self._summary.keys())
        longest_key = max([len(key) for key in sorted_keys])
        # Pretty formatting
        summary_string = ("*" * (longest_key + 50)) + "\n"
        summary_string += "\t{:>{longest_key}}\t{:<12s}\n\t{:>{longest_key}}\t{:<10d}\n\n".format(
            "Table Name:",
            self.cfg.table_name,
            "Number of Records:",
            self.num_records,
            longest_key=longest_key)
        summary_string += "\t{:>{longest_key}}\t{:<12s}\t{:<10s}\n\n".format(
            "Column Name",
            "Average",
            "Std Dev",
            longest_key=longest_key
        )
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
        cdef list records_in_table
        cdef int num_records
        cdef str column
        cdef list column_keys
        summary_data = {}
        records_in_table = self.results
        if records_in_table is None:
             records_in_table = self.sess.query(self.TableClass).all()
        num_records = len(records_in_table)
        column_keys = list(self.columns().keys())
        for record in records_in_table:
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
            for record in records_in_table:
                for column in self.columns().keys():
                    # print(summary_data[column][1], summary_data[column][2])
                    summary_data[column][3] = sqrt((summary_data[column][2] -
                                                    ((summary_data[column][1] ** 2) / num_records)) / (num_records - 1))
        return summary_data, records_in_table, num_records

    def query(self, *args):
        """ Wrapper function for querying database. Converts text argument to query statement

        :param args:
        :return:
        """
        if len(args) > 0:
            self.results = self.sess.query(self.TableClass).filter(text(*args)).all()
        else:
            self.results = self.sess.query(self.TableClass).all()
        self._clear_prior_metadata()

    def _clear_prior_metadata(self):
        self._summary, self._data, self.num_records = None, None, None
