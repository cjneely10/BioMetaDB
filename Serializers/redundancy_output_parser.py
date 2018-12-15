from collections import namedtuple

# Serialized metadata
Match = namedtuple('Match', ['match_id', 'completeness', 'contamination'])


class RedundancyParser:
    def __init__(self, file_name):
        """ Class parses redundancy_checker.__main__ output into dictionary

		File is in format:
			Best_Match:Completeness,Contamination\t[Next_Match:Completeness,Contamination\t]

		:param file_name: (str)	Redundancy checker results
		"""
        self.file_contents = RedundancyParser._read_contents(file_name)

    @staticmethod
    def _read_contents(file_name):
        """ Protected method to read file and return set of matches from file

		File is in format:
			Best_Match:Completeness,Contamination\t[Next_Match:Completeness,Contamination\t]

		:param file_name: Redundancy checker results
		"""
        contents_in_file = []
        with open(file_name, "r") as R:
            # Skip first line
            next(R)
            for line in R:
                matches = []
                # Remove newline character and split by tab
                line = line.rstrip("\r\n").split("\t")
                # Iterate over all entries on line
                for _m in line:
                    # Split based on format in __init__ docstring
                    match = _m.strip("\t").split(":")
                    match_data = match[1].split(",")
                    matches.append(Match._make([match[0], match_data[0], match_data[1]]))
                contents_in_file.append((matches, matches[0]))
        return contents_in_file

    def get_match(self, genome_id):
        for match_set, best_match in self.file_contents:
            if genome_id in [match.match_id for match in match_set]:
                return best_match
