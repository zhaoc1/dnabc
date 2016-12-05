import itertools


class BarcodeAssigner(object):
    def __init__(self, samples, mismatches=0, revcomp=True):
        self.samples = samples
        if mismatches not in [0]:
            raise ValueError(
                "Only 0 mismatches allowed (got %s)" % mismatches)
        self.mismatches = mismatches
        self.revcomp = revcomp
        # Sample names assumed to be unique after validating input data
        self.read_counts = dict((s.name, 0) for s in self.samples)
        self.read_counts['unassigned'] = 0
        self._init_hash()

    def _init_hash(self):
        self._barcodes = {}
        for s in self.samples:
            # Barcodes assumed to be present after validating input data
            if self.revcomp:
                bc = reverse_complement(s.barcode)
            else:
                bc = s.barcode

            # Barcodes assumed to be unique after validating input data
            self._barcodes[bc] = s

            for error_bc in self._error_barcodes(bc):
                # Barcodes not guaranteed to be unique after
                # accounting for errors
                if error_bc in self._barcodes:
                    raise ValueError(
                        "Barcode %s for sample %s matches barcode for "
                        "sample %s with %s mismatches" % (
                            error_bc, self._barcodes[error_bc], s,
                            self.mismatches))
                else:
                    self._barcodes[error_bc] = s

    def _error_barcodes(self, barcode):
        # If the number of mismatches is set to 0, there will be no
        # error barcodes. Immediately stop the iteration.
        if self.mismatches == 0:
            raise StopIteration
        # Each item in idx_sets is a set of indices where mismatches
        # should occur.
        idx_sets = itertools.combinations(range(len(barcode)), self.mismatches)
        for idx_set in idx_sets:
            # Change to list because strings are immutable
            bc = list(barcode)
            # Replace the base at each mismatch position with an
            # ambiguous base specifying all possibilities BUT the one
            # we see.
            for idx in idx_set:
                bc[idx] = AMBIGUOUS_BASES_COMPLEMENT[bc[idx]]
            # Expand to all possibilities for mismatching at this
            # particular set of positions
            for error_bc in deambiguate(bc):
                yield error_bc
        
    def assign(self, seq):
        sample = self._barcodes.get(seq)
        if sample is not None:
            self.read_counts[sample.name] += 1
        else:
            self.read_counts['unassigned'] += 1
        return sample


AMBIGUOUS_BASES = {
    "T": "T",
    "C": "C",
    "A": "A",
    "G": "G",
    "R": "AG",
    "Y": "TC",
    "M": "CA",
    "K": "TG",
    "S": "CG",
    "W": "TA",
    "H": "TCA",
    "B": "TCG",
    "V": "CAG",
    "D": "TAG",
    "N": "TCAG",
    }


# Ambiguous base codes for all bases EXCEPT the key
AMBIGUOUS_BASES_COMPLEMENT = {
    "T": "V",
    "C": "D",
    "A": "B",
    "G": "H",
    }


def deambiguate(seq):
    nt_choices = [AMBIGUOUS_BASES[x] for x in seq]
    return ["".join(c) for c in itertools.product(*nt_choices)]


COMPLEMENT_BASES = {
    "T": "A",
    "C": "G",
    "A": "T",
    "G": "C",
    }


def reverse_complement(seq):
    rc = [COMPLEMENT_BASES[x] for x in seq]
    rc.reverse()
    return ''.join(rc)
