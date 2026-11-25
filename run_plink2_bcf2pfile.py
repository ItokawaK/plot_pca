#!/usr/bin/env python3

import sys
import os
import subprocess as sbp
import argparse

def main(args):

    BCF = args.bcf_file
    OUT = args.output_prefix

    check = sbp.run(["which", "plink2"], capture_output=True, text=True)
    if check.returncode != 0:
        print("Error: plink2 is not installed or not in PATH.")
        sys.exit(1)

    command = ['plink2', '--bcf', BCF, '--out', OUT]
    command += ['--allow-extra-chr']
    command += ['--geno', f'{args.geno}'] # default missing genotype threshold  0.1
    command += ['--hardy']
    command += ['--indep-pairwise'] + args.indep_pairwise.split(' ') # default indep-pairwise 50kb 0.2
    command += ['--maf', f'{args.maf}'] # default minor allele frequency threshold 0.05
    command += ['--make-pgen']
    command += ['--max-alleles', f'{args.max_alleles}'] # default max alleles 2
    command += ['--min-alleles', f'{args.min_alleles}'] # default min alleles 2
    command += ['--mind', f'{args.mind}'] # default missing individual threshold 0.1
    command += ['--var-min-qual', f'{args.var_min_qual}']  # default variant minimum quality threshold 30
    command += ['--vcf-half-call', f'{args.vcf_half_call}'] # default vcf half call missing
    command += ['--vcf-min-dp', f'{args.vcf_min_dp}'] # default vcf minimum depth threshold 10
    command += ['--vcf-min-gq', f'{args.vcf_min_gq}'] # default vcf minimum genotype quality threshold 10

    command += args.other_args

    print("Running command:", ' '.join(command), file=sys.stderr)
    print(" ", file=sys.stderr)

    sbp.run(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper of PLINK2 to convert BCF to pfile format.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("bcf_file", help="Input BCF file")
    parser.add_argument("output_prefix", help="Output prefix for PLINK2 pfile")
    parser.add_argument("--geno", type=float, default=0.1, help="Missing genotype threshold")
    parser.add_argument("--indep_pairwise", type=str, default="50kb 0.2", help="Indep-pairwise parameters")
    parser.add_argument("--maf", type=float, default=0.05, help="Minor allele frequency threshold")
    parser.add_argument("--max_alleles", type=int, default=2, help="Maximum alleles")
    parser.add_argument("--min_alleles", type=int, default=2, help="Minimum alleles")
    parser.add_argument("--mind", type=float, default=0.3, help="Missing individual threshold")
    parser.add_argument("--var_min_qual", type=int, default=30, help="Variant minimum quality threshold")
    parser.add_argument("--vcf_half_call", type=str, default="missing", help="VCF half call missing")
    parser.add_argument("--vcf_min_dp", type=int, default=10, help="VCF minimum depth threshold")
    parser.add_argument("--vcf_min_gq", type=int, default=10, help="VCF minimum genotype quality threshold")
    parser.add_argument("other_args", nargs=argparse.REMAINDER, help="Additional arguments to pass to plink2")

    args = parser.parse_args()  
    main(args)