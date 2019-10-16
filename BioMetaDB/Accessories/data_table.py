# cython: language_level=3
"""
Class for use by user - Build a DataTable and use this to update records and to write to a tsv

"""


class Data:
    def __init__(self, _id=""):
        self._id = _id

    def set(self, key, value):
        setattr(self, key, value)

    def get(self):
        return {val: getattr(self, val) for val in self._get_current_cols()}

    def _get_current_cols(self):
        return tuple((c for c in vars(self) if not c.startswith("__") and c != '_id'))


class DataTable:

    def __init__(self):
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
        return [val.get() for val in self.data]

    def __getitem__(self, item):
        """ Allows class to be indexed and searched

        :param item:
        :return:
        """
        if type(item) == int:
            assert item < self.num_records, "Index must be less than length"
            return self.data[item]
        elif type(item) == slice:
            return tuple(self.data[i] for i in range(item.start, item.stop, item.step))
        elif type(item) == str:
            if item not in (_i._id for _i in self.data):
                self.add(item)
                return self.data[-1]
            for _item in self.data:
                if _item._id == item:
                    return _item
        return None

    def to_tsv(self, file_name):
        W = open(file_name, "w")
        W.write("ID")
        header = list(self.keys())
        for head in header:
            W.write("\t" + head)
        W.write("\n")
        for data in self.data:
            W.write(data._id)
            for head in header:
                val = getattr(data, head, None)
                if val:
                    W.write("\t" + str(val))
                else:
                    W.write("\t" + "None")
            W.write("\n")
        W.close()

    def __len__(self):
        """ Accessible through len()

        :return:
        """
        return self.num_records
