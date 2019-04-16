import os
from BioMetaDB.Accessories.bio_ops import BioOps

"""
Script holds superclass from which all user-created classes will inherit

"""


class Record:

    def __init__(self):
        self._id = None
        self.location = None
        self.temp_filename = None

    def full_path(self):
        """ Method returns full path of bio storage location

        :return str:
        """
        file_path = None
        if os.path.isfile(self.location + "/" + self._id):
            file_path = self.location + "/" + self._id
        elif os.path.isfile(self.location + "/" + self._id + ".gz"):
            file_path = self.location + "/" + self._id + ".gz"
        return file_path

    def __repr__(self):
        """

        :return str:
        """
        # Print sorted attributes, excluding instance state object info
        first_vals = ("_id", "data_type", "location")
        first_cor_vals = ("ID", "Data Type", "File Location")
        attrs = {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"
                 and key not in first_vals and key != "id"}
        longest_key = max([len(key) for key in attrs])
        # Pretty formatting
        summary_string = ("*" * (longest_key + 30)) + "\n"
        for i in range(len(first_vals)):
            if len(self.__dict__[first_vals[i]]) > 50:
                summary_string += "\t{:>{longest_key}}\t{:<12.47s}...\n".format(
                    first_cor_vals[i],
                    self.__dict__[first_vals[i]],
                    longest_key=longest_key)
            else:
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n".format(
                    first_cor_vals[i],
                    self.__dict__[first_vals[i]],
                    longest_key=longest_key)
        summary_string += "\n\t{:>{longest_key}}\n\n".format(
            "Column Name",
            longest_key=longest_key
        )
        # Get all columns
        for key, val in attrs.items():
            if type(val) == str:
                summary_string += "\t{:>{longest_key}}\t{:<12s}\n".format(key, val, longest_key=longest_key)
            else:
                summary_string += "\t{:>{longest_key}}\t{:<12.3f}\n".format(
                    key,
                    val,
                    longest_key=longest_key)
        summary_string += ("-" * (longest_key + 30) + "\n")
        return summary_string

    def write(self):
        """ Method writes file contents to temporary file and stores file name as instance attribute

        """
        filename = self._id + ".tmp." + self.data_type
        W = open(filename, "w")
        with open(self.full_path(), "r") as R:
            W.write(R.read())
        W.close()
        self.temp_filename = filename

    def clear(self):
        """ Method for deleting instance temporary file

        """
        if self.temp_filename:
            os.remove(self.temp_filename)
            self.temp_filename = None

    def Print(self):
        """ Method calls print function on file contents

        """
        print(open(self.full_path(), "r").read())

    def get_records(self):
        """ Method returns contents of record's file as a list of BioPython SeqRecord objects

        :return List[SeqRecord]
        """
        data_type = BioOps.get_type(self.full_path())
        # Parses large file if needed (chunk at 10000 lines)
        return BioOps.parse_large(self.full_path(), data_type)