from BioMetaDB.DBManagers.class_manager import ClassManager
import operator
from sqlalchemy import text

"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


operator_dict = {
    ">":   operator.gt,
    "<=":   operator.le,
    ">=":   operator.ge,
    "<":   operator.lt,
    "==":   operator.eq,
}


class RecordList:
    def __init__(self, db_session, table_class, cfg, compute_metadata=True):
        """

        :param db_session:
        :param table_class:
        :param compute_metadata:
        """
        self.sess = db_session
        self.TableClass = table_class
        self.cfg = cfg
        self._summary = None
        self._data = None
        if compute_metadata:
            self._summary, self._data, self.num_records = self._gather_metadata()

    def get_columns(self):
        return ClassManager.get_class_as_dict(self.cfg)

    def get_summary(self):
        summary_string = "Table Name:\t\t%s\nNumber of Records:\t%s\n\n" \
                         % (self.cfg.table_name, self.num_records)
        if self._summary:
            sorted_keys = sorted(self._summary.keys())
            for key in sorted_keys:
                summary_string += "%s:  %s\n" % (key, self._summary[key])
        summary_string += "-----------------------------------------------------------\n"
        return summary_string

    def _gather_metadata(self):
        summary_data = {}
        records_in_table = self.sess.query(self.TableClass).all()
        num_records = len(records_in_table)
        for record in records_in_table:
            for column in self.get_columns():
                if column not in summary_data.keys():
                    if type(getattr(record, column)) != str:
                        summary_data[column] = getattr(record, column) / num_records
                    else:
                        summary_data[column] = "string"
                else:
                    if type(getattr(record, column)) != str:
                        summary_data[column] += (getattr(record, column) / num_records)

        return summary_data, records_in_table, num_records

    def query(self, *args):
        return self.sess.query(self.TableClass).filter(text(*args)).all()
