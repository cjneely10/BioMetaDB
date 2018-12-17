import os
import shutil
from collections import defaultdict

"""
Script holds class that parses the results from parse_fastANI.py and serialized CheckM results
Outputs folders with copied datafiles and an output summary linking redundant genomes
with their best copies

"""


class RedundancyChecker:

    @staticmethod
    def parse_fastANI_with_checkm_results(file_, checkm_reads, cutoff_criteria, output_prefix):
        """ Combines parse_fastANI.py output with serialized checkm data per cutoff criteria

        :param output_prefix: (str) Prefix for output files
        :param file_: (str)	parse_fastANI.py output file
        :param checkm_reads: (Dict[str, CheckMResult])	output from read_checkm_analysis
        :param cutoff_criteria: (float)	Inclusive cutoff value
        :return Tuple[Set[CheckMResult], Set[str]]:
        """
        match_dict = defaultdict(list)
        # Read by line
        with open(file_, "r") as R:
            next(R)
            for line in R:
                line = line.strip("\n").split("\t")
                A = line[0].strip(".fna")
                B = line[1].strip(".fna")
                # Only save single match and values above cutoff criteria
                if float(line[2]) >= float(cutoff_criteria):
                    match = checkm_reads[B]
                    # Only high completeness low contamination genomes
                    if match.completeness >= 50 and match.contamination <= 5 and match not in match_dict[A]:
                        match_dict[A].append(match)
        hc_unique = set()
        # Begin writing to summary file
        W = open("{}.txt".format(output_prefix), "w")
        W.write("Best match:Completeness,Contamination\t[Next Match:Completeness,Contamination]\n")
        match_data = {}
        for q, match_list in match_dict.items():
            # Combine query with matches
            match_list.append(checkm_reads[q])
            # Set max match as first in list
            max_match = match_list[0]
            for match in match_list:
                # Replace with more complete and less contaminated genomes
                if match.completeness > max_match.completeness and match.contamination < max_match.contamination:
                    max_match = match
            # Separate max from others
            match_data[max_match._id] = [match for match in match_list if match != max_match]
            hc_unique.add(max_match._id)
        # Record duplicate genomes
        duplicate_genomes = set()
        for match_id in hc_unique:
            # Add duplicates for each unique id
            for match in match_data[match_id]:
                duplicate_genomes.add(match._id)
            # Write to summary file
            RedundancyChecker._write_to_output_file(W, checkm_reads[match_id], match_data[match_id])
        W.close()
        return hc_unique, duplicate_genomes

    @staticmethod
    def _write_to_output_file(W, max_match, non_max_match):
        """ Protected member writes data to summary file

        :param W: (object)	file object that is writing
        :param max_match: (CheckMResult)	best matching result
        :param non_max_match: (List[CheckMResult])	other results in list
        :return None:
        """
        W.write_class("{}:{},{}".format(max_match._id, max_match.completeness, max_match.contamination))
        for non_match in non_max_match:
            W.write_class("\t{}:{},{}".format(non_match._id, non_match.completeness, non_match.contamination))
        W.write_class("\n")

    @staticmethod
    def summary_and_copy_genomes_to_folders(checkm_reads, duplicate_genomes, genomes_dir, output_prefix):
        """ Creates printed summary based on files in folder and copies files


        :param checkm_reads: (List[CheckMResult])	list of CheckM reads
        :param duplicate_genomes: (List[str])	list of duplicate genome IDs
        :param genomes_dir: (str)	directory containing all genomes to filter
        :param output_prefix: (str)	output prefix for directory
        :return None:
        """
        # Directory names
        nonred = str(output_prefix) + "/{}.nonredundant".format(output_prefix)
        refine = str(output_prefix) + "/{}.refine".format(output_prefix)
        red = str(output_prefix) + "/{}.redundant".format(output_prefix)
        rem = str(output_prefix) + "/{}.remaining".format(output_prefix)
        # Create directory
        if not os.path.isdir(output_prefix):
            os.makedirs(output_prefix)
            os.makedirs(nonred)
            os.makedirs(red)
            os.makedirs(refine)
        num_rem = 0
        num_non_red = 0
        num_refine = 0
        num_red = 0
        # list of all CheckM ids
        reads_set = set(checkm_reads.keys())
        for name in os.listdir(genomes_dir):
            _name = name.strip(".fna")
            name = genomes_dir + "/{}".format(name)
            # Build summary string
            results_str = str(name) + " copied to "
            # Get non-duplicate genomes that have high completeness and low contamination
            if _name not in duplicate_genomes and _name in reads_set and checkm_reads[_name].completeness >= 50 and \
                    checkm_reads[_name].contamination <= 5:
                shutil.copyfile(name, nonred + "/" + _name + ".fna")
                results_str += "nonredundant"
                num_non_red += 1
            # Get non-duplicate genomes that have high completeness and high contamination
            elif _name not in duplicate_genomes and _name in reads_set and checkm_reads[_name].completeness >= 50 and \
                    checkm_reads[_name].contamination >= 5:
                shutil.copyfile(name, refine + "/" + _name + ".fna")
                results_str += "refine"
                num_refine += 1
            # Redundant genomes
            elif _name in duplicate_genomes:
                shutil.copyfile(name, red + "/" + _name + ".fna")
                results_str += "redundant"
                num_red += 1
            # Other genomes
            else:
                shutil.copyfile(name, red + "/" + _name + ".fna")
                results_str += "remaining"
                num_rem += 1
            # Output results string
            print(results_str)
        # Output summary string
        print("Nonredundant: ", num_non_red, "Redundant: ", num_red, "to refine: ", num_refine, "Remaining: ", num_rem)
