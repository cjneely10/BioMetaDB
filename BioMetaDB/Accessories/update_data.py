"""
Class for use by user - Build a DataTable and use this to update records and to write to a tsv

"""
import os


class Data:
    """ Data node for building objects with key:value attributes

    """
    def __init__(self, _id=""):
        self._id = _id
        self.data = {}

    def _get(self):
        """ Returns a dictionary consisting of the item and its attributes

        :return:
        """
        return self.data

    def get(self):
        return self._id, self.data

    def delattr(self, attr):
        """ Removes column of info storage

        :param attr:
        :return:
        """
        if attr in self.data.keys():
            del self.data[attr]
            return True
        return False

    def __getattr__(self, attr):
        """

        :return:
        """
        try:
            return self.data[attr]
        except KeyError:
            raise AttributeError

    def setattr(self, key, value):
        """ Function sets key, value pair for this object

        :param key:
        :param value:
        :return:
        """
        self.data[key] = value


class UpdateData:

    def __init__(self):
        self.tsv = ""
        self.num_records = 0
        self._header = set()
        self.data = [Data(), ]
        self._ids = {}

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
            self._ids[_id] = 0
            return
        self.data.append(Data(_id=_id))
        self.num_records += 1
        self._ids[_id] = self.num_records - 1

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
            for val in value.data.keys():
                self._header.add(val)
        return self._header

    def get(self):
        """ Return list of dictionaries, each composed of a Data object

        :return:
        """
        return [{val._id: val._get()} for val in self.data]

    def __getitem__(self, item):
        """ Allows class to be indexed and searched

        :param item:
        :return:
        """
        # Index of stored list
        # ID stored
        item_type = type(item)
        if item_type == str:
            # Return matching record
            _id = self._ids.get(item, None)
            if _id is not None:
                return self.data[_id]
            # Not found, add to data
            self.add(item)
            # Get newest added value
            return self.data[-1]
        elif item_type == int:
            assert item < self.num_records, "Index must be less than length"
            return self.data[item]
        # Slice of indices
        elif item_type == slice:
            if type(item.start) is None:
                item.start = 0
            if type(item.stop) is None:
                item.stop = -1
            if type(item.step) is None:
                item.start = 1
            return tuple(self.data[i] for i in range(item.start, item.stop, item.step))
        raise TypeError("Unable to determine type")

    def __add__(self, other):
        assert type(other) == UpdateData, "Must combine two UpdateData objects"
        for item in other.data:
            _id = self._ids.get(item, None)
            if _id is not None:
                for key, val in item._get().items():
                    self.data[_id].setattr(key, val)
            else:
                self.data.append(Data(_id=item._id))
                self.num_records += 1
                for key, val in item._get().items():
                    self.data[-1].setattr(key, val)
                self._ids[item._id] = self.num_records - 1
        return self

    def __delitem__(self, item):
        """ Delete item from list of stored data

        :param item:
        :return:
        """
        if type(item) == int:
            assert item < self.num_records, "Index must be less than length"
            del self.data[item]
            self.num_records -= 1
        # Slice of indices
        elif type(item) == slice:
            if type(item.start) is None:
                item.start = 0
            if type(item.stop) is None:
                item.stop = -1
            if type(item.step) is None:
                item.start = 1
            for i in range(item.start, item.stop, item.step):
                del self.data[i]
                self.num_records -= 1
        # ID stored
        elif type(item) == str:
            # Delete matching record
            _id = self._ids.get(item, None)
            if _id is not None:
                del self.data[_id]
                self.num_records -= 1
                return
            raise ValueError("Item id not found")
        raise TypeError("Unable to determine type")

    def to_file(self, file_name, delim="\t", na_rep="None", _order=None, skip_header=False):
        """ Write entire results to tsv or csv file, filling in gaps as needed with na_rep
        _order is list to follow to output header
        Option to skip header in output

        :param file_name:
        :param na_rep:
        :param delim:
        :param _order:
        :param skip_header:
        :return:
        """
        # Store name of file
        self.tsv = UpdateData._handle_filename(file_name)
        W = open(self.tsv, "w")
        # Write tsv header
        if _order is None:
            header = list(self.keys())
        else:
            header = list(_order)
        header_line = "ID\t"
        if not skip_header:
            for head in header:
                header_line += head + "\t"
            W.write(header_line[:-1] + "\n")
        # Write data, filling in as needed
        for data in self.data:
            W.write(data._id)
            for head in header:
                val = data.data.get(head, None)
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
    def from_file(file_name, has_header=True, delim="\t", na_rep="None", skip_lines=0, comment_delim="#"):
        """ Read in tsv/csv file into UpdateData object. Can add to existing object

        :param file_name:
        :param has_header:
        :param delim:
        :param na_rep:
        :param skip_lines:
        :param comment_delim:
        :param initial_data:
        :return:
        """
        initial_data = UpdateData()
        assert type(na_rep) == str, "Parameter `na_rep` must be of type str"
        assert skip_lines >= 0, "Number of initial lines to skip must be an integer greater than or equal to 0"
        R = open(UpdateData._handle_filename(file_name), "r")
        for i in range(skip_lines):
            next(R)
        if has_header:
            header = next(R).rstrip("\r\n").split(delim)
        else:
            header = "Column"
        # Write data, filling in as needed
        for _line in R:
            # Skip over comment lines, if provided
            if comment_delim is not None and _line.startswith(comment_delim):
                continue
            line = _line.rstrip("\r\n").split(delim)
            line_len = len(line)
            for i in range(1, line_len):
                if line[i] == na_rep:
                    line[i] = None
                if has_header:
                    initial_data[line[0]].setattr(header[i], line[i])
                else:
                    initial_data[line[0]].setattr(header + str(i), line[i])
        return initial_data
