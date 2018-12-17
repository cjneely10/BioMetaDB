import os
from Bio import SeqIO
from Accessories.ops import chunk
from Indexers.index_extensions import IndexExtensions


class BioOps:
    @staticmethod
    def get_type(file_name):
        """ Method for parsing file extension to determine data type

        :param file_name: (str)	User-passed name of file
        """
        _, file_type = os.path.splitext(file_name)
        return BioOps._get_corrected_data_format(file_type.strip("."))

    @staticmethod
    def calculate_phred(scores):
        """ Determines phred quality scores based on presence of lowercase letters

        :param scores: (List[str])	List of nucleotide scores
        :return List[int]:
        """
        is_phred_33 = True
        for score in scores:
            if score.islower():
                is_phred_33 = False
                break
        if is_phred_33:
            return [ord(score) - 33 for score in scores]
        else:
            return [ord(score) - 64 for score in scores]

    @staticmethod
    def _get_corrected_data_format(dt):
        """ Protected method returns corrected data type to make it easier on user

        :param dt: (str)	Inferred data type based on file extension
        :return str:
        """
        avail_types = {
            "fasta": "fasta",
            "fastq": "fastq",
            "fna": "fasta",
            "faa": "fasta",
            "fa": "fasta",
            "fq": "fastq",
        }
        try:
            return avail_types[dt]
        except KeyError as e:
            try:
                return IndexExtensions.match("." + dt)
            except KeyError:
                print("Invalid data type: {}\nConfirm correct file extension".format(e))
                exit(1)

    @staticmethod
    def parse_large(file_name, data_type, batch_size=10000):
        """

        :param file_name:	(str)	Name of fasta or fastq file
        :param data_type:	(str)	Fasta or fastq
        :param batch_size:	(int)	Size of batch for reading in, default 10000
        """
        records = []
        # Create iterator
        record_iter = SeqIO.parse(open(file_name), data_type)
        # Read in by batch
        for batch in chunk(record_iter, batch_size):
            records += batch
        # Return complete records
        return records
