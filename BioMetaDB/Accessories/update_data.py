"""
Class for use by user - Build a DataTable and use this to update records and to write to a tsv

"""
import os


class Data:
    """ Data node for building objects with key:value attributes

    """
    def __init__(self, _id=""):
        self._id = _id

    def get(self):
        """ Returns a dictionary consisting of the item and its attributes

        :return:
        """
        return {self._id: {val: getattr(self, val) for val in self._get_current_cols()}}

    def delattr(self, attr):
        """ Removes column of info storage

        :param attr:
        :return:
        """
        current_cols = self._get_current_cols()
        for col in current_cols:
            if col == attr:
                delattr(self, col)
                return True
        return False

    def _get_current_cols(self):
        """ Returns a tuple of all of the current user-added attributes

        :return:
        """
        return tuple((c for c in vars(self) if not c.startswith("__") and c != '_id'))


class UpdateData:

    def __init__(self):
        self.tsv = ""
        self.num_records = 0
        self._header = set()
        self.data = [Data(),]

    def __repr__(self):
        """ Calls get function for string representation

        :return:
        """
        return str(self.get())

    def __delattr__(self, item):
        """ Builtin function support

        :param item:
        :return:
        """
        self.delcol(item)

    def add(self, _id):
        """ Method for adding a new id to the list. Automatically called when UpdateData is accessed for
        a non-existing id

        :param _id:
        :return:
        """
        if self.num_records == 0:
            self.data[0] = Data(_id=_id)
            self.num_records = 1
            return
        self.data.append(Data(_id=_id))
        self.num_records += 1

    def delcol(self, col_name):
        """ Removes tracked column from UpdateData structure tracking

        :param col_name:
        :return:
        """
        range_obj = range(0, len(self.data))
        success = False
        for i in range_obj:
            success = self.data[i].delattr(col_name)
        if not success:
            raise KeyError("Column name not found")

    def keys(self):
        """ Returns the ids of all Data objects stored in the UpdateData object

        :return:
        """
        for value in self.data:
            for val in value._get_current_cols():
                self._header.add(val)
        return self._header

    def get(self):
        """ Return list of dictionaries, each composed of a Data object

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
            # Return matching record
            for _item in self.data:
                if _item._id == item:
                    return _item
            # Not found, add to data
            self.add(item)
            # Get newest added value
            return self.data[-1]
        raise TypeError("Unable to determine type")

    def __delitem__(self, item):
        """ Delete item from list of stored data

        :param item:
        :return:
        """
        if type(item) == int:
            assert item < self.num_records, "Index must be less than length"
            del self.data[item]
        # Slice of indices
        elif type(item) == slice:
            for i in range(item.start, item.stop, item.step):
                del self.data[i]
        # ID stored
        elif type(item) == str:
            # Delete matching record
            range_obj = range(0, len(self.data))
            for i in range_obj:
                if self.data[i]._id == item:
                    del self.data[i]
                    return
            raise ValueError("Item id not found")
        raise TypeError("Unable to determine type")

    def to_file(self, file_name, delim="\t", na_rep="None"):
        """ Write entire results to tsv or csv file, filling in gaps as needed with na_rep

        :param file_name:
        :param na_rep:
        :param delim:
        :return:
        """
        # Store name of file
        self.tsv = UpdateData._handle_filename(file_name)
        W = open(self.tsv, "w")
        # Write tsv header
        header = list(self.keys())
        header_line = "ID\t"
        for head in header:
            header_line += head + "\t"
        W.write(header_line[:-1] + "\n")
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

    @staticmethod
    def _handle_filename(file_name):
        """ Protected method to handle loading ~ and .. in filenames

        :param file_name:
        :return:
        """
        if "~" in file_name:
            return os.path.relpath(os.path.expanduser(file_name))
        return os.path.relpath(file_name)

    @staticmethod
    def from_file(file_name, has_header=True, delim="\t", na_rep="None", skip_lines=0, n_threads=1, initial_data=None):
        """ Read in tsv/csv file into UpdateData object. Can add to existing object

        :param file_name:
        :param has_header:
        :param delim:
        :param na_rep:
        :param skip_lines:
        :param n_threads:
        :param initial_data:
        :return:
        """
        if initial_data is None:
            initial_data = UpdateData()
        assert type(initial_data) == UpdateData
        R = open(UpdateData._handle_filename(file_name), "r")
        for i in range(skip_lines):
            next(R)
        if has_header:
            header = next(R).rstrip("\r\n").split(delim)
        else:
            header = "Column"
        # Write data, filling in as needed
        for _line in R:
            line = _line.rstrip("\r\n").split(delim)
            line_len = len(line)
            for i in range(1, line_len):
                if line[i] == na_rep:
                    line[i] = None
                if has_header:
                    setattr(initial_data[line[0]], header[i], line[i])
                else:
                    setattr(initial_data[line[0]], header + str(i), line[i])
        return initial_data


if __name__ == '__main__':
    import sys

    assert len(sys.argv) == 4, "Usage: update_data.py <tsv-file> <load/write> <skip-lines>"

    if sys.argv[2] == "load":
        data = UpdateData.from_file(sys.argv[1], skip_lines=int(sys.argv[3]))
