#!/usr/bin/env python
#
# file: $(NEDC_NFC)/util/python/nedc_eval_eeg/nedc_eval_eeg.py
#
# revision history:
#
# 20200730 (LV): merged research and competition versions, added NIST option
# 20170730 (JP): moved parameter file constants out of this driver
# 20170728 (JP): added error checking for duration
# 20170716 (JP): upgraded to using the new annotation tools.
# 20170527 (JP): added epoch-based scoring
# 20150520 (SZ): modularized the code
# 20170510 (VS): encapsulated the three scoring metrics
# 20161230 (SL): revision for standards
# 20150619 (SZ): initial version
# ------------------------------------------------------------------------------

# import system modules
#
import os
import sys
import time

# import NEDC support modules
#
import nedc_comp_tools as nct
import nedc_eval_common as nec
import nedc_cmdl_parser as ncp
import nedc_debug_tools as ndt
import nedc_file_tools as nft

# import NEDC scoring modules
#
import nedc_eval_nist as nnist
import nedc_eval_dpalign as ndpalign
import nedc_eval_epoch as nepoch
import nedc_eval_ovlp as novlp
import nedc_eval_taes as ntaes
import nedc_eval_ira as nira

# ------------------------------------------------------------------------------
#
# global variables are listed here
#
# ------------------------------------------------------------------------------

# set the filename using basename
#
__FILE__ = os.path.basename(__file__)

# define script location
#
SCRIPT_LOC = os.path.dirname(os.path.realpath(__file__))

# define the help file and usage message
#
HELP_FILE = SCRIPT_LOC + "/nedc_eval_eeg.help"
USAGE_FILE = SCRIPT_LOC + "/nedc_eval_eeg.usage"

# define the program options:
#  note that you cannot separate them by spaces
#
ARG_ODIR = "--odir"
ARG_ABRV_ODIR = "-o"

ARG_PARM = "--parameters"
ARG_ABRV_PARM = "-p"

ARG_NIST = "--nist"
ARG_ABRV_NIST = "-n"

ARG_COMP = "--competition"
ARG_ABRV_COMP = "-c"

# define default values for arguments:
#  note we assume the parameter file is in the same
#  directory as the source code.
#
DEF_PFILE = SCRIPT_LOC + "/nedc_eval_eeg_params_v00.txt"
DEF_ODIR = "./output"

# define the required number of arguments
#
NUM_ARGS = 2

# define the names of the output files
#
NEDC_SUMMARY_FILE = "summary.txt"
NEDC_DPALIGN_FILE = "summary_dpalign.txt"
NEDC_NIST_FILE = "summary_nist.txt"
NEDC_EPOCH_FILE = "summary_epoch.txt"
NEDC_OVLP_FILE = "summary_ovlp.txt"
NEDC_TAES_FILE = "summary_taes.txt"
NEDC_IRA_FILE = "summary_ira.txt"

# define parameters for competition version:
#  the competition version does not use parameter files by default
#
DEF_COMP_DPALIGN = {"penalty_del": "1.0", "penalty_ins": "1.0", "penalty_sub": "1.0"}
DEF_COMP_EPOCH = {"epoch_duration": "0.25", "null_class": "BCKG"}
DEF_COMP_OVLP = {"guard_width": "0.001", "ndigits_round": "3"}
DEF_COMP_TAES = {}


# define formatting constants
#
NEDC_EVAL_SEP = nft.DELIM_EQUAL * 78
NEDC_VERSION = "NEDC Eval EEG (v4.0.0)"

# define class definitions
#
SEIZ = "SEIZ"
BCKG = "BCKG"
CLASSES = [SEIZ, BCKG]

# ------------------------------------------------------------------------------
#
# the main program starts here
#
# ------------------------------------------------------------------------------

