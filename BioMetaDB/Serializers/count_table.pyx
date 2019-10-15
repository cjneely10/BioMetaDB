# cython: language_level=3
cdef class CountTable:
    cdef public dict file_contents
    cdef public list header

    def __init__(self, str file_name):
        """ Class parses count tables from KEGG workflow

        :param file_name: (str)	count table output (from KEGG workflow)
        """
        self.file_contents = self._read_contents(file_name)

    def _read_contents(self, str file_name):
        """ Protected method to read file and return set of matches from file


        :param file_name: KEGG workflow output table
        :return Dict[str, namedtuple(Genome)]:
        """
        cdef dict contents_in_file = {}
        cdef list line
        cdef bytes _line
        with open(file_name, "rb") as R:
            # Save first line, removing empty tabs that may exist on header line
            self.header = [val for val in R.readline().decode().rstrip("\r\n").split("\t")[1:] if val != ""]
            for _line in R:
                # ID/key is first item on line
                line = _line.decode().rstrip("\r\n").split("\t")
                contents_in_file[line[0]] = line[1:]
        return contents_in_file

    def get_line(self, str genome_id, bint endline=False):
        """ Returns line from count table based on genome id

        :param genome_id: (str)	ID of genome
        :param endline: (bool)  Adds newline character
        :return str:
        """
        if endline:
            return "\t".join(self.file_contents[genome_id]) + "\n"
        else:
            return "\t".join(self.file_contents[genome_id])

    def get_header_line(self, bint endline=False, bint start_field=False):
        """ Returns header as string

        :param endline: (bool)  Add newline character
        :return str:
        """
        cdef str return_string = "\t".join(self.header)
        if endline:
            return_string += "\n"
        elif start_field:
            return_string = "ID\t" + return_string
        return return_string

    def get_at(self, str genome_id, int location):
        """ Returns value from count table based on genome id and location
        Note that, if header indices are [0,1,2,3,...],
        then the locations are gathered by [1,2,3,4,...] indices
        
        :param genome_id: (str) ID of genome
        :param location: (int)      Location in line (first column is location 0)
        :return str: 
        """
        return CountTable._try_return(self.file_contents[genome_id][location])

    def get_line_with_taxa(self, str genome_id, str taxa):
        """ Returns genome id with added string (typically taxonomy) appended

        :param genome_id: (str)	ID of genome
        :param taxa:	(str)	Requested taxa (e.g. family, phylum, etc)
        :return str:
        """
        cdef list content = self.file_contents[genome_id]
        content[0] += "." + taxa
        return "\t".join(content)

    @staticmethod
    def _try_return(object value):
        """ Attempts to parse value as integer and then as float. Simply returns if fails

        :param value: (str) Value from count table
        :return:
        """
        if value == "True":
            return True
        elif value == "False":
            return False
        elif value == 'None':
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                if value and value != '':
                    return value
                else:
                    return None

    @staticmethod
    def _try_return_type(object value):
        """ Attempts to parse value as integer and then as float. Simply returns if fails

        :param value: (str) Value from count table
        :return:
        """
        if value in ("True", "False"):
            return bool
        try:
            val = int(value)
            return int
        except ValueError:
            try:
                val = float(value)
                return float
            except ValueError:
                if value != '':
                    return str
                else:
                    return None


class TSVJoiner:
    def __init__(self, str tsv_file_path, dict initial_data={}):
        self.header = set()
        self.data = initial_data
        self.read_tsv(tsv_file_path)

    def _join_header(self, list header):
        cdef str _h
        for _h in header:
            self.header.add(_h)

    def read_tsv(self, str tsv_file_path):
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
