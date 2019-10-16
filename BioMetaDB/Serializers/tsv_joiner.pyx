# cython: language_level=3
import os
class TSVJoiner:
    def __init__(self, str tsv_file_path = "", list initial_data=[]):
        self.header = set()
        self.data = {}
        for val in initial_data:
            for k, v in val.items():
                self.data[k] = k
        if os.path.exists(tsv_file_path):
            self.read_tsv(tsv_file_path)

    def _join_header(self, list header):
        cdef str _h
        for _h in header:
            self.header.add(_h)

    def read_tsv(self, str tsv_file_path):
        assert os.path.exists(tsv_file_path), "%s does not exist" % tsv_file_path
        cdef object R = open(tsv_file_path, "r")
        header = next(R).rstrip("\r\n").split("\t")
        cdef int header_len = len(header)
        data = None
        cdef str _line
        self._join_header(header[1:])
        for _line in R:
            line = _line.rstrip("\r\n").split("\t")
            data = self.data.get(line[0], None)
            if data is None:
                self.data[line[0]] = {}
            for i in range(1,header_len):
                self.data[line[0]][header[i]] = line[i]
        R.close()

    def write_tsv(self, str out_tsv_path):
        W = open(out_tsv_path, "w")
        header_list = list(self.header)
        cdef str head
        cdef str _id
        _out = ""
        W.write("ID\t")
        for head in header_list:
            _out += head + "\t"
        W.write(_out[:-1] + "\n")
        for _id in self.data.keys():
            _out = _id + "\t"
            for head in header_list:
                _out += self.data[_id].get(head, "None") + "\t"
            W.write(_out[:-1] + "\n")
        W.close()
