class CountTable:
    def __init__(self, file_name):
        """ Class parses count tables from KEGG workflow

        :param file_name: (str)	count table output (from KEGG workflow)
        """
        self.file_contents = self._read_contents(file_name)

    def _read_contents(self, file_name):
        """ Protected method to read file and return set of matches from file


        :param file_name: KEGG workflow output table
        :return Dict[str, namedtuple(Genome)]:
        """
        contents_in_file = {}
        with open(file_name, "rb") as R:
            # Save first line, removing empty tabs that may exist on header line
            self.header = [val for val in R.readline().decode().rstrip("\r\n").split("\t")[1:] if val != ""]
            for line in R:
                # ID/key is first item on line
                line = line.decode().rstrip("\r\n").split("\t")
                contents_in_file[line[0]] = line[1:]
        return contents_in_file

    def get_line(self, genome_id, endline=False):
        """ Returns line from count table based on genome id

        :param genome_id: (str)	ID of genome
        :param endline: (bool)  Adds newline character
        :return str:
        """
        if endline:
            return "\t".join(self.file_contents[genome_id]) + "\n"
        else:
            return "\t".join(self.file_contents[genome_id])

    def get_header_line(self, endline=False, start_field=False):
        """ Returns header as string

        :param endline: (bool)  Add newline character
        :return str:
        """
        return_string = "\t".join(self.header)
        if endline:
            return_string += "\n"
        elif start_field:
            return_string = "ID\t" + return_string
        return return_string

    def get_at(self, genome_id, location):
        """ Returns value from count table based on genome id and location
        Note that, if header indices are [0,1,2,3,...],
        then the locations are gathered by [1,2,3,4,...] indices
        
        :param genome_id: (str) ID of genome
        :param location: (int)      Location in line (first column is location 0)
        :return str: 
        """
        return CountTable._try_return(self.file_contents[genome_id][location])

    def get_line_with_taxa(self, genome_id, taxa):
        """ Returns genome id with added string (typically taxonomy) appended

        :param genome_id: (str)	ID of genome
        :param taxa:	(str)	Requested taxa (e.g. family, phylum, etc)
        :return str:
        """
        content = self.file_contents[genome_id]
        content[0] += "." + taxa
        return "\t".join(content)

    @staticmethod
    def _try_return(value):
        """ Attempts to parse value as integer and then as float. Simply returns if fails

        :param value: (str) Value from count table
        :return:
        """
        if value == "True":
            return True
        elif value == "False":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                if value != '':
                    return value
                else:
                    return "None"
