import os
import random
import shutil
from Bio import SeqIO
from random import randint
from string import ascii_letters
from BioMetaDB.Accessories.ops import chunk
from BioMetaDB.Accessories.bio_ops import BioOps
from BioMetaDB.Accessories.ops import read_until
from BioMetaDB.Indexers.index_extensions import IndexExtensions
from BioMetaDB.Exceptions.get_exceptions import SequenceIdNotFoundError
from BioMetaDB.Exceptions.get_exceptions import ImproperFormatIndexFileError


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
                        data_dict[line[0]] = (line[2], int(line[1]))
                        inv_data_dict[line[2]] = (line[0], int(line[1]))
                    elif len(line) == 2:
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
    def make_idx_for_directory_file_names(directory_name):
        """ Make index file for filenames in a directory

        :param directory_name: (str)    Name of directory with files to rename
        :return:
        """
        current_dir = os.getcwd()
        W = open(os.path.join(current_dir, os.path.dirname(directory_name) + IndexExtensions.IDX_FILE), "wb")
        files_in_directory = set(file for file in os.listdir(directory_name))
        for _file in files_in_directory:
            data_type = BioOps.get_type(_file)
            W.write(("%s\t%s\n" % (_file, IndexCreator._line_edit(16) + "." + data_type)).encode())
        W.close()

    @staticmethod
    def create_from_file(file_name, CHUNK_SIZE=100000):
        """ Create shortened id index from list of genomes

        :param CHUNK_SIZE: (int)    Chunk size for fast reading
        :param file_name: (str)	    Name of file for which to create index
        """
        line_count = 0
        W = open(file_name + IndexExtensions.IDX_FILE, "wb")
        with open(file_name, "rb") as R:
            # Load large files by chunks
            for lines in chunk(R, CHUNK_SIZE):
                for line in lines:
                    line_count += 1
                    line = line.decode().rstrip("\r\n")
                    W.write(("%s\t%s\t%s\n" % (line, str(line_count), IndexCreator._line_edit(16))).encode())
        W.close()

    @staticmethod
    def create_from_fastx(file_name, CHUNK_SIZE=100000):
        """ Create index of short names for a fastx file

        :param file_name: (str)	Name of fastx file
        :param CHUNK_SIZE: (int)    Chunk size for fast reading
        """
        line_count = 0
        # Read file by bytes
        W = open(file_name + IndexExtensions.IDX_FILE, "wb")
        with open(file_name, "rb") as R:
            # Load large files by chunks
            for lines in chunk(R, CHUNK_SIZE):
                for line in lines:
                    line = line.decode().rstrip("\r\n")
                    line_count += 1
                    if line.startswith(">") or line.startswith("@"):
                        W.write(("%s\t%s\t%s\n" % (
                            read_until(line[1:], " "), str(line_count), IndexCreator._line_edit(16)
                        )).encode())
        W.close()

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
    def rename_directory_contents_using_index(directory):
        """ Uses index file to rename all files in a folder
        Note that index file name must match directory name

        :param directory: (str) Directory with files to rename
        :return:
        """
        im = IndexMapper(directory)
        for _file in os.listdir(directory):
            try:
                shutil.move(os.path.join(directory, _file), os.path.join(directory, im.get(_file)))
            except SequenceIdNotFoundError:
                print("Could not move %s" % _file)

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
