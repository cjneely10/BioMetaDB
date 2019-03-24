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
            self._summary, self._data, self.num_records = self._gather_metadata(query)
        elif query:
            self.results = self.query(query)

    def get_columns(self):
        """ Wrapper for returning columns in class as simple dictionary Name: SQLType

        :return:
        """
        return ClassManager.get_class_as_dict(self.cfg)

    def get_summary_string(self):
        """ Returns metadata for list of records queried in list

        :return:
        """
        cdef str summary_string
        cdef list sorted_keys
        cdef str key
        if self._summary is None or self._data is None:
            self._summary, self._data, self.num_records = self._gather_metadata()
        # Pretty formatting
        summary_string = "*******************************************************************\n"
        summary_string += "\t{:>20s}\t{:<12s}\n\t{:>20s}\t{:<10d}\n\n".format(
            "Table Name:",
            self.cfg.table_name,
            "Number of Records:",
            self.num_records)
        summary_string += "\t{:>20s}\t{:<12s}\t{:<10s}\n\n".format(
            "Column Name",
            "Average",
            "Std Dev"
        )
        if self._summary:
            sorted_keys = sorted(self._summary.keys())
            for key in sorted_keys:
                if type(self._summary[key]) == str:
                    summary_string += "\t{:>20s}\n".format("Text entry")
                else:
                    summary_string += "\t{:>20s}\t{:<12.3f}\t{:<12.3f}\n".format(
                        key,
                        self._summary[key][0],
                        self._summary[key][3])
        summary_string += "------------------------------------------------------------------\n"
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
        records_in_table = self.results or self.sess.query(self.TableClass).all()
        num_records = len(records_in_table)
        column_keys = list(self.get_columns().keys())
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
                        summary_data[column][0] += getattr(record, column) / num_records
                        # Gather portion for running sum
                        summary_data[column][1] += getattr(record, column)
                        # Gather portion for running sq sum
                        summary_data[column][2] += getattr(record, column) ** 2
        # Determine standard deviation values
        if num_records > 1:
            for record in records_in_table:
                for column in self.get_columns().keys():
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
        return self.results

    def _clear_prior_metadata(self):
        self._summary, self._data, self.num_records = None, None, None
