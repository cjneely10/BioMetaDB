import csv
import re


class CheckMResult:
    def __init__(self, _id, completeness, contamination, heterogeneity):
        """ Class for serializing the CheckM output file

		:param _id: (str)	genome id, typically the base of the filename
		:param completeness: (float)	CheckM completeness percent
		:param contamination: (float)	CheckM contamination percent
		:param heterogeneity: (float)	CheckM heterogeneity score
		"""
        self._id = _id
        self.completeness = float(completeness)
        self.contamination = float(contamination)
        self.heterogeneity = float(heterogeneity)

    def __eq__(self, other):
        return self._id == other._id

    @staticmethod
    def read_checkm_analysis(file_):
        """ Parse checkm qa output file

		:param file_: (str)	checkm output
		:return Dict[str, CheckMResult]:
		"""
        # Load checkm qa analysis output into csv
        checkm = list(csv.reader(open(file_, 'r')))
        # Gather rows and remove whitespace characters
        new = []
        for list_ in checkm:
            for string in list_:
                x = re.sub(' +', ' ', str(re.split(r'\t+', string.rstrip('\t'))))
                new.append(x)
        del new[0], new[1], new[(len(new) - 1)]
        # Parse row by removing brackets
        new_2 = []
        for list_ in new:
            x = list_.strip("['']")
            x_2 = x.split()
            new_2.append(x_2)
        del new_2[0]
        # Collect reads in Dict[str, CheckMResult]
        checkm_reads = {}
        for list_ in new_2:
            _id = list_[0].strip(".fna")
            completeness = float(list_[12])
            contamination = float(list_[13])
            heterogeneity = float(list_[14])
            checkm_reads[_id] = CheckMResult(_id, completeness, contamination, heterogeneity)
        return checkm_reads
