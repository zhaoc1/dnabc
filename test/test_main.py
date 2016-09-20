import json
import os
import shutil
import tempfile
import unittest

from dnabclib.main import (
    main, get_config, get_sample_names_main,
)


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp_home_dir = tempfile.mkdtemp()
        self._old_home_dir = os.environ['HOME']
        os.environ['HOME'] = self.temp_home_dir

    def tearDown(self):
        shutil.rmtree(self.temp_home_dir)
        os.environ['HOME'] = self._old_home_dir

    def test_default_config_locataion(self):
        """Config file in user home dir should be read and used"""
        with open(os.path.join(self.temp_home_dir, ".dnabc.json"), "w") as f:
            f.write('{"output_format": "SOMECRAZYVALUE"}')
        config = get_config(None)
        self.assertEqual(config["output_format"], u"SOMECRAZYVALUE")


class FastqDemultiplexTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.index_fp = os.path.join(
            self.temp_dir, "Undetermined_S0_L001_I1_001.fastq")
        self.index_contents = (
            "@a\nACGTACGT\n+\n9812734[\n"
            "@b\nGGGGCGCT\n+\n78154987\n"
            "@c\nCCTTCCTT\n+\nkjafd;;;\n")
        with open(self.index_fp, "w") as f:
            f.write(self.index_contents)

        self.forward_fp = os.path.join(
            self.temp_dir, "Undetermined_S0_L001_R1_001.fastq")
        with open(self.forward_fp, "w") as f:
            f.write(
                "@a\nGACTGCAGACGACTACGACGT\n+\n8A7T4C2G3CkAjThCeArG;\n"
                "@b\nCAGTCAGACGCGCATCAGATC\n+\n78154987bjhasf78612rb\n"
                "@c\nTCAGTACGTACGATACGTACG\n+\nkjafd;;;hjfasd82AHG99\n")

        self.reverse_fp = os.path.join(
            self.temp_dir, "Undetermined_S0_L001_R2_001.fastq")
        with open(self.reverse_fp, "w") as f:
            f.write(
                "@a\nCATACGACGACTACGACTCAG\n+\nkjfhda987123GA;,.;,..\n"
                "@b\nGTNNNNNNNNNNNNNNNNNNN\n+\n#####################\n"
                "@c\nACTAGACTACGCATCAGCATG\n+\nkjafd;;;hjfasd82AHG99\n")

        self.barcode_fp = os.path.join(self.temp_dir, "manifest.txt")
        with open(self.barcode_fp, "w") as f:
            f.write(
                "SampleA\tAAGGAAGG\n"
                "SampleB\tACGTACGT\n")

        self.output_dir = os.path.join(self.temp_dir, "output")
        self.summary_fp = os.path.join(self.temp_dir, "summary.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_regular(self):
        main([
            "--forward-reads", self.forward_fp,
            "--reverse-reads", self.reverse_fp,
            "--index-reads", self.index_fp,
            "--barcode-file", self.barcode_fp,
            "--output-dir", self.output_dir,
            "--summary-file", self.summary_fp,
            ])
        with open(self.summary_fp) as f:
            res = json.load(f)
            self.assertEqual(res["data"], {"SampleA": 1, "SampleB": 1, "unassigned":1})


class SampleNameTests(unittest.TestCase):
    def test_get_sample_names_main(self):
        barcode_file = tempfile.NamedTemporaryFile()
        barcode_file.write(
            b"SampleA\tAAGGAAGG\n"
            b"SampleB\tACGTACGT\n")
        barcode_file.seek(0)

        output_file = tempfile.NamedTemporaryFile()
        
        get_sample_names_main([
            "--barcode-file", barcode_file.name,
            "--output-file", output_file.name,
        ])

        output_file.seek(0)
        observed_sample_names = output_file.read()

        self.assertEqual(observed_sample_names, b"SampleA\nSampleB\n")

if __name__ == "__main__":
    unittest.main()
