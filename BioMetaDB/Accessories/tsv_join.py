#!/usr/bin/env python3

from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.Serializers.count_table import CountTable
from BioMetaDB.Serializers.checkm_result import CheckMResult
from BioMetaDB.Serializers.gtdbtk_output_parser import GTDBtkParser


if __name__ == "__main__":
    args_list = [
        [["-g", "--gtdbtk_output"],
         {"help": "GTDB-tk output summary file", "require": True}],
        [["-c", "--checkm_output"],
         {"help": "CheckM summary output", "require": True}],
        [["-k", "--kegg_file"],
         {"help": "KEGG-decoder.py output", "require": True}],
        [["-m1", "--hmm_file"],
         {"help": "KEGG-expander.py output", "require": True}],
        [["-m2", "--merops_file"],
         {"help": "MEROPS final Extracellular output from Peptidase Workflow", "require": True}],
        # [["-m3", "--anammox_files"],
        #  {"help": "Anammox tsv summary file", "require": True}],
        [["-l", "--nonredundant_genomes"],
         {"help": "File with list of non-redundant genomes in order", "require": True}],
        [["-p", "--pfam_count_table"],
         {"help": "PFAM extracellular assignments", "require": True}],
        [["-o", "--output_prefix"],
         {"help": "Output prefix to give summary file", "require": True}],
    ]

    ap = ArgParse(args_list, description="tsv_join:\tCombines multiple test outputs into single .tsv file")

    non_redundant_ids = list(line.decode().rstrip("\r\n") for line in open(ap.args.nonredundant_genomes, "rb"))

    gtdbtk_parser = GTDBtkParser(ap.args.gtdbtk_output)

    hmm_table = CountTable(ap.args.hmm_file)

    ko_table = CountTable(ap.args.kegg_file)

    pfam_table = CountTable(ap.args.pfam_count_table)

    merops_table = CountTable(ap.args.merops_file)

    checkm_reads = CheckMResult.read_checkm_analysis(ap.args.checkm_output)

    combined_tsv_header = "ID\tGTDBtk_taxonomy\tCheckM_Completion\tCheckM_Contamination\t"

    combined_tsv_header += "\t".join(hmm_table.header)

    combined_tsv_header += "\t"

    combined_tsv_header += "\t".join(ko_table.header)

    combined_tsv_header += "\t"

    combined_tsv_header += "\t".join(pfam_table.header)

    combined_tsv_header += "\t"

    combined_tsv_header += "\t".join(merops_table.header[1:])

    output_file = open(ap.args.output_prefix + ".tsv", "w")
    output_file.write(combined_tsv_header + "\n")
    for _id in non_redundant_ids:
        adj_id = _id.replace("_", "")
        out_string = _id + "\t"
        out_string += gtdbtk_parser.get_all_taxa(_id) + "\t"
        out_string += str(checkm_reads[_id].completeness) + "\t"
        out_string += str(checkm_reads[_id].contamination) + "\t"
        ko_found = False
        for k_id in ko_table.file_contents.keys():
            if k_id == adj_id:
                out_string += ko_table.get_line(adj_id) + "\t"
                ko_found = True
        if not ko_found:
            out_string += "No KO matches" + "\t"
        hmm_found = False
        for h_id in hmm_table.file_contents.keys():
            if h_id == adj_id:
                out_string += hmm_table.get_line(h_id) + "\t"
                hmm_found = True
        if not hmm_found:
            out_string += "No HMM matches" + "\t"
        try:
            out_string += pfam_table.get_line(_id)
        except KeyError:
            out_string += "No PFAM matches"
        try:
            out_string += merops_table.get_line(_id)
        except KeyError:
            out_string += "No MEROPS matches"
        output_file.write(out_string + "\n")
    output_file.close()
