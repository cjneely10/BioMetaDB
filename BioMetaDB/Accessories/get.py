#!/usr/bin/env python3

import os
import re
from Bio import SeqIO
import itertools as it
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from collections import Counter
from BioMetaDB.Accessories.bio_ops import BioOps
from BioMetaDB.Accessories.ops import read_until
from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.Indexers.index_mapper import IndexMapper
from BioMetaDB.Indexers.index_mapper import IndexCreator
from BioMetaDB.Indexers.index_mapper import IndexExtensions
from BioMetaDB.Accessories.program_caller import ProgramCaller
from BioMetaDB.Exceptions.get_exceptions import SequenceIdNotFoundError
from BioMetaDB.Exceptions.get_exceptions import ImproperFormatIndexFileError

"""
Script handles file IO operations

"""


def get_seq_from_file(file_name, seq_id):
    """ Locate sequence by ID/description (regex supported) and save to file

    :param file_name: (str)	User-passed name of file
    :param seq_id: (str)	User-passed sequence id to get from file
    """
    file_type = BioOps.get_type(file_name)
    value_to_return = set()
    seq_num = None
    data = {}
    try:
        data = {record.id: record for record in BioOps.parse_large(file_name, file_type)}
        value_to_return = data[seq_id]
    # If value is not found in parsed file, try regex
    except KeyError:
        seq_num = 0
        possible_seqs = list(data.keys())
        possible_descriptions = {val.id: val.description for val in data.values()}
        is_found = False
        # Try each sequence to see if matches regex
        for seq in possible_seqs:
            found = re.search(seq_id, seq)
            if found:
                value_to_return.add(data[seq])
                is_found = True
                seq_num += 1
        # Also check description to see for regex matches
        for _id, desc in possible_descriptions.items():
            found = re.search(seq_id, desc)
            if found:
                value_to_return.add(data[_id])
                is_found = True
                seq_num += 1
        if not is_found:
            print("Could not locate %s in %s" % (seq_id, file_name))
            raise SequenceIdNotFoundError(seq_id)
    file_name = os.path.splitext(file_name)[0]
    # Write found sequence to file
    out_file = "{}.{}".format(seq_id, file_name)
    W = open(out_file, "w")
    SeqIO.write(value_to_return, out_file, file_type)
    W.close()
    if not seq_num:
        print(" Sequence {} copied from file {} to {}".format(seq_id, file_name, out_file))
    else:
        print("{} sequence(s) copied from file {} to {}".format(seq_num, file_name, out_file))


def get_seqs_from_file(file_name, number):
    """ Retrieve a number of sequences from a file

    :param file_name: (str)	Name of file to parse
    :param number: (str)	User-passed number, list or numbers, or range to get
    """
    indices_to_get = _translate_number_string_to_interval(number)
    to_return = []
    data_type = BioOps.get_type(file_name)
    data = BioOps.parse_large(file_name, data_type)
    # Build list of values to return based on user-passed indices (list, range, or value)
    for index in indices_to_get:
        to_return.append(data[index])
    # Write found sequence to file
    out_file = "selected.{}".format(file_name)
    W = open(out_file, "w")
    SeqIO.write(to_return, out_file, data_type)
    W.close()
    print(" {} sequences copied from file {} to {}".format(len(indices_to_get), file_name, out_file))


def _translate_number_string_to_interval(number):
    """ Parses user-passed string for indices to get.
    Supported:
        0-4		Returns indices [0,1,2,3,4]
        1,3,5	Returns indices [1,3,5]

    :param number: (str)	User-passed string for numbers to get
    :return List[int]:
    """
    # List of values to get
    if "," in number:
        number = number.split(",")
        number = [int(_n) for _n in number]
        return number
    # Range of values to get
    else:
        number = number.strip(" ").split("-")
        number = [int(num) for num in number]
        if len(number) == 2:
            number = [_n for _n in range(number[0], number[1] + 1)]
        return number


def get_by_directory(directory):
    """ Renames all files in directory based on filename

    :param directory: (str)		Name of directory with files to rename
    """
    # Correct passed data type based on extension
    # New directory name and create if not exists
    new_location = os.path.join(directory, "tmp")
    if not os.path.isdir(new_location):
        os.makedirs(new_location)
    # Get all files in user-passed directory
    for file in [f for f in os.listdir(directory) if os.path.isfile(f)]:
        # Split file name from extension, get name of old file
        data_type = BioOps.get_type(file)
        _file, ext = os.path.splitext(file)
        fullpath_old = os.path.join(directory, file)
        # Get all records in file
        records_in_file = BioOps.parse_large(fullpath_old, data_type)
        # Rename ids based on file name, add number to end to distinguish
        num = 0
        for record in records_in_file:
            record.id += "_" + _file + "_" + str(num)
            num += 1
        # Write renamed version of file to .tmp directory
        fullpath_new = os.path.join(new_location, _file + ext)
        with open(fullpath_new, "w") as O:
            SeqIO.write(records_in_file, O, data_type)


