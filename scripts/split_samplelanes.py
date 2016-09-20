#!/usr/bin/env python
import csv
import argparse

def get_args(argv):
    parser = argparse.ArgumentParser(
        description="creates barcode file by lane for de-multiplexing.")
    parser.add_argument(
        "--sample-sheet", required=True,
        type=argparse.FileType("r"),
        help="sample-sheet file")
    parser.add_argument(
        "--lane", required=True,
        help="Lane number")
    parser.add_argument(
        "--output", required=True,
        type=argparse.FileType("w"),
        help="output file")
    args = parser.parse_args(argv)
    return(args)

def main(argv=None):
    args = get_args(argv)
    reader = csv.reader(args.sample_sheet, delimiter=",")
    w = csv.writer(args.output, delimiter="\t")
    for row in reader:
        if row[1]==args.lane:
            w.writerow([row[2].replace(" ",""), row[4].replace("-","")])
    args.sample_sheet.close()
    args.output.close()

if __name__=="__main__":
    main()
