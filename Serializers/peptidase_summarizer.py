#!/usr/bin/env python3

import os
from collections import defaultdict
from Accessories.arg_parse import ArgParse
from Serializers.count_table import CountTable

"""
Script will condense the output from extracellular-assignments-EG.py
Output will be a list of genomes with the total count of each kind of protein found

"""

if __name__ == "__main__":
    args_list = [
        [["-n", "--non_redundant_file"],
         {"help": "List of non-redundant genome ids", "require": True}],
        [["-f", "--file_to_condense"],
         {"help": "Peptidase count table of proteins to summarize by genome", "require": True}],
    ]

    ap = ArgParse(args_list,
                  description="peptidase_summarizer\tSummarize a peptidase by-protein count-table by genome")

    # Get genome ids in order
    genome_ids = [line.decode().rstrip("\r\n") for line in open(ap.args.non_redundant_file, "rb")]
    # Load peptidase file and get all ids (which include proteins)
    serialized_peptidases = CountTable(ap.args.file_to_condense)
    serialized_peptidases_ids = set(serialized_peptidases.file_contents.keys())
    # Name of file (for naming output)
    pep_prefix_and_ext = os.path.basename(ap.args.file_to_condense)
    # defaultdict to gather data to combine
    combine_by = defaultdict(list)
    # Begin writing output file by writing headers
    summary_file = open("summary." + pep_prefix_and_ext, "w")
    summary_file.write(serialized_peptidases.get_header_line(endline=True))
    # Iterate over genomes
    for _id in genome_ids:
        # All KEGG output has header underscores removed
        adj_id = _id.replace("_", "")
        # Check if peptidase output id (containing proteins) begins with genome id
        for pep_id in serialized_peptidases_ids:
            if pep_id.startswith(adj_id):
                # Add to list of found proteins for a given genome
                combine_by[_id].append(pep_id)

    combined_by_id = defaultdict(list)
    for genome_id, gen_prot_ids in combine_by.items():
        data_for_genome_id = [
            0 for _ in range(
                max([len(serialized_peptidases.file_contents[key]) for key in serialized_peptidases.file_contents.keys()])
            )
        ]
        for gen_prot_id in gen_prot_ids:
            for i in range(len(data_for_genome_id)):
                data_for_genome_id[i] += serialized_peptidases.get_at(gen_prot_id, i)
        combined_by_id[genome_id] = [str(data) for data in data_for_genome_id]

    for genome_id, collected_data in combined_by_id.items():
        summary_file.write(genome_id + "\t" + "\t".join(collected_data) + "\n")

    summary_file.close()