def get_by_file(file_name):
    """ Renames sequences in file based on file name

    :param file_name: (str)	Name of file to rename
    """
    # Location to write data
    new_location = file_name + ".tmp"
    # Parse data file
    data_type = BioOps.get_type(file_name)
    records_in_file = BioOps.parse_large(file_name, data_type)
    num = 0
    for record in records_in_file:
        # Rename sequence id based on file name and a number for uniqueness
        record.id = file_name + "_" + str(num)
        num += 1
    # Write sequences to new file
    with open(new_location, "w") as O:
        SeqIO.write(records_in_file, O, data_type)


def get_t_to_u(file_name):
    """ Converts thymine to uracil in line

    :param file_name: (str)	Name of fasta file to amend
    """
    data = []
    with open(file_name, "U") as A:
        for line in A:
            # Only change non-header lines
            if not line.startswith(">"):
                line = line.replace("T", "U")
                line = line.replace("t", "u")
            data.append(line)
    with open(file_name, "w") as W:
        for _dat in data:
            W.write(_dat)


def get_u_to_t(file_name):
    """ Converts uracil to thymine in line

    :param file_name: (str)	Name of fasta file to amend
    """
    data = []
    with open(file_name, "U") as A:
        for line in A:
            # Only change non-header lines
            if not line.startswith(">"):
                line = line.replace("U", "T")
                line = line.replace("u", "t")
            data.append(line)
    with open(file_name, "w") as W:
        for _dat in data:
            W.write(_dat)


def reverse_complement_file(file_name):
    """ Reverse complements fasta sequences in file

    :param file_name: (str)	Name of file
    """
    data_type = BioOps.get_type(file_name)
    records_in_file = BioOps.parse_large(file_name, data_type)
    for record in records_in_file:
        record.reverse_complement()
        record.id += ".revComp"
    SeqIO.write(records_in_file, "tmp." + file_name, data_type)


def remove_ambiguity_from_file(file_name):
    """ Removes N from data file in-line

    :param file_name: (str)	Name of file to edit
    """
    data = []
    data_type = BioOps.get_type(file_name)
    records_in_file = BioOps.parse_large(file_name, data_type)
    for record in records_in_file:
        # Build new sequence
        new_seq = ""
        for val in record.seq:
            # Skip ambiguous character
            if val.upper() not in ("R", "Y", "W", "S", "M", "K", "H", "B", "V", "D", "N"):
                new_seq += val
        # Try DNA sequence type first (more restrictive)
        try:
            record.seq = Seq(new_seq, IUPAC.unambiguous_dna)
        # Default to protein otherwise
        except:
            record.seq = Seq(new_seq, IUPAC.unambiguous_rna)
        data.append(record)
    SeqIO.write(data, file_name, data_type)


def summarize_file(file_name, view):
    """ Outputs character count summary of file

    :param view: (str)          User-passed view value
    :param file_name: (str)		Name of file for which to gather character data
    """
    # Corrected view name and data type
    data_type = BioOps.get_type(file_name)
    view = _view_corrector(view)
    # File to read
    record_metadata = {}
    num_records = 0
    R = open(file_name, "rb")
    # Collect file data
    data = []
    if data_type == "fasta":
        # Read in file by fasta header, removing newlines
        for key, group in it.groupby(R, lambda line: line.decode().startswith(">")):
            data.append([gr.decode().rstrip("\r\n").strip(">") for gr in list(group)])
        # Retain record number
        num_records = len(data) // 2
        # Collect metadata by record
        for i in range(0, len(data), 2):
            record_metadata[data[i][0]] = (Counter(data[i][0]), Counter("".join(data[i + 1])))
    elif data_type == "fastq":
        # Read in file by fastq header, removing newlines
        for key, group in it.groupby(R, lambda line: line.startswith("@")):
            data.append([gr.rstrip("\r\n").strip("@") for gr in list(group)])
        # Retain record number
        num_records = len(data) // 2
        # Collect metadata by record
        # Note indices based on presence on "+" in records
        for i in range(0, len(data), 2):
            plus_loc = data[i + 1].index("+")
            record_metadata[data[i][0]] = (Counter(data[i][0]), Counter("".join(data[i + 1][:plus_loc])),
                                           Counter("".join(data[i + 1][plus_loc + 1:])))
    R.close()
    # Output general summary
    _summary_all(num_records, file_name)
    # Output based on user-passed value
    if view == "s":
        _summary_short(record_metadata)
    elif view == "l":
        _summary_long(record_metadata)