# method: main
#
# arguments: none
#
# return: none
#
# This function is the main program.
#
def main(argv):

    # declare local variables
    #
    status = True
    dbgl = ndt.Dbgl()

    # declare default values for command line arguments
    #
    odir = nft.get_fullpath(DEF_ODIR)

    # create a command line parser
    #
    cmdl = ncp.Cmdl(USAGE_FILE, HELP_FILE)

    # define the command line arguments
    #
    cmdl.add_argument("files", type=str, nargs="*")
    cmdl.add_argument(ARG_ABRV_ODIR, ARG_ODIR, type=str)
    cmdl.add_argument(ARG_ABRV_PARM, ARG_PARM, type=str)
    cmdl.add_argument(ARG_ABRV_COMP, ARG_COMP, action="store_true")
    cmdl.add_argument(ARG_ABRV_NIST, ARG_NIST, action="store_true")

    # parse the command line
    #
    args = cmdl.parse_args()

    if dbgl > ndt.NONE:
        print("command line arguments:")
        print(" output directory = %s" % (args.odir))
        print(" nist = %s" % (bool(args.nist)))
        print(" competition = %d" % (bool(args.competition)))
        print(" ref file  = %s" % (args.files[0]))
        print(" hyp file = %s" % (args.files[1]))
        print("")

    # check if the proper number of lists has been provided
    #
    if len(args.files) != NUM_ARGS:
        cmdl.print_usage("stdout")
        sys.exit(os.EX_SOFTWARE)

    # check if there are contradictions in the arguments provided
    #
    if (args.competition is not False) and (args.nist is not False):
        print(
            "Error: %s (line: %s) %s: %s"
            % (
                __FILE__,
                ndt.__LINE__,
                ndt.__NAME__,
                "competiton and NIST args cannot be specified together",
            )
        )
        cmdl.print_usage("stdout")
        sys.exit(os.EX_SOFTWARE)

    if (args.competition is not False) and (args.parameters is not None):
        print(
            "Error: %s (line: %s) %s: %s"
            % (
                __FILE__,
                ndt.__LINE__,
                ndt.__NAME__,
                "parameters should not be specified for competition version",
            )
        )
        cmdl.print_usage("stdout")
        sys.exit(os.EX_SOFTWARE)

    # set argument values
    #
    if args.odir is not None:
        odir = args.odir

    if args.parameters is not None:
        pfile = args.parameters

    if (args.parameters is None) and (args.competition is False):
        pfile = nft.get_fullpath(DEF_PFILE)

    # if using competition version, define parameters
    #
    if args.competition is not False:
        nedc_dpalign = DEF_COMP_DPALIGN
        nedc_epoch = DEF_COMP_EPOCH
        nedc_ovlp = DEF_COMP_OVLP
        nedc_taes = DEF_COMP_TAES

    # if using research version, load parameters
    #
    else:
        nedc_dpalign = nft.load_parameters(pfile, ndpalign.NEDC_DPALIGN)
        nedc_epoch = nft.load_parameters(pfile, nepoch.NEDC_EPOCH)
        nedc_ovlp = nft.load_parameters(pfile, novlp.NEDC_OVLP)
        nedc_taes = nft.load_parameters(pfile, ntaes.NEDC_TAES)
        nedc_ira = nft.load_parameters(pfile, nira.NEDC_IRA)

    # if using NIST scoring algorithm, load NIST parameters
    #
    if args.nist is not False:
        nist_f4de = nft.load_parameters(pfile, nnist.NIST_F4DE)

    # set the input lists
    #
    fname_ref = args.files[0]
    fname_hyp = args.files[1]

    # if using research version, parse the ref and hyp file lists
    #
    if args.competition is False:
        reflist = nft.get_flist(fname_ref)
        hyplist = nft.get_flist(fname_hyp)
        ref_anns = nec.parse_files(reflist)
        hyp_anns = nec.parse_files(hyplist)

    # if using competition version, parse the ref and hyp files:
    #  dur_dict is a dictionary that maps durations to file names and
    #  is created from the reference files to fill gaps in hypothesis
    #  files
    #
    else:
        ref_anns, dur_dict = nct.parse_file(fname_ref)
        hyp_anns = nct.parse_file(fname_hyp, dur_dict)

    # check for mismatched file lists:
    #  note that we do this here so it is done only once, rather than
    #  in each scoring method
    #
    if (ref_anns == None) or (hyp_anns == None):
        print(
            "Error: %s (line: %s) %s: %s (ref: %s) and (hyp: %s)"
            % (
                __FILE__,
                ndt.__LINE__,
                ndt.__NAME__,
                "error loading filelists",
                fname_ref,
                fname_hyp,
            )
        )
        sys.exit(os.EX_SOFTWARE)
    elif len(ref_anns) != len(hyp_anns):
        print(
            "Error: %s (line: %s) %s: (ref: %d) and (hyp: %d) %s"
            % (
                __FILE__,
                ndt.__LINE__,
                ndt.__NAME__,
                len(ref_anns),
                len(hyp_anns),
                "have different lengths",
            )
        )
        sys.exit(os.EX_SOFTWARE)

    # load the scoring map for competition version
    #
    if args.competition is not False:
        tmpmap = {}
        for label in CLASSES:
            tmpmap[label] = label

    # load the scoring map for research version
    #
    else:
        tmpmap = nft.load_parameters(pfile, nec.PARAM_MAP)
        if tmpmap == None:
            print(
                "Error: %s (line: %s) %s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    ndt.__NAME__,
                    "error loading the scoring map",
                    pfile,
                )
            )
            sys.exit(os.EX_SOFTWARE)

    # convert the map:
    #  note that both versions use the map
    #
    scmap = nft.generate_map(tmpmap)
    if scmap == None:
        print(
            "Error: %s (line: %s) %s: error converting the map"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        print(tmpmap)
        sys.exit(os.EX_SOFTWARE)

    # create the output directory and the output summary file
    #
    print(" ... creating the output directory ...")
    if nft.make_dir(odir) == False:
        print(
            "Error: %s (line: %s) %s: error creating output directory (%s)"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__, odir)
        )
        sys.exit(os.EX_SOFTWARE)

    fname = nft.concat_names(odir, NEDC_SUMMARY_FILE)
    fp = nft.make_fp(fname)

    # print the header of the summary file showing the relevant information
    #
    fp.write(
        "%s%s%s" % (NEDC_EVAL_SEP, nft.DELIM_NEWLINE, NEDC_VERSION)
        + nft.DELIM_NEWLINE
        + nft.DELIM_NEWLINE
    )
    fp.write(" File: %s" % fname + nft.DELIM_NEWLINE)
    fp.write(" Date: %s" % time.strftime("%c") + nft.DELIM_NEWLINE + nft.DELIM_NEWLINE)
    fp.write(" Data:" + nft.DELIM_NEWLINE)
    fp.write("  Ref: %s" % fname_ref + nft.DELIM_NEWLINE)
    fp.write("  Hyp: %s" % fname_hyp + nft.DELIM_NEWLINE + nft.DELIM_NEWLINE)

    # execute NIST scoring if NIST option used
    #
    if args.nist is not False:
        print(" ... executing NIST ATWV scoring ...")
        fp.write(
            "%s\n%s\n\n"
            % (NEDC_EVAL_SEP, ("NIST ATWV Scoring Summary (f4de_3.3.1):").upper())
        )

        # pass the original file list to the NIST software
        #
        status = nnist.run(reflist, hyplist, scmap, nist_f4de, odir, NEDC_NIST_FILE, fp)
        if status == False:
            print(
                "Error: %s (line: %s) %s: error in NIST scoring"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            sys.exit(os.EX_SOFTWARE)

    # execute dp alignment scoring
    #
    print(" ... executing NEDC DP Alignment scoring ...")
    fp.write(
        "%s\n%s\n\n"
        % (NEDC_EVAL_SEP, ("NEDC DP Alignment Scoring Summary (v4.0.0):").upper())
    )
    fname = nft.concat_names(odir, NEDC_DPALIGN_FILE)
    status = ndpalign.run(ref_anns, hyp_anns, scmap, nedc_dpalign, odir, fname, fp)
    if status == False:
        print(
            "Error: %s (line: %s) %s: error in DPALIGN scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        sys.exit(os.EX_SOFTWARE)

    # execute NEDC epoch-based scoring
    #
    print(" ... executing NEDC Epoch scoring ...")
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, "NEDC Epoch Scoring Summary (v4.0.0):"))
    fname = nft.concat_names(odir, NEDC_EPOCH_FILE)
    status = nepoch.run(ref_anns, hyp_anns, scmap, nedc_epoch, odir, fname, fp)
    if status == False:
        print(
            "Error: %s (line: %s) %s: error in EPOCH scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        sys.exit(os.EX_SOFTWARE)

    # execute overlap scoring
    #
    print(" ... executing NEDC Overlap scoring ...")
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, "NEDC Overlap Scoring Summary (v4.0.0):"))
    fname = nft.concat_names(odir, NEDC_OVLP_FILE)
    status = novlp.run(ref_anns, hyp_anns, scmap, nedc_ovlp, odir, fname, fp)
    if status == False:
        print(
            "Error: %s (line: %s) %s: error in OVLP scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        sys.exit(os.EX_SOFTWARE)

    # execute time-aligned event scoring
    #
    print(" ... executing NEDC Time-Aligned Event scoring ...")
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, "NEDC TAES Scoring Summary (v4.0.0):"))
    fname = nft.concat_names(odir, NEDC_TAES_FILE)
    status = ntaes.run(ref_anns, hyp_anns, scmap, nedc_taes, odir, fname, fp)
    if status == False:
        print(
            "Error: %s (line: %s) %s: error in TAES scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        sys.exit(os.EX_SOFTWARE)

    # execute ira scoring if using research version
    #
    if args.competition is False:
        print(" ... executing NEDC IRA scoring ...")
        fp.write(
            "%s\n%s\n\n"
            % (NEDC_EVAL_SEP, "NEDC Inter-Rater Agreement Summary (v4.0.0):")
        )
        nedc_ira = nft.load_parameters(pfile, nira.NEDC_IRA)
        status = nira.run(ref_anns, hyp_anns, scmap, nedc_ira, odir, fp)
        if status == False:
            print(
                "Error: %s (line: %s) %s: error in IRA scoring"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            sys.exit(os.EX_SOFTWARE)

    # print the final message to the summary file, close it and exit
    #
    print(" ... done ...")
    fp.write(
        "%s\nNEDC EEG Eval Successfully Completed on %s\n%s\n"
        % (NEDC_EVAL_SEP, time.strftime("%c"), NEDC_EVAL_SEP)
    )

    # close the output file
    #
    fp.close()

    # end of main
    #
    sys.exit(os.EX_OK)


#
# end of main

# begin gracefully
#
if __name__ == "__main__":
    main(sys.argv[0:])

#
# end of file
