from collections import namedtuple

# Serialized metadata
Genome = namedtuple('Genome', ['domain', 'phylum', 'clss', 'order',
                               'family', 'genus', 'species'])


class GTDBtkParser:
    def __init__(self, file_name):
        """ Class parses gtdbtk output into dictionary

        :param file_name: (str)	gtdbtk output file
        """
        self.file_contents = GTDBtkParser._read_contents(file_name)

    @staticmethod
    def _read_contents(file_name):
        """ Protected method to read file and return set of matches from file


        :param file_name: Redundancy checker results
        :return Dict[str, namedtuple(Genome)]:
        """
        contents_in_file = {}
        with open(file_name, "rb") as R:
            # Skip first line
            next(R)
            for line in R:
                line = line.decode()
                # Remove newline character and split by tab
                line = line.rstrip("\r\n").split("\t")
                # ID is first item on line
                genome_id = line[0]
                taxonomy = line[1].strip("\t").split(";")
                taxonomy = [_t.split("__")[1] for _t in taxonomy]
                contents_in_file[genome_id] = Genome._make(taxonomy)
        return contents_in_file

    def get_taxa(self, genome_id, taxa):
        """ Returns value in taxonomy created by gtdb-tk output

        :param genome_id: (str)	ID of genome
        :param taxa:	(str)	Requested taxa (e.g. family, phylum, etc)
        :return str:
        """
        return self.file_contents[genome_id]._asdict()[taxa]

    def get_all_taxa(self, genome_id):
        """ Returns value in taxonomy created by gtdb-tk output

        :param genome_id: (str)	ID of genome
        :param taxa:	(str)	Requested taxa (e.g. family, phylum, etc)
        :return str:
        """
        return ";".join(self.file_contents[genome_id]._asdict().values())