def _view_corrector(view):
    """ Returns s or l depending on value passed by user

    :param view: (str)	User-passed view of summary
    :return str:
    """
    if view == "short" or view == "s" or view == "S":
        view = "s"
    elif view == "long" or view == "l" or view == "L":
        view = "l"
    else:
        print("Summary type not found, default to short")
        view = "s"
    return view


def _summary_all(num, file_name):
    """ Displays name of file and number of records

    :param num: (int)			Number of records found
    :param file_name:	(str)	Name of file
    """
    print("%s summary:" % file_name)
    print("Number of records: %i" % num)


def _summary_short(record_metadata):
    """ Short summary that highlighting all data

    :param record_metadata: (Dict[str, Tuple[Counter, Counter]])	Dict with file data
    """
    all_header_metadata = Counter("")
    all_sequence_metadata = Counter("")
    all_quality_metadata = Counter("")
    for met_tuple in record_metadata.values():
        all_header_metadata += met_tuple[0]
        all_sequence_metadata += met_tuple[1]
        if len(met_tuple) == 3:
            all_quality_metadata += met_tuple[2]
    print("Values found in headers:")
    for k, v in all_header_metadata.items():
        print("# %s: %i" % (k, v))
    print("Values found in sequences:")
    for k, v in all_sequence_metadata.items():
        print("# %s: %i" % (k, v))
    if len(all_quality_metadata.keys()) > 0:
        print("Values found in quality scores:")
        for k, v in all_sequence_metadata.items():
            print("# %s: %i" % (BioOps.calculate_phred([k])[0], v))


def _summary_long(record_metadata):
    """ Print summary that highlights each record's information

    :param record_metadata: (Dict[str, Tuple[Counter, Counter]])	Dict with file data
    """
    sorted_keys = sorted(record_metadata.keys())
    for _id in sorted_keys:
        met_tuple = record_metadata[_id]
        print("Id: %s" % _id)
        print("Values found in header:")
        for k, v in met_tuple[0].items():
            print("# %s: %i" % (k, v))
        print("Values found in sequences:")
        for k, v in met_tuple[1].items():
            print("# %s: %i" % (k, v))
        if len(met_tuple) == 3:
            print("Values found in quality scores:")
            for k, v in met_tuple[2].items():
                print("# %s: %i" % (BioOps.calculate_phred([k])[0], v))


def make_file_index(file_name):
    """ Create index of fastx file sequence ids

    :param file_name: (str)	Name of fasta file to index
    """
    # Use fasta file to create index matching short names with ids
    IndexCreator.create_from_fastx(file_name)


def make_list_index(file_name):
    """ Creates simple index using simple list

    :param file_name: (str) Name of file
    :return:
    """
    IndexCreator.create_from_file(file_name)


def make_dir_index(directory):
    """ Creates an index mapping for all files in a directory

    :param directory: (str) Name of directory
    :return:
    """
    IndexCreator.make_idx_for_directory_file_names(directory)


def rename_files_in_dir_using_index(directory):
    """ Renames all files in directory with index file

    :param directory:
    :return:
    """
    IndexCreator.rename_directory_contents_using_index(directory)


def make_fastx_indexed(file_name):
    """ Rename ids in fastx file based on index file

    :param file_name: (str)	Name of fastx file
    """
    # Load index file for user-passed file
    im = IndexMapper(file_name)
    # Write amended fastx file
    IndexCreator.rewrite_ids_in_fastx(im, file_name)


def make_tsv_indexed(file_name, index_file, comment, skip):
    """ Replace sequence ids (first column) in .tsv file with index file ids

    :param file_name: (str)		Path to .tsv file to index
    :param index_file: (str)			Path to index (.imidx) file
    :param comment:	(List[str])	List of comment delimiters to exclude in parsing
    :param skip: (str)			Number of lines at head to exclude in parsing
    """
    im = IndexMapper(index_file)
    # Collect data in list
    data = []
    # Gather comment identifiers
    comments = comment.split(",")
    with open(file_name, "rb") as R:
        # Skip user-determined header lines, store in list
        for i in range(int(skip)):
            data.append(R.readline().decode())
        for line in R:
            line = line.decode()
            # Store comments in data
            if line[0: max([len(_comment) for _comment in comments])] in comments:
                data.append(line)
            # Index remaining items based on file
            else:
                _id = read_until(line, "\t")
                # Replace with indexed value
                line = line.replace(_id, im.get(_id))
                # Store in data
                data.append(line)
    # Rewrite to file-name with extension for indexed file
    with open(file_name + IndexExtensions.IDX_TSV_FILE, "w") as W:
        for line in data:
            W.write(line)


