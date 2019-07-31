#!/usr/bin/env python3
from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.Accessories.ops import chunk
import fileinput
import sys
import os


CHUNK_SIZE = 1000


def issue_match(search_params_set, issue_info, replace_dict):
    """ Function checks if user-set criteria in search_params was met by the particular issue
    data in *args

    :return:
    """
    # Issue matches search criteria passed by user
    set_values = set(issue_info.values())
    for key in search_params_set:
        if key not in set_values:
            return None
    replace_string = list(replace_dict.values())[0]
    for item in issue_info.keys():
        if item is not None and issue_info[item] is not None:
            replace_string = replace_string.replace("<%s>" % item, issue_info[item])
    return replace_string


if __name__ == "__main__":
    args_list = (
        (("-m", "--match"),
         {"help": "Look for issues matching list, ex: RECORD,BAD_LOCATION,genomic", "required": True}),
        (("-r", "--replace"),
         {"help": "Set value using list, ex: FILE,/path/to/<ID>.fna", "required": True}),
        (("-f", "--fix_file"),
         {"help": "/path/to/generated_fix_file.fix", "required": True}),
    )

    ap = ArgParse(args_list, description="Script will make changes to .fix file\n")

    R = fileinput.FileInput(ap.args.fix_file, inplace=True, backup=".bak")
    search_params = set([val for val in ap.args.match.split(",") if val != ""])
    _replace_lookup = [_v for _v in ap.args.replace.split(",") if _v != ""]
    replace_lookup = {_replace_lookup[0]: _replace_lookup[1]}
    # For possibly large files
    _id = ""
    data_type = ""
    location = None
    fix_data = None
    issue_type = ""
    fix_type = ""
    replace_id = None
    fix_data_col = list(replace_lookup.keys())[0]
    try:
        for batch in chunk(R, CHUNK_SIZE):
            for line in R:
                while line.startswith("@"):
                    line = next(R)
                    sys.stdout.write(line)
                while line == "ISSUE:\n":
                    # Read in '<DATA_TYPE:\t<ID>[:\t<LOCATION]\n' line
                    line = next(R)
                    sys.stdout.write(line)
                    line = line.rstrip("\r\n").split(":\t")
                    data_type = line[0]
                    _id = line[1]
                    if len(line) == 3:
                        location = line[2]
                    # Read in '<ISSUE_TYPE>\t<FIX_TYPE>[\t<FIX_DATA>]\n' line
                    line = next(R)
                    line = line.rstrip("\r\n").split("\t")
                    issue_type = line[0]
                    fix_type = line[1]
                    fix_data = issue_match(
                        search_params,
                        {"DATA_TYPE": data_type,
                         "ID": _id,
                         "LOCATION": location,
                         "FIX_DATA": fix_data,
                         "ISSUE_TYPE": issue_type,
                         "FIX_TYPE": fix_type},
                        replace_lookup
                    )
                    if fix_data:
                        sys.stdout.write("%s\t%s\t%s\n" % (line[0], fix_data_col, fix_data))
                    else:
                        sys.stdout.write("%s\t%s\n" % (line[0],"\t".join(line[1:])))
                    # Read in '---' line
                    line = next(R)
                    sys.stdout.write(line)
                    # Read in next issue header
                    line = next(R)
                    sys.stdout.write(line)
                    fix_data = None
    except StopIteration:
        pass
    R.close()
    os.remove(ap.args.fix_file + ".bak")
