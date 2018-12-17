import random
import os
from random import randint
from string import ascii_letters
from Bio import SeqIO
from Accessories.ops import chunk
from Accessories.bio_ops import BioOps
from Accessories.ops import read_until
from Indexers.index_extensions import IndexExtensions
from Exceptions.get_exceptions import SequenceIdNotFoundError
from Exceptions.get_exceptions import ImproperFormatIndexFileError


class IndexMapper:
    def __init__(self, file_name):
        """

        :param file_name: (str)	Load data into dictionaries
        """
        if IndexExtensions.IDX_FILE not in file_name:
            file_name += IndexExtensions.IDX_FILE
        self.data_dict, self.inv_data_dict = IndexMapper._load_file(file_name)

    @staticmethod
    def is_indexed(file_name):
        """ Checks if index file exists

        :param file_name: (str) Name of file
        :return bool:
        """
        return os.path.isfile(os.path.join(file_name, IndexExtensions.IDX_FILE))

    @staticmethod
    def _load_file(file_name, CHUNK_SIZE=100000):
        """ Loads file data into two of dictionaries

        :param file_name: (str)	Name of file to map
        :return Tuple[Dict[str, str], Dict[str, str]]:
        """
        data_dict = {}
        inv_data_dict = {}
        with open(file_name, "rb") as R:
            # Load large files by chunks
            for lines in chunk(R, CHUNK_SIZE):
                for line in lines:
                    line = line.decode().rstrip("\r\n").split("\t")
                    if len(line) == 3:
                        data_dict[line[0]] = (line[1], int(line[2]))
                        inv_data_dict[line[1]] = (line[0], int(line[2]))
                    elif len(line == 2):
                        data_dict[line[0]] = (line[1],)
                        inv_data_dict[line[1]] = (line[0],)
                    else:
                        raise ImproperFormatIndexFileError
        return data_dict, inv_data_dict

    def get(self, key):
        """ Retrieve associated match based on either key or value

        :param key: (str)	Value to retrieve, can either be key or value
        :return str:
        """
        try:
            return self.data_dict[key][0]
        except KeyError:
            try:
                return self.inv_data_dict[key][0]
            except KeyError as e:
                raise SequenceIdNotFoundError(e)

    def get_line_num(self, key):
        """ Retrieve associated match for line number based on either key or value

        :param key: (str)	Value to retrieve, can either be key or value
        :return int:
        """
        assert len(self.data_dict[key]) == 2, "File does not store line numbers"
        try:
            return self.data_dict[key][1]
        except KeyError:
            try:
                return self.inv_data_dict[key][1]
            except KeyError as e:
                raise SequenceIdNotFoundError(e)


class IndexCreator:
    @staticmethod
    def create_from_file(file_name, CHUNK_SIZE=100000):
        """ Create shortened id index from list of genomes

        :param CHUNK_SIZE: (int)    Chunk size for fast reading
        :param file_name: (str)	    Name of file for which to create index
        """
        index = {}
        line_count = 0
        with open(file_name, "rb") as R:
            # Load large files by chunks
            for lines in chunk(R, CHUNK_SIZE):
                for line in lines:
                    line_count += 1
                    line = line.decode().rstrip("\r\n")
                    index[line] = (line_count, IndexCreator._line_edit(16))
        IndexCreator._write(file_name + IndexExtensions.IDX_FILE, index)

    @staticmethod
    def create_from_fastx(file_name, CHUNK_SIZE=100000):
        """ Create index of short names for a fastx file

        :param file_name: (str)	Name of fastx file
        :param CHUNK_SIZE: (int)    Chunk size for fast reading
        """
        line_count = 0
        # Read file by bytes
        index = {}
        with open(file_name, "rb") as R:
            # Load large files by chunks
            for lines in chunk(R, CHUNK_SIZE):
                for line in lines:
                    line = line.decode().rstrip("\r\n")
                    line_count += 1
                    if line.startswith(">") or line.startswith("@"):
                        index[read_until(line[1:], " ")] = (line_count, IndexCreator._line_edit(16))
        IndexCreator._write(file_name + IndexExtensions.IDX_FILE, index)

    @staticmethod
    def rewrite_ids_in_fastx(image_mapper, file_name, remove_description=True):
        """ Rename fastx ids using index file, write to new file

        :param remove_description: (bool)   Only write ids in new file
        :param image_mapper: (IndexMapper)	Mapped index file
        :param file_name: (str)	Name of fastx file
        """
        data_type = BioOps.get_type(file_name)
        records = BioOps.parse_large(file_name, data_type)
        for record in records:
            record.id = image_mapper.get(record.id)
            if remove_description:
                record.description = ""
        SeqIO.write(records, file_name + IndexExtensions.match[data_type], data_type)

    @staticmethod
    def _line_edit(new_length):
        """ Get shortened version of line

        :param new_length: (int)    Length of id to create
        :return str:
        """
        shortened_line = ""
        for i in range(new_length - 5):
            shortened_line += random.choice(ascii_letters)
        shortened_line += str(randint(10000, 99999))
        return shortened_line

    @staticmethod
    def _write(file_name, index_dict):
        """ Writes dictionary contents

        :param file_name: (str) Name of file to which to write
        :param index_dict: (Dict[str, str]) Dictionary with values
        :return:
        """
        W = open(file_name, "wb")
        for k, v in index_dict.items():
            to_write = "{}\t{}\t{}\n".format(k, v[1], v[0])
            W.write(to_write.encode())
        W.close()
