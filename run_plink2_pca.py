#!/usr/bin/env python3

import sys
import os
import subprocess as sbp
import argparse

def main(args):
    
    INPREFIX = args.pfile_prefix
    OUT = args.output_prefix

    check = sbp.run(["which", "plink2"], capture_output=True, text=True)
    if check.returncode != 0:
        print("Error: plink2 is not installed or not in PATH.")
        sys.exit(1)

    if 'extract' not in args.other_args:
        args.extract = f'{INPREFIX}.prune.in'

    if not os.path.isfile(f'{INPREFIX}.prune.in'):
        print(f"Error: Extract file {INPREFIX}.prune.in does not exist.")
        sys.exit(1)

    command = ['plink2', '--pfile', INPREFIX, '--out', OUT]
    command += ['--pca', '20', 'allele-wts']
    command += ['--extract', f'{args.extract}']
    command += args.other_args

    print("Running command:", ' '.join(command), file=sys.stderr)
    print(" ", file=sys.stderr)

    sbp.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper of PLINK2 to perform PCA on pfile format.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("pfile_prefix", help="Input PLINK2 pfile prefix")
    parser.add_argument("output_prefix", help="Output prefix for PCA results")
    parser.add_argument("other_args", nargs=argparse.REMAINDER, help="Additional arguments to pass to plink2")


    args = parser.parse_args()
    main(args)