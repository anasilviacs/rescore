"""
Module that calls the necessary functions and run the re-scoring algorithm.
"""

import argparse
import sys
import subprocess

import mgf_msgf2pin
from mapper import mapper
import pin2pepfile
import features2pin

# Path to MSGFPlus - this should come from a config file
MSGF_DIR = "/home/compomics/software/MSGFPlus"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run MSGF+ and Percolator')
    parser.add_argument('spec_file', metavar='spectrum-file',
                        help='file containing MS2 spectra (MGF,PKL,DTA,mzXML,mzDATA or mzML)')
    parser.add_argument('fasta_file', metavar='FASTA-file',
                        help='file containing protein sequences')
    parser.add_argument('-m', '--mods', metavar='FILE', action="store", default='',
                        dest='modsfile', help='Mods.txt file for MSGF+')
    parser.add_argument('-f', '--frag', metavar='frag_method', action="store", default='HCD',
                        dest='frag', help='fragmentation method (CID or HCD), default HCD')

    args = parser.parse_args()

    # Run MSGF+
    mgf_msgf2pin.run_msgfplus(MSGF_DIR, args.spec_file + ".target", args.spec_file,
                 args.fasta_file, args.modsfile, args.frag)

    # Convert .mzid to pin, for percolator. XXX is the decoy pattern from MSGF+
    convert_command = "msgf2pin -P XXX %s.mzid > %s.pin" % (
        args.spec_file + ".target", args.spec_file + ".target")
    sys.stdout.write("Converting .mzid file to pin file: {}".format(convert_command))
    sys.stdout.flush()
    subprocess.run(convert_command, shell=True)

    # Add mgf TITLE column to pin file
    pin = mapper.lazy_pin_parser(args.spec_file + ".target.pin")
    pin = mapper.map_mgf_title(pin, args.spec_file + ".target")

    pin.to_csv(args.spec_file + ".target.titles.pin", sep='\t', index=False)

    peprec = pin2pepfile.make_pepfile(args.spec_file + ".target.titles.pin")
    pin2pepfile.write_PEPREC(peprec, args.spec_file + ".target.titles.pin")

    # Run ms2pip_rescore

    features = join_features(args.pep_file + '.target.titles.pin.PEPREC_rescore_features.csv', args.pin)
    write_pin_files(features)

    # Run Percolator
