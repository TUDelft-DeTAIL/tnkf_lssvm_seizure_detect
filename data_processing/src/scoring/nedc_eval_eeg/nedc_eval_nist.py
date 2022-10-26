#!/usr/bin/env python
#
# file: $NEDC_NFC/python/nedc_eval_tools/nedc_eval_nist.py
#
# revision history:
#  20200813 (LV): updated for rehaul of nedc_eval_eeg
#  20170815 (JP): added another metric: prevalence
#  20170812 (JP): changed the divide by zero checks
#  20170716 (JP): upgraded to using the new annotation tools
#  20170709 (JP): refactored code for the new environment
#  20170702 (JP): added summary scoring; revamped derived metrics
#  20170622 (JP): rewritten to conform to standards
#  20170527 (JP): cosmetic revisions
#  20161230 (SL): revision for standards
#  20160627 (SZ): initial version
#
# usage:
#  import nedc_eval_nist as nnist
#
# This file contains Python code that interfaces our scoring software
# to the NIST KWS scoring software
# ------------------------------------------------------------------------------

# import required system modules
#
import os
import sys
import re
from collections import OrderedDict
import math

# import required NEDC modules
#
import nedc_ann_tools as nat
import nedc_debug_tools as ndt
import nedc_file_tools as nft

# ------------------------------------------------------------------------------
#
# define important constants
#
# ------------------------------------------------------------------------------

# set the filename using basename
#
__FILE__ = os.path.basename(__file__)

# define paramter file constants
#
NIST_F4DE = "NIST_F4DE"

# ------------------------------------------------------------------------------
#
# functions are listed here
#
# ------------------------------------------------------------------------------

# declare a global debug object so we can use it in functions
#
dbgl = ndt.Dbgl()

