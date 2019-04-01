from BioMetaDB.Accessories.arg_parse import ArgParse
from BioMetaDB.Accessories.ops import chunk

CHUNK_SIZE = 10000

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

    R = open(ap.args.fix_file, "rb")
    # For possibly large files
    for batch in chunk(R, CHUNK_SIZE):
        for line in R:
            line = line.decode().rstrip("\r\n")
            if line.startswith("@"):
                line = next(R)
            while line == "ISSUE:\n":
                line = next(R)