if __name__ == '__main__':
    args_list = [
        [["program"],
         {"help": "Select program"}],
        [["-f", "--file_name"],
         {"help": "Data file for reading/editing"}],
        [["-x", "--index_file"],
         {"help": "Index file with complete and short ids"}],
        [["-d", "--directory"],
         {"help": "Name of directory"}],
        [["-i", "--seq_id"],
         {"help": "Sequence ID to grab (regex)"}],
        [["-v", "--view"],
         {"help": "See in (l)ong or (s)hort format"}],
        [["-n", "--number"],
         {"help": "Number of sequences, inclusive range (index 0), or comma-separated list"}],
        [["-s", "--skip"],
         {"help": "Number of lines for which to skip indexing operation (default 0)", "default": "0"}],
        [["-c", "--comment"],
         {"help": "Comma-separated comment values indicating lines to retain but not parse", "default": "#"}],
    ]
    programs = {
        "ID": get_seq_from_file,
        "NUM": get_seqs_from_file,
        "RDIR": get_by_directory,
        "RFILE": get_by_file,
        "TtoU": get_t_to_u,
        "UtoT": get_u_to_t,
        "REVCOMP": reverse_complement_file,
        "REMOVEAMB": remove_ambiguity_from_file,
        "SUMMARIZE": summarize_file,
        "MAKEIDX": make_file_index,
        "MAKEDIRIDX": make_dir_index,
        "MAKELISTIDX": make_list_index,
        "IDXTOFX": make_fastx_indexed,
        "IDXTOTSV": make_tsv_indexed,
        "IDXTODIR": rename_files_in_dir_using_index,
    }
    flags = {
        "ID": ("file_name", "seq_id"),
        "NUM": ("file_name", "number"),
        "RDIR": ("directory",),
        "RFILE": ("file_name",),
        "TtoU": ("file_name",),
        "UtoT": ("file_name",),
        "REVCOMP": ("file_name",),
        "REMOVEAMB": ("file_name",),
        "SUMMARIZE": ("file_name", "view"),
        "MAKEIDX": ("file_name",),
        "MAKEDIRIDX": ("directory",),
        "MAKELISTIDX": ("file_name",),
        "IDXTOFX": ("file_name",),
        "IDXTOTSV": ("file_name", "index_file", "comment", "skip"),
        "IDXTODIR": ("directory",)
    }
    errors = {
        FileNotFoundError: "Provided filename does not exist",
        SequenceIdNotFoundError: "Sequence ID not found in file",
        ValueError: "File type cannot be parsed by BioPython",
        IndexError: "Sequence number or range exceeds data in file",
        IOError: "File path does not exist",
        TypeError: "Incorrect sequence type in file",
        ImproperFormatIndexFileError: "File is not in .imidx format",
    }
    _help = {
        "ID": "Program for getting a sequence from a file regex-matching request",
        "NUM": "Program for getting a sequence from a file by number, range, or list",
        "RDIR": "Program for renaming entire directory contents based on filenames",
        "RFILE": "Program for renaming sequences in a file based on filename",
        "TtoU": "Program converts thymine bases to uracil in file",
        "UtoT": "Program converts uracil bases to thymine in file",
        "REVCOMP": "Program reverse-complements fasta records in file",
        "REMOVEAMB": "Program removes ambiguous letters from sequence",
        "SUMMARIZE": "Program creates simple summary of sequences in file",
        "MAKEIDX": "Program creates index of fastx file",
        "IDXTOFX": "Program converts fasta file to indexed version (or back!)",
        "IDXTOTSV": "Program converts tsv file to indexed version (or back!)",
        "IDXTODIR": "Program renames contents of directory using index values",
        "MAKEDIRIDX": "Create index for names of file in a directory",
        "MAKELISTIDX": "Create index for list file",
    }

    ap = ArgParse(args_list,
                  description=ArgParse.description_builder("get:\tProgram for basic biological file get operations.",
                                                           _help, flags))

    pc = ProgramCaller(programs=programs, flags=flags, errors=errors, _help=_help)

    pc.run(ap.args, debug=False)
