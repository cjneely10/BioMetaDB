"""
Class holds extensions used by indexers
Carries dictionary for parsing indexed fasta files

"""


class IndexExtensions:
    IDX_FILE = ".imidx"
    IDX_FA_FILE = ".imfadx"
    IDX_FQ_FILE = ".imfqdx"
    IDX_TSV_FILE = ".imtbx"
    match = {
        IDX_FA_FILE:    "fasta",
        IDX_FQ_FILE:    "fastq",
        "fasta":        IDX_FA_FILE,
        "fastq":        IDX_FQ_FILE,
    }
