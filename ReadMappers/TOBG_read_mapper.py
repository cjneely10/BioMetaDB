#!/usr/bin/env python3.5

import os
import sys
import glob
import shutil
import subprocess
from collections import OrderedDict
from Accessories.ops import split_line_at
from Accessories.arg_parse import ArgParse

# Directory with reads
fastq_dir = "/media/eclipse/TaraReads"

if __name__ == "__main__":
    args_list = [
        [["-m", "--master_list"],
         {"help": "List of tara genomes/locations and their associated reads", "require": True}],
        [["-f", "--fasta_file"],
         {"help": "Fasta file with genomes to against which to map reads", "require": True}],
        [["-o", "--out_dir"],
         {"help": "Output directory for mapping. Note that prior runs can be continued is directory is existing",
          "require": True}],
        [["-r", "--rewrite"],
         {"help": "Rewrite output in existing directory, deleting existing files", "default": False}],
    ]

    ap = ArgParse(args_list, description="TOBG_read_mapper:\tMap TARA reads to fasta file")
    # Load initial reads from file
    reads_to_map = OrderedDict()
    with open(ap.args.master_list, "rb") as W:
        for line in W:
            line = line.decode().rstrip("\r\n")
            tara_id, read_file_prefixes = split_line_at(line, "\t")
            reads_to_map[tara_id] = read_file_prefixes
    # Store for easier access
    fasta_file = os.path.basename(ap.args.fasta_file)
    fasta_prefix = os.path.splitext(ap.args.fasta_file)[0]
    fasta_file_and_path = os.path.join(ap.args.out_dir, fasta_file)
    # All workflow items that will run
    possible_subprocesses = [
        ['bowtie2', '-q', '-1', "reads_1", '-2', "reads_2", '-S', "key" + ".sam", '-x',  # run bowtie
            fasta_prefix + ".bt_index", '--no-unal', '-p', '20'],
        ['sambamba', 'view', "-t", '20', '-S', "key" + '.sam', '-f', 'bam', '-o', "key" + '.bam'],  # convert sam to bam
        ['sambamba', 'sort', '-t', '20', "key" + '.bam', '-o', "key" + '.sorted.bam'],  # convert sam to sorted bam
        ['python2.7', '/usr/local/bin/bamm', 'filter', '-b', "key" + '.sorted.bam', '--percentage_id', '0.95',  # filter sorted bam of reads
            '--percentage_aln', '0.75']                                             # with high alignment stats
    ]
    # Populate all subprocesses for all files if outdir does not exist
    subprocesses_to_run = OrderedDict()
    # Remove existing directory if requested
    if ap.args.rewrite:
        shutil.rmtree(ap.args.out_dir)

    # Directory does not exist, create
    if not os.path.exists(ap.args.out_dir):
        # Make directory
        os.makedirs(ap.args.out_dir)
        # Copy fasta file to directory
        shutil.copy(ap.args.fasta_file, os.path.join(ap.args.out_dir, fasta_file))
        needs_index = True
    # Otherwise only run workflow items that are needed based on completed files in folder
    else:
        print("Populating data from %s" % ap.args.out_dir)
        # Check if bowtie2-index needs to run
        if len(glob.glob(os.path.join(ap.args.out_dir, "*.bt2"))) < 1:
            needs_index = True
            print("..Bowtie2 index not found")
        else:
            needs_index = False
            print("..Bowtie2 index exists")
    print("Gathering existing data")
    for tara_id in reads_to_map.keys():
        processes_to_run = []
        sys.stdout.write(("..%s" % tara_id).ljust(24) + "needs:\t".ljust(10))
        # Check if bowtie2 needs to be run
        if not os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".sam")) and not \
                os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".sorted_filtered.bam")):
            processes_to_run.append(possible_subprocesses[0])
            sys.stdout.write("bowtie2  ")
        # Check if sambamba view needs to run
        if not os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".bam")) and not \
                os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".sorted_filtered.bam")):
            processes_to_run.append(possible_subprocesses[1])
            sys.stdout.write("sambamba_view  ")
        # Check if sambamba sort needs to run
        if not os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".sorted.bam")):
            processes_to_run.append(possible_subprocesses[2])
            sys.stdout.write("sambamba_sort  ")
        # Check if BamM needs to run
        if not os.path.isfile(os.path.join(ap.args.out_dir, tara_id + ".sorted_filtered.bam")):
            processes_to_run.append(possible_subprocesses[3])
            sys.stdout.write("BamM")
        sys.stdout.write("\n")
        subprocesses_to_run[tara_id] = processes_to_run

    # Begin process by moving to output directory
    os.chdir(ap.args.out_dir)
    # Create bowtie2 index
    if needs_index:
        print("Building Bowtie2 index")
        subprocess.run(['bowtie2-build', fasta_file, fasta_prefix + ".bt_index"], check=True)
    # Run rest of workflow
    for tara_id, value in reads_to_map.items():
        value = value.split("\t")
        reads_1 = ""
        reads_2 = ""
        # Remove empty elements from list
        value = [val for val in value if val != ""]
        if len(value) > 1:
            for val in value:
                reads_1 += fastq_dir + "/" + val + "_1.fastq.gz,"
                reads_2 += fastq_dir + "/" + val + "_2.fastq.gz,"
            reads_1 = reads_1[:-1]
        else:
            reads_1 = fastq_dir + "/" + value[0] + "_1.fastq.gz"
            reads_2 = fastq_dir + "/" + value[0] + "_2.fastq.gz"

        # Replace parts of subprocess commands related to given key
        # Replace iteratively, based on number of processes remaining to run
        length_of_subprocess_list = len(subprocesses_to_run[tara_id])

        if length_of_subprocess_list == 4:
            subprocesses_to_run[tara_id][0][3] = reads_1
            subprocesses_to_run[tara_id][0][5] = reads_2
            subprocesses_to_run[tara_id][0][7] = tara_id + ".sam"

            subprocesses_to_run[tara_id][1][5] = tara_id + ".sam"
            subprocesses_to_run[tara_id][1][9] = tara_id + ".bam"

            subprocesses_to_run[tara_id][2][4] = tara_id + ".bam"
            subprocesses_to_run[tara_id][2][6] = tara_id + ".sorted.bam"

            subprocesses_to_run[tara_id][3][4] = tara_id + ".sorted.bam"
        elif length_of_subprocess_list == 3:
            subprocesses_to_run[tara_id][0][5] = tara_id + ".sam"
            subprocesses_to_run[tara_id][0][9] = tara_id + ".bam"

            subprocesses_to_run[tara_id][1][4] = tara_id + ".bam"
            subprocesses_to_run[tara_id][1][6] = tara_id + ".sorted.bam"

            subprocesses_to_run[tara_id][2][4] = tara_id + ".sorted.bam"
        elif length_of_subprocess_list == 2:
            subprocesses_to_run[tara_id][0][4] = tara_id + ".bam"
            subprocesses_to_run[tara_id][0][6] = tara_id + ".sorted.bam"

            subprocesses_to_run[tara_id][1][4] = tara_id + ".sorted.bam"
        elif length_of_subprocess_list == 1:
            subprocesses_to_run[tara_id][0][4] = tara_id + ".sorted.bam"

        # Call each process in order
        print("Calling processes for %s\n" % tara_id)
        for proc in subprocesses_to_run[tara_id]:
            print(" ".join(proc))
            subprocess.run(proc, check=True)

        # Remove intermediary files
        if os.path.isfile(tara_id + '.bam'):
            os.remove(tara_id + '.bam')
        if os.path.isfile(tara_id + '.sam'):
            os.remove(tara_id + '.sam')
