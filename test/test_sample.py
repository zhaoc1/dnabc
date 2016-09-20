import unittest

from dnabclib.sample import Sample


class SampleTests(unittest.TestCase):
    def test_prefixes(self):
        s = Sample("a", "agct")
        self.assertEqual(s.barcode, "AGCT")


if __name__ == "__main__":
    unittest.main()
