import argparse
import json
import os

from .writer import FastaWriter, PairedFastqWriter
from .sample import Sample
from .seqfile import IndexFastqSequenceFile
from .seqfile import NoIndexFastqSequenceFile
from .assigner import BarcodeAssigner
from .version import __version__

writers = {
    "fastq": PairedFastqWriter,
    "fasta": FastaWriter,
}


def get_sample_names_main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--barcode-file", required=True,
        type=argparse.FileType("r"),
        help="Barcode information file")
    p.add_argument(
        "--output-file", required=True,
        type=argparse.FileType("w"),
        help="Output file of sample names"
    )
    args = p.parse_args(argv)
    
    samples = Sample.load(args.barcode_file)
    for s in samples:
        args.output_file.write("%s\n" % s.name)


def get_config(user_config_file):
    config = {
        "output_format": "fastq"
    }

    if user_config_file is None:
        default_user_config_fp = os.path.expanduser("~/.dnabc.json")
        if os.path.exists(default_user_config_fp):
            user_config_file = open(default_user_config_fp)

    if user_config_file is not None:
        user_config = json.load(user_config_file)
        config.update(user_config)
    return config


def main(argv=None):
    p = argparse.ArgumentParser()
    # Input
    p.add_argument(
        "--forward-reads", required=True,
        type=argparse.FileType("r"),
        help="Forward reads file (FASTQ format)")
    p.add_argument(
        "--reverse-reads", required=True,
        type=argparse.FileType("r"),
        help="Reverse reads file (FASTQ format)")
    p.add_argument(
        "--index-reads",
        type=argparse.FileType("r"), help=(
            "Index reads file (FASTQ format). If this file is not provided, "
            "the index reads will be taken from the description lines in the "
            "forward reads file."))
    p.add_argument(
        "--barcode-file", required=True,
        help="Barcode information file",
        type=argparse.FileType("r"))
    # Output
    p.add_argument(
        "--output-dir", required=True,
        help="Output sequence data directory")
    p.add_argument(
        "--summary-file", required=True,
        type=argparse.FileType("w"),
        help="Summary filepath")
    # Config
    p.add_argument("--config-file",
        type=argparse.FileType("r"),
        help="Configuration file (JSON format)")
    args = p.parse_args(argv)

    config = get_config(args.config_file)

    samples = list(Sample.load(args.barcode_file))

    writer_cls = writers[config["output_format"]]
    if not os.path.exists(args.output_dir):
       #p.error("Output directory already exists")
       os.mkdir(args.output_dir)
    writer = writer_cls(args.output_dir)

    if args.index_reads is None:
        seq_file = NoIndexFastqSequenceFile(
            args.forward_reads, args.reverse_reads)
        assigner = BarcodeAssigner(samples, revcomp=False)
    else:
        seq_file = IndexFastqSequenceFile(
            args.forward_reads, args.reverse_reads, args.index_reads)
        assigner = BarcodeAssigner(samples, revcomp=True)

    summary_data = seq_file.demultiplex(assigner, writer)
    save_summary(args.summary_file, config, summary_data)


def save_summary(f, config, data):
    result = {
        "program": "dnabc",
        "version": __version__,
        "config": config,
        "data": data,
        }
    json.dump(result, f)
