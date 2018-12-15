from Accessories.ops import read_until


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
        with open(file_name, "r") as R:
            # Save first line
            self.header = R.readline()
            for line in R:
                # ID is first item on line
                genome_id = read_until(line, "\t")
                contents_in_file[genome_id] = line.rstrip("\n")
        return contents_in_file

    def get_line(self, genome_id, endline=False):
        """ Returns line from count table based on genome id

		:param genome_id: (str)	ID of genome
		:return str:
		"""
        if endline:
            return self.file_contents[genome_id] + "\n"
        else:
            return self.file_contents[genome_id]

    def get_line_with_taxa(self, genome_id, taxa):
        """ Returns value in taxonomy created by gtdb-tk output for given genome id

		:param genome_id: (str)	ID of genome
		:param taxa:	(str)	Requested taxa (e.g. family, phylum, etc)
		:return str:
		"""
        content = self.file_contents[genome_id].split("\t")
        content[0] += "." + taxa
        return "\t".join(content)
