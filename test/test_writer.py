from collections import namedtuple
import os.path
import shutil
import tempfile
import unittest

from dnabclib.writer import FastaWriter, FastqWriter, PairedFastqWriter


class FastaWriterTests(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.Sample = namedtuple("Sample", "name")
        self.Read = namedtuple("Read", ["desc", "seq"])

    def tearDown(self):
        shutil.rmtree(self.output_dir)
    
    def test_write(self):
        s1 = self.Sample("abc")
        s2 = self.Sample("d.e")
        w = FastaWriter(self.output_dir)

        w.write(self.Read("Read0", "ACCTTGG"), s1)
        w.close()

        fp = w._get_output_fp(s1)
        with open(fp) as f:
        	obs_output = f.read()
        self.assertEqual(obs_output, ">Read0\nACCTTGG\n")

        self.assertFalse(os.path.exists(w._get_output_fp(s2)))


class FastqWriterTests(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.Sample = namedtuple("Sample", "name")
        self.Read = namedtuple("Read", "desc seq qual")

    def tearDown(self):
        shutil.rmtree(self.output_dir)
    
    def test_write(self):
        s1 = self.Sample("h56")
        s2 = self.Sample("123")
        w = FastqWriter(self.output_dir)

        w.write(self.Read("Read0", "ACCTTGG", "#######"), s1)
        w.close()

        fp = w._get_output_fp(s1)
        with open(fp) as f:
        	obs_output = f.read()
        
        self.assertEqual(obs_output, "@Read0\nACCTTGG\n+\n#######\n")

        self.assertFalse(os.path.exists(w._get_output_fp(s2)))


class PairedFastqWriterTests(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.Sample = namedtuple("Sample", "name")
        self.Read = namedtuple("Read", "desc seq qual")

    def tearDown(self):
        shutil.rmtree(self.output_dir)
    
    def test_write(self):
        s1 = self.Sample("ghj")
        s2 = self.Sample("kl;")
        w = PairedFastqWriter(self.output_dir)

        readpair = (
            self.Read("Read0", "ACCTTGG", "#######"),
            self.Read("Read1", "GCTAGCT", ";342dfA"),
            )
        w.write(readpair, s1)
        w.close()

        fp1, fp2 = w._get_output_fp(s1)

        with open(fp1) as f:
        	obs1 = f.read()
        self.assertEqual(obs1, "@Read0\nACCTTGG\n+\n#######\n")

        with open(fp2) as f:
        	obs2 = f.read()
        self.assertEqual(obs2, "@Read1\nGCTAGCT\n+\n;342dfA\n")

        self.assertFalse(any(
            os.path.exists(fp) for fp in w._get_output_fp(s2)))


if __name__ == '__main__':
    unittest.main()