# method: run
#
# arguments:
#  reflist: the reference file list
#  hyplist: the hypothesis file list
#  mapping: a mapping used to collapse classes during scoring
#  nist_f4de: the NIST scoring algorithm parameters
#  odir: the output directory
#  rfile: the results file (written in odir)
#  fp: a pointer to the output summary file
#
# return: a boolean value indicating status
#
# This method runs the NIST scoring software by:
#  (1) creating the necessary inputs
#  (2) running NIST scoring
#  (3) retrieving the results
#
def run(reflist, hyplist, mapping, nist_f4de, odir, rfile, fp):

    # display an informational message
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: running epoch scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    # define local variables
    #
    status = True
    nnist = NISTF4DE(nist_f4de)

    # create the output directory
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: creating output directory"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    odir = nft.concat_names(odir, nnist.output_directory_d)
    status = nft.make_dir(odir)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error creating directory (%s)"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__, odir)
        )
        return False

    # create the necessary inputs to run the NIST scoring
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: creating inputs" % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    status = nnist.create_input(reflist, hyplist, mapping, odir)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error creating input data"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # run the NIST scoring
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: run the nist scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    status = nnist.init_score(mapping)
    status = nnist.score(odir)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error during scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # fetch the results from the NIST output files
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: fetch the results"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    fname_bsum = nnist.get_ofilename(odir)

    status = nnist.get_results(fname_bsum, mapping)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error during scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # compute performance
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: compute performance"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    status = nnist.compute_performance()
    if status == None:
        print(
            "Error: %s (line: %s):%s: error compute performance"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # collect information for scoring and display
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: displaying results"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    status = nnist.display_results(fp)
    if status == False:
        print(
            "Error: %s (line: %s) %s: error displaying results"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # exit gracefully
    #
    return status


#
# end of function

# ------------------------------------------------------------------------------
#
# classes are listed here
#
# ------------------------------------------------------------------------------

# class: NISTF4DE
#
# This class contains methods to generate input files for NIST scoring and\
# generate output file.
#
class NISTF4DE:

    # --------------------------------------------------------------------------
    #
    # static data declarations
    #
    # --------------------------------------------------------------------------

    # define static variables for debug and verbosity
    #
    dbgl_d = ndt.Dbgl()
    vrbl_d = ndt.Vrbl()

    # method: NISTF4DE::constructor
    #
    # arguments: none
    #
    # return: none
    #
    def __init__(self, params):

        # create class data
        #
        NISTF4DE.__CLASS_NAME__ = self.__class__.__name__

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: scoring files"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # decode the parameters passed from the parameter file
        #
        self.koefcorrect_d = float(params["koefcorrect"])
        self.koefincorrect_d = float(params["koefincorrect"])
        self.delta_d = float(params["delta"])
        self.probterm_d = float(params["probterm"])

        self.fname_kwslist_d = params["fname_kwslist"]
        self.fname_kwlist_d = params["fname_kwlist"]
        self.fname_rttm_d = params["fname_rttm"]
        self.fname_ecf_d = params["fname_ecf"]
        self.fname_bsum_d = params["fname_bsum"]
        self.fname_log_d = params["fname_log"]
        self.output_directory_d = params["output_directory"]
        self.basename_d = params["basename"]
        self.command_d = params["command"]

        # declare a variable to hold a permuted map
        #
        self.pmap_d = {}

        # declare a duration parameter used to calculate the false alarm rate:
        #  we need to know the total duration of the data in secs of each
        #  file for NIST scoreing and the total duration for
        #  false alarm computations
        #
        self.fdur_d = []
        self.total_dur_d = float(0)

        # declare parameters to track errors:
        #  all algorithms should track the following per label:
        #   substitutions, deletions, insertions, hits, misses
        #   and false alarms.
        #
        self.tp_d = {}
        self.tn_d = {}
        self.fp_d = {}
        self.fn_d = {}

        self.tgt_d = {}
        self.hit_d = {}
        self.mis_d = {}
        self.fal_d = {}
        self.ins_d = {}
        self.del_d = {}

        # additional derived data:
        #  we use class data to store a number of statistical measures
        #
        self.tpr_d = {}
        self.tnr_d = {}
        self.ppv_d = {}
        self.npv_d = {}
        self.fnr_d = {}
        self.fpr_d = {}
        self.fdr_d = {}
        self.for_d = {}
        self.acc_d = {}
        self.msr_d = {}
        self.prv_d = {}
        self.f1s_d = {}
        self.mcc_d = {}
        self.flr_d = {}

        # declare parameters to compute summaries
        #
        self.sum_tp_d = int(0)
        self.sum_tn_d = int(0)
        self.sum_fp_d = int(0)
        self.sum_fn_d = int(0)

        self.sum_tgt_d = int(0)
        self.sum_hit_d = int(0)
        self.sum_mis_d = int(0)
        self.sum_fal_d = int(0)
        self.sum_ins_d = int(0)
        self.sum_del_d = int(0)

        # additional derived data:
        #  we use class data to store a number of statistical measures
        #
        self.sum_tpr_d = float(0)
        self.sum_tnr_d = float(0)
        self.sum_ppv_d = float(0)
        self.sum_npv_d = float(0)
        self.sum_fnr_d = float(0)
        self.sum_fpr_d = float(0)
        self.sum_fdr_d = float(0)
        self.sum_for_d = float(0)
        self.sum_acc_d = float(0)
        self.sum_msr_d = float(0)
        self.sum_prv_d = float(0)
        self.sum_f1s_d = float(0)
        self.sum_mcc_d = float(0)
        self.sum_flr_d = float(0)

        # algorithm-specific computed data
        #
        self.twv_d = {}
        self.sum_twv_d = float(0)

    #
    # end of method

    # method: NISTF4DE::init_score
    #
    # arguments:
    #  score_map: a scoring map
    #
    # return: a boolean value indicating status
    #
    # This method initializes parameters used to track errors.
    # We use ordered dictionaries that are initialized in the order
    # labels appear in the scoring map.
    #
    def init_score(self, score_map):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: initializing score"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # initialize global counters:
        #  note that total_dur_d is computed prior to this to interface
        #  to the NIST software, and should not be resset here.
        #

        # initialiaze parameters to track errors:
        #  these are declared as ordered dictionaries organized
        #  in the order of the scoring map
        #
        self.tp_d = OrderedDict()
        self.tn_d = OrderedDict()
        self.fp_d = OrderedDict()
        self.fn_d = OrderedDict()

        self.tgt_d = OrderedDict()
        self.hit_d = OrderedDict()
        self.mis_d = OrderedDict()
        self.fal_d = OrderedDict()
        self.sub_d = OrderedDict()
        self.ins_d = OrderedDict()
        self.del_d = OrderedDict()

        self.tpr_d = OrderedDict()
        self.tnr_d = OrderedDict()
        self.ppv_d = OrderedDict()
        self.npv_d = OrderedDict()
        self.fnr_d = OrderedDict()
        self.fpr_d = OrderedDict()
        self.fdr_d = OrderedDict()
        self.for_d = OrderedDict()
        self.acc_d = OrderedDict()
        self.msr_d = OrderedDict()
        self.prv_d = OrderedDict()
        self.f1s_d = OrderedDict()
        self.mcc_d = OrderedDict()
        self.flr_d = OrderedDict()

        # declare parameters to compute summaries
        #
        self.sum_tp_d = int(0)
        self.sum_tn_d = int(0)
        self.sum_fp_d = int(0)
        self.sum_fn_d = int(0)

        self.sum_tgt_d = int(0)
        self.sum_hit_d = int(0)
        self.sum_mis_d = int(0)
        self.sum_fal_d = int(0)
        self.sum_ins_d = int(0)
        self.sum_del_d = int(0)

        self.sum_tpr_d = float(0)
        self.sum_tnr_d = float(0)
        self.sum_ppv_d = float(0)
        self.sum_npv_d = float(0)
        self.sum_fnr_d = float(0)
        self.sum_fpr_d = float(0)
        self.sum_fdr_d = float(0)
        self.sum_for_d = float(0)
        self.sum_msr_d = float(0)
        self.sum_f1s_d = float(0)
        self.sum_mcc_d = float(0)
        self.sum_flr_d = float(0)

        # declare algorithm-specific paramters
        #
        self.twv_d = OrderedDict()
        self.sum_twv_d = float(0)

        # establish the order of these dictionaries in terms of
        # the scoring map.
        #
        for key in score_map:

            self.tp_d[key] = int(0)
            self.tn_d[key] = int(0)
            self.fp_d[key] = int(0)
            self.fn_d[key] = int(0)

            self.tgt_d[key] = int(0)
            self.hit_d[key] = int(0)
            self.mis_d[key] = int(0)
            self.fal_d[key] = int(0)
            self.ins_d[key] = int(0)
            self.del_d[key] = int(0)

            self.tpr_d[key] = float(0)
            self.tnr_d[key] = float(0)
            self.ppv_d[key] = float(0)
            self.npv_d[key] = float(0)
            self.fnr_d[key] = float(0)
            self.fpr_d[key] = float(0)
            self.fdr_d[key] = float(0)
            self.for_d[key] = float(0)
            self.acc_d[key] = float(0)
            self.msr_d[key] = float(0)
            self.prv_d[key] = float(0)
            self.f1s_d[key] = float(0)
            self.mcc_d[key] = float(0)
            self.flr_d[key] = float(0)

            self.twv_d[key] = float(0)

        # permute the map: we need this in various places
        #
        self.pmap_d = nft.permute_map(score_map)

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::get_ofilename
    #
    # arguments:
    #  odir: output directory
    #
    # return:
    #  fname_bsum: the full pathname of the NIST output file
    #
    # This method returns the path of the NIST output file.
    #
    def get_ofilename(self, odir):
        return nft.concat_names(odir, self.fname_bsum_d)

    # method: NISTF4DE::create_input
    #
    # arguments:
    #  reflist: filelist of reference files
    #  hyplist: filelist of hypothesis files
    #  score_map: list of event names to be scored
    #  odir: output directory
    #
    # return: a boolean value indicating status
    #
    # This method creates the following files required by the NIST
    # scoring software (in this order): (1) *.kwlist.xml, (2) *.rttm.xml,
    # (3) *.kwslist.xml, (4) *.ecf.xml.
    #
    def create_input(self, reflist, hyplist, score_map, odir):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: creating input"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # check the reference and hyp file lists
        #
        num_files_ref = len(reflist)
        num_files_hyp = len(hyplist)

        if num_files_ref < 1 or num_files_hyp < 1 or num_files_ref != num_files_hyp:
            print(
                "Error: %s (line: %s) %s::%s: %s (%d %d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "mistmatched file listsfile list error",
                    num_files_ref,
                    num_files_hyp,
                )
            )
            return False

        # generate unique tags for each filename in the annotation list:
        #  the NIST software needs each 'filename' to be unique.
        #
        tags = self.create_unique_tags(reflist)

        # generate the kwlist file:
        #  note that we apply the class mapping here
        #
        fname_kwlist = nft.concat_names(odir, self.fname_kwlist_d)
        status = self.create_kwlist(fname_kwlist, score_map)
        if status == False:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "kwlist creation error",
                    self.fname_kwlist_d,
                )
            )
            return False

        # generate the rttm file:
        #  we need to permute the map so that lookup is fast
        #
        fname_rttm = nft.concat_names(odir, self.fname_rttm_d)
        pmap = nft.permute_map(score_map)
        self.fdur_d = self.create_rttm(fname_rttm, reflist, tags, pmap)
        if self.fdur_d == None or len(self.fdur_d) == 0:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "rttm creation error",
                    self.fname_rttm_d,
                )
            )
            return False
        self.total_dur_d = sum(self.fdur_d)

        # generate the kwslist file
        #
        fname_kwslist = nft.concat_names(odir, self.fname_kwslist_d)
        status = self.create_kwslist(fname_kwslist, hyplist, tags, score_map, odir)
        if status == False:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "kwlist creation error",
                    self.fname_kwlist_d,
                )
            )
            return False

        # generate the ecf file
        #
        fname_ecf = nft.concat_names(odir, self.fname_ecf_d)
        status = self.create_ecf(
            fname_ecf, reflist, tags, self.fdur_d, self.total_dur_d
        )
        if status == False:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "ecf creation error",
                    self.fname_ecf_d,
                )
            )
            return False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: NISTF4DE::create_unique_tags
    #
    # arguments:
    #  flist: a list of filenames
    #
    # return: a list of unqiue tags
    #
    # This method creates list of tags based on the filename
    # provided. It is assumed that a full pathname is provided,
    # including the directory name. The directory delimiter is replaced
    # with an underscore.
    #
    def create_unique_tags(self, flist):

        # declare an output list
        #
        tags = []

        # loop over list file
        #
        for fname in flist:
            tags.append(fname.replace(nft.DELIM_SLASH, nft.DELIM_USCORE))

        # exit gracefully
        #
        return tags

    #
    # end of method

    # method: NISTF4DE::create_kwlist
    #
    # arguments:
    #  fname: full pathname of the kwlist file
    #  score_map: a mapping used to collapse classes for scoring
    #
    # return: a boolean value indicating the status
    #
    # This method creates a NIST-formatted XML file known
    # as a keyword list file (kwlist).
    #
    def create_kwlist(self, fname, score_map):

        # open the file and write the body tag
        #
        fp = nft.make_fp(fname)
        fp.write(
            '<kwlist ecf_filename="%s" version="01" '
            'language="english" compareNormalize=""'
            ' encoding="UTF-8">' % self.fname_ecf_d + nft.DELIM_NEWLINE
        )

        # loop over the mapping file and write each term
        #
        for key in score_map:
            fp.write(
                '  <kw kwid="term-%(0)s"><kwtext>%(0)s</kwtext></kw>' % {"0": key}
                + nft.DELIM_NEWLINE
            )

        # write end of body tag and close the file
        #
        fp.write("</kwlist>")
        fp.close()

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::create_rttm
    #
    # arguments:
    #  fname: full pathname of the rttm file
    #  flist: a list of filenames for the annotations
    #  tags: a list of unique tags
    #  score_map: a mapping used to collapse classes for scoring
    #
    # return:
    #  fdur: the duration of each annotations file in secs
    #
    # This method creates a NIST-formatted XML file known
    # as an rttm file. It returns the total duration, which is needed
    # at the top of the ECF file and for false alarm calculations.
    #
    def create_rttm(self, fname, flist, tags, score_map):

        # initialize local variable
        #
        fdur = []
        counter = 0

        # open the file
        #
        fp = nft.make_fp(fname)

        # loop over the list
        #
        for fname_i in flist:

            # generate the list of terms
            #
            events = self.create_terms(fname_i, score_map)
            if events == None:
                print(
                    "Error: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "error creating terms",
                        fname_i,
                    )
                )
                return None

            # loop over list files and write to the output file
            #
            base = os.path.splitext(tags[counter])[0]

            for i in range(len(events)):
                key = next(iter(events[i][2]))
                fp.write(
                    "LEXEME %s 1 %12.4f %12.4f %s lex <NA> <NA>"
                    % (
                        base,
                        events[i][0],
                        float(events[i][1]) - float(events[i][0]),
                        key,
                    )
                    + nft.DELIM_NEWLINE
                )

            # save duration of each file
            #
            fdur.append(float(events[-1][1]))
            counter += 1

        # close the file
        #
        fp.close()

        # exit gracefully
        #
        return fdur

    #
    # end of method

    # method: NISTF4DE::create_kwslist
    #
    # arguments:
    #  fname: full pathname of the kwslist file
    #  flist: a list of filenames for the hypotheses
    #  tags: a list of unique tags
    #  score_map: a mapping used to collapse classes for scoring
    #  odir: output directory
    #
    # return: a boolean value indicating the status
    #
    # This method creates a NIST-formatted XML file known as a kwslist file.
    #
    def create_kwslist(self, fname, flist, tags, score_map, odir):

        # declare local variables:
        #  tmp is used to accumulate per-term output
        #
        tmp = OrderedDict()

        # generate a permuted map to make lookups easy
        #
        pmap = nft.permute_map(score_map)

        # create a temporary file for each event
        #
        for key in score_map:

            # create a dictionary of tmp file names
            #
            tmp[key] = []
            tmp[key].append(
                str(
                    '  <detected_kwlist kwid="term-%s" '
                    'search_time="999.0" oov_count="0">' % key
                )
            )

        # loop over filenames
        #
        counter = int(0)
        for fname_i in flist:

            # generate a list of terms
            #
            events = self.create_terms(fname_i, pmap)
            if events == None:
                print(
                    "Error: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "error creating terms",
                        fname_i,
                    )
                )
                return False

            # loop over the events and print them to the output file
            #
            base = os.path.splitext(tags[counter])[0]
            for i in range(len(events)):
                key = next(iter(events[i][2]))
                tmp[key].append(
                    str(
                        '    <kw file="%s" channel="1" '
                        'tbeg="%.4f" dur="%.4f" '
                        'score="%.4f" decision="YES"/>'
                        % (
                            base,
                            float(events[i][0]),
                            float(events[i][1]) - float(events[i][0]),
                            float(events[i][2][key]),
                        )
                    )
                )
            counter += 1

        # open the kwslist file, write the data, and close the file
        #
        fp = nft.make_fp(fname)
        fp.write(
            '<kwslist kwlist_filename="%s" language="english" '
            'system_id="">' % self.fname_kwlist_d
            + nft.DELIM_NEWLINE
            + nft.DELIM_NEWLINE
        )
        for key in tmp:
            for content in tmp[key]:
                fp.write(content + nft.DELIM_NEWLINE)
            fp.write("  </detected_kwlist>" + nft.DELIM_NEWLINE + nft.DELIM_NEWLINE)
        fp.write("</kwslist>")
        fp.close()

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::create_terms
    #
    # arguments:
    #  fname: full pathname of the file
    #  pmap: a permuted map used to map events to scoring classes
    #
    # return:
    #  events: a data structure containing start/stop_times and events labels
    #
    # This method reads events from a file and maps them.
    #
    def create_terms(self, fname, pmap=None):

        # load the labels
        #
        ann = nat.Ann()
        if ann.load(fname) == None:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "error loading references",
                    fname,
                )
            )
            return None

        # get the events
        #
        events = ann.get()
        if events == None:
            print(
                "Error: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "error loading references",
                    fname,
                )
            )
            return None

        # map the events
        #
        if pmap != None:
            events_new = []
            for i in range(len(events)):
                events_new.append(events[i])
                for key in events[i][2]:
                    events_new[i][2][pmap[key].lower()] = events[i][2][key]
            return events_new

        # else: exit gracefully
        #
        return events

    #
    # end of method

    # method: NISTF4DE::create_ecf
    #
    # arguments:
    #  fname: full pathname of the ecf file
    #  flist: a list of filenames for the annotations
    #  tags: a list of unique tags
    #  fdur: the duration of each file in secs
    #  total_dur: the total duration in secs of the annotations
    #
    # return: a boolean value indicating the status
    #
    # This method creates a NIST-formatted XML file known
    # as an ECF file.
    #
    def create_ecf(self, fname, flist, tags, fdur, total_dur):

        # open the file
        #
        fp = nft.make_fp(fname)

        # write total duration
        #
        fp.write(
            '<ecf source_signal_duration="%.4f" language="english" '
            'version="">' % total_dur + nft.DELIM_NEWLINE
        )

        # loops over all entries in the list
        #
        counter = 0
        for fname_i in flist:
            fp.write(
                '  <excerpt audio_filename="%s" channel="1" '
                'tbeg="%.4f" dur="%.4f" source_type="bnews"/>'
                % (tags[counter], float(0), float(fdur[counter]))
                + nft.DELIM_NEWLINE
            )
            counter += 1

        # clean up by writing the last line and closing the file
        #
        fp.write("</ecf>")
        fp.close()

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::score
    #
    # arguments:
    #  odir: output directory
    #
    # return: a boolean value indicating status
    #
    # This method sets up a command and runs NIST scoring.
    #
    def score(self, odir):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: scoring files"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # path to input files
        #
        fname_ecf = nft.concat_names(odir, self.fname_ecf_d)
        fname_kwlist = nft.concat_names(odir, self.fname_kwlist_d)
        fname_kwslist = nft.concat_names(odir, self.fname_kwslist_d)
        fname_rttm = nft.concat_names(odir, self.fname_rttm_d)
        fname_log = nft.concat_names(odir, self.fname_log_d)
        odir_i = nft.concat_names(odir, self.basename_d)

        # run KWSEval
        #
        cmd = (
            "KWSEval -e %s -r %s -t %s -s %s -S %s -p %s -k %s -K %s -o -b \
		 -d -c -f %s"
            % (
                fname_ecf,
                fname_rttm,
                fname_kwlist,
                fname_kwslist,
                self.delta_d,
                self.probterm_d,
                self.koefcorrect_d,
                self.koefincorrect_d,
                odir_i,
            )
        )

        # create a shell file
        #
        fname_cmd = nft.concat_names(odir, self.command_d)
        fp = nft.make_fp(fname_cmd)
        fp.write(cmd)
        fp.close()

        # run the command
        #
        rvalue = os.system("sh %s > %s" % (fname_cmd, fname_log))

        # exit gracefully
        #
        if rvalue >= 0:
            return True
        else:
            return False

    #
    # end of method

    # method: NISTF4DE::get_results
    #
    # arguments:
    #  fname: path to the NIST "bsum" file
    #  score_map: the class scoring map
    #
    # return: a boolean value indicating status
    #
    # This method reads a NIST-formatted results file and extracts
    # the necessary scoring information that we use to display results.
    # The results are stored in class data.
    #
    def get_results(self, fname, score_map):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: getting results"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # read the file into memory
        #
        lines = [line.rstrip(nft.DELIM_NEWLINE) for line in open(fname)]

        # loop over the contents and extract the necessary information
        #
        ind1 = nft.first_substring(lines, "Keyword")
        ind2 = nft.first_substring(lines, "Summary  Totals")

        for i in range(ind1, ind2):

            # split the line into parts
            #
            parts = (re.sub(r"\s+", "", lines[i])).split("|")

            # grab hits, misses, false alarms and twv since
            # these are reported directly in the NIST report
            #
            key = parts[1]
            if len(parts[2]) > 0:
                self.tgt_d[key] = int(parts[2])
                self.hit_d[key] = int(parts[3])
                self.mis_d[key] = int(parts[5])
                self.fal_d[key] = int(parts[4])
                self.twv_d[key] = float(parts[6])
            else:
                self.tgt_d[key] = int(0)
                self.hit_d[key] = int(0)
                self.mis_d[key] = int(0)
                self.fal_d[key] = int(0)
                self.twv_d[key] = float(0)

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::compute_performance
    #
    # arguments: none
    #
    # return: a boolean value indicating status
    #
    # This method computes a number of standard measures of performance. The
    # terminology follows these references closely:
    #
    #  https://en.wikipedia.org/wiki/Confusion_matrix
    #  https://en.wikipedia.org/wiki/Precision_and_recall
    #  http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
    #
    # The approach taken here for a multi-class problem is to convert the
    # NxN matrix to a 2x2 for each label, and then do the necessary
    # computations.
    # c
    # Note that NIST does not give us a confusion matrix (sub_d).
    #
    def compute_performance(self):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: computing the performance"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # check for a zero count
        #
        num_total_ref_events = sum(self.tgt_d.values())
        if num_total_ref_events == 0:
            print(
                "Error: %s (line: %s) %s::%s: %s (%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "number of events is zero",
                    num_total_ref_events,
                )
            )
            # return None

        # ----------------------------------------------------------------------
        # (1) The first block of parameters count events such as hits,
        #     missses and false alarms. The NIST algorithm provides
        #     these directly.
        #
        for key1 in self.hit_d:
            self.ins_d[key1] = self.fal_d[key1]
            self.del_d[key1] = self.mis_d[key1]

        # ----------------------------------------------------------------------
        # (2) The second block of computations are the derived measures
        #     such as sensitivity. These are computed using a three-step
        #     approach:
        #      (2.2) compute true positives, etc. (tp, tn, fp, fn)
        #      (2.3) compute the derived measures (e.g., sensitivity)
        #
        # loop over all labels
        #
        for key1 in self.hit_d:

            # ------------------------------------------------------------------
            # (2.2) The NIST algorithm outputs hits, misses and false alarms
            #       directly. These must be converted to (tp, tn, fp, fn).
            #
            # compute true positives (tp): copy hits
            #
            self.tp_d[key1] = self.hit_d[key1]

            # compute true negatives (tn):
            #  sum the hits that are not the current label
            #
            tn_sum = int(0)
            for key2 in self.hit_d:
                if key1 != key2:
                    tn_sum += self.hit_d[key2]
            self.tn_d[key1] = tn_sum

            # compute false positives (fp): copy false alarms
            #
            self.fp_d[key1] = self.fal_d[key1]

            # compute false negatives (fn): copy misses
            #
            self.fn_d[key1] = self.mis_d[key1]

            # check the health of the confusion matrix
            #
            tp = self.tp_d[key1]
            fp = self.fp_d[key1]
            tn = self.tn_d[key1]
            fn = self.fn_d[key1]
            tdur = self.total_dur_d

            if (
                ((tp + fn) == 0)
                or ((fp + tn) == 0)
                or ((tp + fp) == 0)
                or ((fn + tn) == 0)
            ):
                print(
                    "Warning: %s (line: %s) %s::%s: %s (%d %d %d %d)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "divide by zero",
                        tp,
                        fp,
                        tn,
                        fn,
                    )
                )
            elif round(tdur, ndt.MAX_PRECISION) == 0:
                print(
                    "Warning: %s (line: %s) %s::%s: duration is zero (%f)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        tdur,
                    )
                )

            # (2.3) compute derived measures
            #
            if (tp + fn) != 0:
                self.tpr_d[key1] = float(self.tp_d[key1]) / float(tp + fn)
            else:
                self.tpr_d[key1] = float(0)

            if (tn + fp) != 0:
                self.tnr_d[key1] = float(self.tn_d[key1]) / float(tn + fp)
            else:
                self.tnr_d[key1] = float(0)

            if (tp + fp) != 0:
                self.ppv_d[key1] = float(self.tp_d[key1]) / float(tp + fp)
            else:
                self.ppv_d[key1] = float(0)

            if (tn + fn) != 0:
                self.npv_d[key1] = float(self.tn_d[key1]) / float(tn + fn)
            else:
                self.npv_d[key1] = float(0)

            self.fnr_d[key1] = 1 - float(self.tpr_d[key1])
            self.fpr_d[key1] = 1 - float(self.tnr_d[key1])
            self.fdr_d[key1] = 1 - float(self.ppv_d[key1])
            self.for_d[key1] = 1 - float(self.npv_d[key1])

            if (tp + tn + fp + fn) != 0:
                self.acc_d[key1] = float(self.tp_d[key1] + self.tn_d[key1]) / (
                    tp + tn + fp + fn
                )
                self.prv_d[key1] = float(self.tp_d[key1] + self.fn_d[key1]) / (
                    tp + tn + fp + fn
                )
            else:
                self.acc_d[key1] = float(0)
                self.prv_d[key1] = float(0)

            self.msr_d[key1] = 1 - self.acc_d[key1]

            # compute the f1 score:
            #  this has to be done after sensitivity and prec are computed
            #
            f1s_denom = float(self.ppv_d[key1] + self.tpr_d[key1])
            if round(f1s_denom, ndt.MAX_PRECISION) == 0:
                print(
                    "Warning: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "f ratio divide by zero",
                        key1,
                    )
                )
                self.f1s_d[key1] = float(0)
            else:
                self.f1s_d[key1] = 2.0 * self.ppv_d[key1] * self.tpr_d[key1] / f1s_denom

            # compute the mcc score:
            #  this has to be done after sensitivity and prec are computed
            #
            mcc_denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
            mcc_num = (tp * tn) - (fp * fn)
            if round(mcc_denom, ndt.MAX_PRECISION) == 0:
                print(
                    "Warning: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "mcc ration divide by zero",
                        key1,
                    )
                )
                self.mcc_d[key1] = float(0)
            else:
                self.mcc_d[key1] = mcc_num / math.sqrt(mcc_denom)

            # compute the false alarm rate
            #
            if round(tdur, ndt.MAX_PRECISION) == 0:
                print(
                    "Warning: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NISTF4DE.__CLASS_NAME__,
                        ndt.__NAME__,
                        "zero duration",
                        key1,
                    )
                )
                self.flr_d[key1] = float(0)
            else:
                self.flr_d[key1] = float(fp) / tdur * (60 * 60 * 24)

        # ----------------------------------------------------------------------
        # (3) the third block of parameters are the summary values
        #
        self.sum_tgt_d = sum(self.tgt_d.values())
        self.sum_hit_d = sum(self.hit_d.values())
        self.sum_mis_d = sum(self.mis_d.values())
        self.sum_fal_d = sum(self.fal_d.values())
        self.sum_ins_d = sum(self.ins_d.values())
        self.sum_del_d = sum(self.del_d.values())

        self.sum_tp_d = sum(self.tp_d.values())
        self.sum_tn_d = sum(self.tn_d.values())
        self.sum_fp_d = sum(self.fp_d.values())
        self.sum_fn_d = sum(self.fn_d.values())

        if (self.sum_tp_d + self.sum_fn_d) != 0:
            self.sum_tpr_d = float(self.sum_tp_d) / float(self.sum_tp_d + self.sum_fn_d)
        else:
            self.sum_tpr_d = float(0)

        if (self.sum_tn_d + self.sum_fp_d) != 0:
            self.sum_tnr_d = float(self.sum_tn_d) / float(self.sum_tn_d + self.sum_fp_d)
        else:
            self.sum_tnr_d = float(0)

        if (self.sum_tp_d + self.sum_fp_d) != 0:
            self.sum_ppv_d = float(self.sum_tp_d) / float(self.sum_tp_d + self.sum_fp_d)
        else:
            self.sum_ppv_d = float(0)

        if (self.sum_tn_d + self.sum_fn_d) != 0:
            self.sum_npv_d = float(self.sum_tn_d) / float(self.sum_tn_d + self.sum_fn_d)
        else:
            self.sum_npv_d = float(0)

        self.sum_fnr_d = 1 - float(self.sum_tpr_d)
        self.sum_fpr_d = 1 - float(self.sum_tnr_d)
        self.sum_fdr_d = 1 - float(self.sum_ppv_d)
        self.sum_for_d = 1 - float(self.sum_npv_d)

        if (self.sum_tp_d + self.sum_tn_d + self.sum_fp_d + self.sum_fn_d) != 0:
            self.sum_acc_d = float(self.sum_tp_d + self.sum_tn_d) / (
                float(self.sum_tp_d + self.sum_tn_d + self.sum_fp_d + self.sum_fn_d)
            )
            self.sum_prv_d = float(self.sum_tp_d + self.sum_fn_d) / (
                float(self.sum_tp_d + self.sum_tn_d + self.sum_fp_d + self.sum_fn_d)
            )
        else:
            self.sum_acc_d = float(0)
            self.sum_prv_d = float(0)

        self.sum_msr_d = 1 - self.sum_acc_d

        # compute the f1 score
        #
        f1s_denom = self.sum_ppv_d + self.sum_tpr_d
        if round(f1s_denom, ndt.MAX_PRECISION) == 0:
            print(
                "Warning: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "f ratio divide by zero",
                    "summary",
                )
            )
            self.sum_f1s_d = float(0)
        else:
            self.sum_f1s_d = 2.0 * self.sum_ppv_d * self.sum_tpr_d / f1s_denom

        # compute the mcc score:
        #  this has to be done after sensitivity and prec are computed
        #
        sum_mcc_denom = (
            (self.sum_tp_d + self.sum_fp_d)
            * (self.sum_tp_d + self.sum_fn_d)
            * (self.sum_tn_d + self.sum_fp_d)
            * (self.sum_tn_d + self.sum_fn_d)
        )
        sum_mcc_num = (self.sum_tp_d * self.sum_tn_d) - (self.sum_fp_d * self.sum_fn_d)
        if round(sum_mcc_denom, ndt.MAX_PRECISION) == 0:
            print(
                "Warning: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "mcc ratio divide by zero",
                    "summary",
                )
            )
            self.sum_mcc_d = float(0)
        else:
            self.sum_mcc_d = sum_mcc_num / math.sqrt(sum_mcc_denom)

        # compute the false alarm rate
        #
        if round(self.total_dur_d, ndt.MAX_PRECISION) == 0:
            print(
                "Warning: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NISTF4DE.__CLASS_NAME__,
                    ndt.__NAME__,
                    "zero duration",
                    "summary",
                )
            )
            self.sum_flr_d = float(0)
        else:
            self.sum_flr_d = float(self.sum_fp_d) / self.total_dur_d * (60 * 60 * 24)

        # compute the summary TWV as the average
        #
        self.sum_twv_d = float(sum(self.twv_d.values())) / len(self.twv_d)

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NISTF4DE::display_results
    #
    # arguments:
    #  fp: output file pointer
    #
    # return: a boolean value indicating status
    #
    # This method displays all the results in output report.
    #
    def display_results(self, fp):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: displaying results to output file"
                % (__FILE__, ndt.__LINE__, NISTF4DE.__CLASS_NAME__, ndt.__NAME__)
            )

        # write per label header
        #
        fp.write(("Per Label Results:" + nft.DELIM_NEWLINE).upper())
        fp.write(nft.DELIM_NEWLINE)

        # per label results: loop over all classes
        #
        for key in self.hit_d:
            fp.write((" Label: %s" % key + nft.DELIM_NEWLINE).upper())
            fp.write(nft.DELIM_NEWLINE)

            fp.write(
                "   %30s: %12.0f   <**" % ("Targets", float(self.tgt_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f   <**" % ("Hits", float(self.hit_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f   <**" % ("Misses", float(self.mis_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f   <**" % ("False Alarms", float(self.fal_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f" % ("Insertions", float(self.ins_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f" % ("Deletions", float(self.del_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(nft.DELIM_NEWLINE)

            fp.write(
                "   %30s: %12.0f" % ("True Positives (TP)", float(self.tp_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f" % ("True Negatives (TN)", float(self.tn_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f" % ("False Positives (FP)", float(self.fp_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.0f" % ("False Negatives (FN)", float(self.fn_d[key]))
                + nft.DELIM_NEWLINE
            )
            fp.write(nft.DELIM_NEWLINE)

            fp.write(
                "   %30s: %12.4f%%"
                % ("Sensitivity (TPR, Recall)", self.tpr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%" % ("Specificity (TNR)", self.tnr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%" % ("Precision (PPV)", self.ppv_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%"
                % ("Negative Pred. Value (NPV)", self.npv_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%" % ("Miss Rate (FNR)", self.fnr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%"
                % ("False Positive Rate (FPR)", self.fpr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%"
                % ("False Discovery Rate (FDR)", self.fdr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%"
                % ("False Omission Rate (FOR)", self.for_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%" % ("Accuracy", self.acc_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%"
                % ("Misclassification Rate", self.msr_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f%%" % ("Prevalence", self.prv_d[key] * 100.0)
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f" % ("F1 Score (F Ratio)", self.f1s_d[key])
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f" % ("Matthews (MCC)", self.mcc_d[key])
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f per 24 hours" % ("False Alarm Rate", self.flr_d[key])
                + nft.DELIM_NEWLINE
            )
            fp.write(
                "   %30s: %12.4f   <**" % ("TWV", self.twv_d[key]) + nft.DELIM_NEWLINE
            )
            fp.write(nft.DELIM_NEWLINE)

        # display a summary of the results
        #
        fp.write(("Summary:" + nft.DELIM_NEWLINE).upper())
        fp.write(nft.DELIM_NEWLINE)

        # display the standard derived values
        #
        fp.write(
            "   %30s: %12.0f" % ("Total", float(self.sum_tgt_d)) + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("Hits", float(self.sum_hit_d)) + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("Misses", float(self.sum_mis_d)) + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("False Alarms", float(self.sum_fal_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("Insertions", float(self.sum_ins_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("Deletions", float(self.sum_del_d)) + nft.DELIM_NEWLINE
        )
        fp.write(nft.DELIM_NEWLINE)

        fp.write(
            "   %30s: %12.0f" % ("True Positives(TP)", float(self.sum_tp_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f" % ("False Positives (FP)", float(self.sum_fp_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(nft.DELIM_NEWLINE)

        fp.write(
            "   %30s: %12.4f%%" % ("Sensitivity (TPR, Recall)", self.sum_tpr_d * 100.0)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f%%" % ("Miss Rate (FNR)", self.sum_fnr_d * 100.0)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f%%" % ("Accuracy", self.sum_acc_d * 100.0)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f%%" % ("Misclassification Rate", self.sum_msr_d * 100.0)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f%%" % ("Prevalence", self.sum_prv_d * 100.0)
            + nft.DELIM_NEWLINE
        )
        fp.write("   %30s: %12.4f" % ("F1 Score", self.sum_f1s_d) + nft.DELIM_NEWLINE)
        fp.write(
            "   %30s: %12.4f" % ("Matthews (MCC)", self.sum_mcc_d) + nft.DELIM_NEWLINE
        )
        fp.write(nft.DELIM_NEWLINE)

        # display the overall false alarm rate
        #
        fp.write(
            "   %30s: %12.4f secs" % ("Total Duration", self.total_dur_d)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f events" % ("Total False Alarms", self.sum_fp_d)
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.4f per 24 hours" % ("Total False Alarm Rate", self.sum_flr_d)
            + nft.DELIM_NEWLINE
        )
        fp.write(nft.DELIM_NEWLINE)

        # display the actual twv
        #
        fp.write(
            "   %30s: %12.4f   <**" % ("Average TWV", self.sum_twv_d)
            + nft.DELIM_NEWLINE
        )
        fp.write(nft.DELIM_NEWLINE)

        # exit gracefully
        #
        return True

    #
    # end of method


# end of file
#
