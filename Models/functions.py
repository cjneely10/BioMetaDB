import os
from Accessories.bio_ops import BioOps


def full_path(self):
    """ Method returns full path

    :return str:
    """
    return self.location + "/" + self._id + "." + self.data_type


def write(self):
    """ Method writes file contents to temporary file and stores file name in object

    """
    filename = self._id + ".tmp." + self.data_type
    W = open(filename, "w")
    with open(self.full_path(), "r") as R:
        W.write(R.read())
    W.close()
    self.temp_filename = filename


def clear(self):
    """ Method for deleting temporary file

    """
    if self.temp_filename:
        os.remove(self.temp_filename)
        self.temp_filename = None


def print(self):
    """ Method for printing file contents to screen

    """
    with open(self.full_path(), "r") as R:
        print(R.read())


def get(self):
    """ Method for retrieving file contents

    :return str:
    """
    file_contents = ""
    with open(self.full_path(), "r") as R:
        file_contents += R.read()
    return file_contents


def get_records(self):
    """ Method returns contents of record's file as a list of SeqRecord objects

    :return List[SeqRecord]
    """
    data_type = BioOps.get_type(self.full_path())
    return BioOps.parse_large(self.full_path(), data_type)


accessing_functions = {
    "full_path": full_path,
    "write": write,
    "clear": clear,
    "print": print,
    "get": get,
    "get_records": get_records,
}
