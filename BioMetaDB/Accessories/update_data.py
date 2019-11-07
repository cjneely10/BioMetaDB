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
        return {val: getattr(self, val) for val in self._get_current_cols()}

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