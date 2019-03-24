from BioMetaDB.DBManagers.class_manager import ClassManager
from sqlalchemy import text

"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


class RecordList:
    def __init__(self, db_session, table_class, cfg, compute_metadata=False):
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
        if compute_metadata:
            self._summary, self._data, self.num_records = self._gather_metadata()

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
                if type(self._summary[key]) == int:
                    summary_string += "\t{:>20s}\t{:<12d}\n".format(
                        key,
                        self._summary[key])
                elif type(self._summary[key]) == float:
                    summary_string += "\t{:>20s}\t{:<12.3f}\n".format(
                        key,
                        self._summary[key])
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
        cdef float running_sum
        cdef float running_sq_sum
        running_sq_sum = 0.0
        running_sum = 0.0
        summary_data = {}
        records_in_table = self.sess.query(self.TableClass).all()
        num_records = len(records_in_table)
        for record in records_in_table:
            for column in self.get_columns().keys():
                if column not in summary_data.keys():
                    if type(getattr(record, column)) != str:
                        # Compute average
                        summary_data[column] = getattr(record, column) / num_records
                    else:
                        summary_data[column] = "string"
                else:
                    if type(getattr(record, column)) != str:
                        summary_data[column] += (getattr(record, column) / num_records)

        return summary_data, records_in_table, num_records

    def query(self, *args):
        """ Wrapper function for querying database. Converts text argument to query statement

        :param args:
        :return:
        """
        return self.sess.query(self.TableClass).filter(text(*args)).all()
