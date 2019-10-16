# cython: language_level=3
"""
Class for use by user - Build a DataTable and use this to update records and to write to a tsv

"""
import os


class Data:
    def __init__(self, _id=""):
        self._id = _id

    def set(self, key, value):
        setattr(self, key, value)

    def get(self):
        return {val: getattr(self, val) for val in self._get_current_cols()}

    def _get_current_cols(self):
        return tuple((c for c in vars(self) if not c.startswith("__") and c != '_id'))


class UpdateData:

    def __init__(self):
        self.tsv = ""
        self.num_records = 0
        self._header = set()
        self.data = [Data(),]

    def add(self, _id):
        if self.num_records == 0:
            self.data[0] = Data(_id=_id)
            self.num_records = 1
            return
        self.data.append(Data(_id=_id))
        self.num_records += 1

    def keys(self):
        for value in self.data:
            for val in value._get_current_cols():
                self._header.add(val)
        return self._header

    def get(self):
        """ Return list of

        :return:
        """
        return [val.get() for val in self.data]

    def __getitem__(self, item):
        """ Allows class to be indexed and searched

        :param item:
        :return:
        """
        # Index of stored list
        if type(item) == int:
            assert item < self.num_records, "Index must be less than length"
            return self.data[item]
        # Slice of indices
        elif type(item) == slice:
            return tuple(self.data[i] for i in range(item.start, item.stop, item.step))
        # ID stored
        elif type(item) == str:
            # Check if not already stored and add if needed
            if item not in (_i._id for _i in self.data):
                self.add(item)
                # Get newest added value
                return self.data[-1]
            # Return matching record
            for _item in self.data:
                if _item._id == item:
                    return _item
        return None

    def to_file(self, file_name, delim="\t", na_rep="None"):
        """ Write entire results to tsv file, filling in gaps as needed with na_rep

        :param file_name:
        :param na_rep:
        :param delim:
        :return:
        """
        # Store name of file
        self.tsv = file_name
        W = open(file_name, "w")
        # Write tsv header
        W.write("ID")
        header = list(self.keys())
        for head in header:
            W.write("\t" + head)
        W.write("\n")
        # Write data, filling in as needed
        for data in self.data:
            W.write(data._id)
            for head in header:
                val = getattr(data, head, None)
                if val:
                    W.write(delim + str(val))
                else:
                    W.write(delim + na_rep)
            W.write("\n")
        W.close()

    def delete_file(self):
        """ Removes tsv file stored as object attribute

        :return:
        """
        if os.path.exists(self.tsv):
            os.remove(self.tsv)

    def __len__(self):
        """ Accessible through len()

        :return:
        """
        return self.num_records
