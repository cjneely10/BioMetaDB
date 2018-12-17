#!/usr/bin/env python3

import os
import sys
import pandas as pd
from Visualizers.grapher import Grapher
from Accessories.arg_parse import ArgParse


if __name__ == "__main__":
    args_list = [
        [["-i", "--input_file"],
         {"help": ".tsv/.csv file to load", "require": True}],
        [["-o", "--output_prefix"],
         {"help": "Prefix to give to heatmap", "require": True}],
    ]

    ap = ArgParse(args_list, description="xsv_to_heatmap:\tGenerate matplotlib heatmap for .tsv/csv file")

    _, ext = os.path.splitext(ap.args.input_file)
    csv_table = None
    if ext == ".tsv" or ext == ".imtbx":
        csv_table = pd.read_table(ap.args.input_file, sep="\t")
    elif ext == ".csv":
        csv_table = pd.read_table(ap.args.input_file)
    else:
        sys.stderr.write_class("File is incorrect format\n")
        exit(1)

    grapher = Grapher((8, 8))
    grapher.init()
    grapher.plt.imshow(csv_table.values, cmap='hot', interpolation='nearest')
    grapher.plt.show()
    grapher.fig.savefig(ap.args.output_prefix + ".png")
