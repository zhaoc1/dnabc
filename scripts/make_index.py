#!/usr/bin/env python
import argparse
import itertools

def get_args(argv):
    parser = argparse.ArgumentParser(
        description="creates index file for de-multiplexing.")
    parser.add_argument(
        "--reads", required=True,
        type=argparse.FileType("r"),
        help="Raw fastq file")
    parser.add_argument(
        "--output", required=True,
        type=argparse.FileType("w"),
        help="output file")
    args = parser.parse_args(argv)
    return(args)

def make_reverse_complement(seq):
    """
    Function to make reverse complement of a sequence
    """

    comp = {
        "A":"T",
        "T":"A",
        "G":"C",
        "C":"G",
        "N":"N",
        " ":""}

    rev = ""
    for i in range(0,len(seq)):
        rev = comp[seq[i]] + rev
    return rev

def _grouper(iterable, n):
    """ Collect data into fixed-length
    chunks or blocks """
    args = [iter(iterable)] * n
    return itertools.izip(*args)
                                    

def parse_fastq(f):
    """ parse original fastq file and
    write new fastq file the filtered
    non-human reads.
    """
    for desc, seq, _, qual in _grouper(f, 4):
        desc = desc.rstrip()[1:]
        seq = desc
        barcode = seq.split(":")[-1]
        yield desc, barcode

def write_index(out_fastq, desc, barcode):
        out_fastq.write("@" + desc + "\n")
        out_fastq.write(make_reverse_complement(barcode) + "\n")
        out_fastq.write("+\n")
        out_fastq.write("E" * len(barcode) + "\n")

def main(argv=None):
    args = get_args(argv)
    index = parse_fastq(args.reads)
    for desc, barcode in index:
        write_index(args.output, desc, barcode)
    args.reads.close()
    args.output.close()

if __name__=="__main__":
    main()
