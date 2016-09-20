#!/usr/bin/env python

from distutils.core import setup

# Get version number from package
exec(open('dnabclib/version.py').read())

setup(
    name='DNAbc',
    version=__version__,
    description='Demultiplex pooled DNA sequencing data',
    author='Kyle Bittinger',
    author_email='kylebittinger@gmail.com',
    url='https://github.com/PennChopMicrobiomeProgram',
    packages=['dnabclib'],
    scripts=[
        'scripts/dnabc.py',
        'scripts/split_samplelanes.py',
        'scripts/make_index.py',
        'scripts/get_sample_names.py'],
    )
