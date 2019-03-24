import os
from math import ceil
from BioMetaDB.Accessories.bio_ops import BioOps

"""
Script holds superclass from which all user-created classes will inherit

"""


class DBUserClass:

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
        first_vals = ["_id", "data_type", "location"]
        attrs = {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"
                 and key not in first_vals}
        return_string = ""
        for i in range(len(first_vals)):
            return_string += "%s:\t%s\n" % (first_vals[i], self.__dict__[first_vals[i]])
        return_string += "\n"
        sorted_keys = sorted(attrs.keys())
        num_rows = int(ceil(len(sorted_keys) / 3))
        # Organized printing, rows of 3
        for j in range(num_rows + 1):
            for i in range(3):
                if i + 3 * j < len(sorted_keys):
                    return_string += "{:40s}".format(
                            "%s: %s" % (sorted_keys[i + 3 * j], attrs[sorted_keys[i + 3 * j]]))
                    return_string += "\t"
                else:
                    break
            return_string += "\n"
        return return_string

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

    def print(self):
        """ Method calls print function on file contents

        """
        print(open(self.full_path(), "r").read())

    def get(self):
        """ Method for retrieving file contents

        :return str:
        """
        return open(self.full_path(), "r").read()

    def get_records(self):
        """ Method returns contents of record's file as a list of BioPython SeqRecord objects

        :return List[SeqRecord]
        """
        data_type = BioOps.get_type(self.full_path())
        # Parses large file if needed (chunk at 10000 lines)
        return BioOps.parse_large(self.full_path(), data_type)
