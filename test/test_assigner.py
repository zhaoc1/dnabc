from collections import namedtuple
from io import StringIO
import os
import shutil
import tempfile
import unittest

from dnabclib.assigner import (
    BarcodeAssigner, deambiguate, reverse_complement,
    )


MockRead = namedtuple("Read", "seq")
MockSample = namedtuple("Sample", "name barcode")


class BarcodeAssignerTests(unittest.TestCase):
    def test_error_barcodes(self):
        a = BarcodeAssigner([], mismatches=1)
        obs = a._error_barcodes("AGG")
        exp = [
            "CGG", "GGG", "TGG",
            "AAG", "ACG", "ATG",
            "AGA", "AGC", "AGT",
            ]
        self.assertEqual(set(obs), set(exp))

    def test_one_mismatch(self):
        s = MockSample("Abc", "ACCTGAC")
        a = BarcodeAssigner([s], mismatches=1, revcomp=True)
        self.assertEqual(a.read_counts, {"Abc": 0, 'unassigned':0})

        # 0 mismatches
        self.assertEqual(a.assign("GTCAGGT"), s)
        self.assertEqual(a.read_counts, {"Abc": 1, 'unassigned':0})

        # 1 mismatch
        self.assertEqual(a.assign("GTCAAGT"), s)
        self.assertEqual(a.read_counts, {"Abc": 2, 'unassigned':0})

        # 2 mismatches
        self.assertEqual(a.assign("GTCAAAT"), None)
        self.assertEqual(a.read_counts, {"Abc": 2, 'unassigned':1})


class FunctionTests(unittest.TestCase):
    def test_deambiguate(self):
        obs = set(deambiguate("AYGR"))
        exp = set(["ACGA", "ACGG", "ATGA", "ATGG"])
        self.assertEqual(obs, exp)

        obs = set(deambiguate("AGN"))
        exp = set(["AGA", "AGC", "AGG", "AGT"])
        self.assertEqual(obs, exp)

    def test_reverse_complement(self):
        self.assertEqual(reverse_complement("AGATC"), "GATCT")
        self.assertRaises(KeyError, reverse_complement, "ANCC")

                
if __name__ == "__main__":
    unittest.main()
