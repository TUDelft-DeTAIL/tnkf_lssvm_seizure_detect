#!/usr/bin/env python

# file: $NEDC_NFC/class/python/nedc_eval_tools/nedc_eval_ovlp.py
#
# revision history:
#  20200813 (LV): updated for rehaul of nedc_eval_eeg
#  20170815 (JP): added another metric: prevalence
#  20170812 (JP): changed the divide by zero checks
#  20170716 (JP): upgraded to using the new annotation tools
#  20170710 (JP): refactored code
#  20170702 (JP): added summary scoring; revamped the derived metrics
#  20170615 (JP): initial version
#
# usage:
#  import nedc_eval_ovlp as novlp
#
# This file implements NEDC's overlap scoring algorithm. This algorithm is
# described here:
#
#  Wilson, Scheuer, Plummer, Young, & Pacia. (2003). Seizure detection:
#  Correlation of human experts. Clinical Neurophysiology, 114(11), 2156-2164.
#
# A synposis is as follows:
#
#  Inter-reader sensitivity and false positive rate are calculated
#  with the traditional algorithm described in Section 1. Given
#  Readers X and Y, SensitivityXY (the sensitivity of Reader X with
#  respect to Reader Y) is given by the number of events marked by Y
#  that are overlapped by one or more events marked by X divided by the
#  number of events marked by Y. FPRateXY is given by the number of events
#  marked by X that do not overlap any event marked by Y divided by
#  the record duration in minutes. Wilson et al. (1996) show how to
#  extend the any-overlap comparison calculations to support perception
#  values, but perception values were not used in these anyoverlap
#  computations since the cost (probably time) to review a false positive
#  seizure is independent of its perception value.
#
# ------------------------------------------------------------------------------

# import required system modules
#
import os
import sys
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
NEDC_OVLP = "NEDC_OVERLAP"

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
#  nedc_ovlp: the NEDC overlap scoring algorithm parameters
#  odir: the output directory
#  rfile: the results file (written in odir)
#  fp: a pointer to the output summary file
#
# return: a boolean value indicating status
#
# This method runs the NEDC overlap scoring algorithm by:
#  (1) loading the annotations
#  (2) scoring them
#  (3) displaying the results
#
def run(reflist, hyplist, mapping, nedc_ovlp, odir, rfile, fp):

    # display an informational message
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: running ovlp scoring"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    # define local variables
    #
    status = True
    novlp = NedcOverlap(nedc_ovlp)

    # load the reference and hyp file lists into memory
    #
    num_files_ref = len(reflist)
    num_files_hyp = len(hyplist)

    if num_files_ref < 1 or num_files_hyp < 1 or num_files_ref != num_files_hyp:
        print(
            "Error: %s (line: %s): %s: file list error (%s %s)"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__, reflist, hyplist)
        )
        return False

    # run overlap scoring
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: scoring files" % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    status = novlp.init_score(mapping)
    status = novlp.score(reflist, hyplist, mapping, rfile)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error during results"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )
        return False

    # compute performance
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: computing performance"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    cnf = novlp.compute_performance()
    if status == None:
        print(
            "Error: %s (line: %s):%s: error computing performance"
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

    status = novlp.display_results(fp)
    if status == False:
        print(
            "Error: %s (line: %s):%s: error displaying results"
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

# class: NedcOverlap
#
# This class contains methods that execute the overlap-based scoring algorithm.
# This approach is very permissive in how it counts correct recognitions.
# It is a popular way to score that is cited extensively in the literature.
#
class NedcOverlap:

    # --------------------------------------------------------------------------
    #
    # static data declarations
    #
    # --------------------------------------------------------------------------

    # define static variables for debug and verbosity
    #
    dbgl_d = ndt.Dbgl()
    vrbl_d = ndt.Vrbl()

    # method: NedcOverlap::constructor
    #
    # arguments: none
    #
    # return: none
    #
    def __init__(self, params):

        # create class data
        #
        NedcOverlap.__CLASS_NAME__ = self.__class__.__name__

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: scoring files"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
            )

        # decode the parameters passed from the parameter file
        # (if we are using this)
        #
        # self.guard_width_d = params['guard_width']
        # self.ndigits_round_d = params['ndigits_round']

        # declare a variable to hold a permuted map
        #
        self.pmap_d = {}

        # declare a duration parameter used to calculate the false alarm rate:
        #  we need to know the total duration of the data in secs
        #
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

        # declare parameters to hold per file output
        #
        self.rfile_d = None

    #
    # end of method

    # method: NedcOverlap::init_score
    #
    # arguments:
    #  score_map: a scoring map
    #
    # return: a boolean value indicating status
    #
    # This method initializes parameters used to track errors.
    # We use dictionaries that are initialized in the order
    # labels appear in the scoring map.
    #
    def init_score(self, score_map):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: initializing score"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
            )

        # initialize global counters
        #
        self.total_dur_d = float(0)

        # initialiaze parameters to track errors:
        #  these are declared as dictionaries organized
        #  in the order of the scoring map
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

        # permute the map: we need this in various places
        #
        self.pmap_d = nft.permute_map(score_map)

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NedcOverlap::score
    #
    # arguments:
    #  files_ref: a reference file list
    #  files_hyp: a hypothesis file list
    #  score_map: a scoring map
    #  rfile: a file that contains per file scoring results
    #
    # return: a boolean value indicating status
    #
    # This method computes a confusion matrix.
    #
    def score(self, files_ref, files_hyp, score_map, rfile):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: scoring files"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
            )

        # declare local variables
        #
        status = True

        # create the results file
        #
        self.rfile_d = nft.make_fp(rfile)

        # loop over all files
        #
        for i, fname in enumerate(files_ref):

            events_ref = files_ref.get(fname, None)
            if events_ref == None:
                print(
                    "Error: %s (line: %s) %s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        ndt.__NAME__,
                        "error getting annotations",
                        fname,
                    )
                )
                return False

            # get the hyp eventss
            #
            events_hyp = files_hyp.get(fname, None)
            if events_hyp == None:
                print(
                    "Error: %s (line: %s) %s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        ndt.__NAME__,
                        "error getting annotations",
                        fname,
                    )
                )
                return False

            # update the total duration
            #
            self.total_dur_d += events_ref[-1][1]

            # map the annotations before scoring:
            #  only extract the first label and convert to a pure list
            #
            ann_ref = []
            for event in events_ref:
                key = next(iter(event[2]))
                ann_ref.append([event[0], event[1], self.pmap_d[key], event[2][key]])

            ann_hyp = []
            for event in events_hyp:
                key = next(iter(event[2]))
                ann_hyp.append([event[0], event[1], self.pmap_d[key], event[2][key]])

            # add this to the confusion matrix
            #
            refo, hypo, hit, mis, fal = self.compute(ann_ref, ann_hyp)
            if refo == None:
                print(
                    "Error: %s (line: %s) %s::%s: %s (%s)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NedcOverlap.__CLASS_NAME__,
                        ndt.__NAME__,
                        "error computing confusions",
                        fname,
                    )
                )
                return False

            # output the files to the per file results file
            #
            self.rfile_d.write("%5d: %s" % (i, fname) + nft.DELIM_NEWLINE)
            self.rfile_d.write(
                "%5s  %s" % (nft.STRING_EMPTY, fname) + nft.DELIM_NEWLINE
            )
            self.rfile_d.write(
                "  Ref: %s" % nft.DELIM_SPACE.join(refo) + nft.DELIM_NEWLINE
            )
            self.rfile_d.write(
                "  Hyp: %s" % nft.DELIM_SPACE.join(hypo) + nft.DELIM_NEWLINE
            )
            self.rfile_d.write(
                "%6s (%s %d  %s %d  %s %d  Total: %d)"
                % (
                    nft.STRING_EMPTY,
                    "Hit:",
                    hit,
                    "Miss:",
                    mis,
                    "False Alarms:",
                    fal,
                    hit + mis + fal,
                )
                + nft.DELIM_NEWLINE
            )
            self.rfile_d.write(nft.DELIM_NEWLINE)

        # close the file
        #
        self.rfile_d.close()

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NedcOverlap::compute
    #
    # arguments:
    #  ref: reference annotation
    #  hyp: hypothesis annotation
    #
    # return:
    #  refo: the output aligned ref string
    #  hypo: the output aligned hyp string
    #  hit: the number of hits
    #  mis: the number of misses
    #  fal: the number of false alarms
    #
    # this method loops through reference and hypothesis annotations to
    # collect miss/hits and false alarms.
    #
    def compute(self, ref, hyp):

        # check to make sure the annotations match:
        #  since these are floating point values for times, we
        #  do a simple sanity check to make sure the end times
        #  are close (within 1 microsecond)
        #
        if round(ref[-1][1], 3) != round(hyp[-1][1], 3):
            return False

        # prime the output strings with null characters
        #
        refo = []
        hypo = []

        # loop over the ref annotation to collect hits and misses
        #
        hit = int(0)
        mis = int(0)
        fal = int(0)

        for event in ref:
            self.tgt_d[event[2]] += 1
            refo.append(event[2])
            labels, starts, stops = self.get_events(event[0], event[1], hyp)
            if event[2] in labels:
                self.hit_d[event[2]] += 1
                hit += 1
            else:
                self.mis_d[event[2]] += 1
                mis += 1

        # loop over the hyp annotation to collect false alarms
        #
        for event in hyp:
            hypo.append(event[2])
            labels, starts, stops = self.get_events(event[0], event[1], ref)
            if event[2] not in labels:
                self.fal_d[event[2]] += 1
                fal += 1

        # exit gracefully
        #
        return (refo, hypo, hit, mis, fal)

    #
    # end of method

    # method: NedcOverlap::get_events
    #
    # arguments:
    #  start: start time
    #  stop: stop_time
    #  events: a list of events
    #
    # return:
    #  labels: the labels that overlap with the start and stop time
    #  starts: a list of start times
    #  stops: a list of stop times
    #
    # this method returns a list of events that fall within a specified
    # range of time.
    #
    def get_events(self, start, stop, events):

        # declare output variables
        #
        labels = []
        starts = []
        stops = []

        # loop over all events
        #
        for event in events:

            # if the event overlaps partially with the interval,
            # it is a match. this means:
            #              start               stop
            #   |------------|<---------------->|-------------|
            #          |---------- event -----|
            #
            if (event[1] > start) and (event[0] < stop):
                starts.append(event[0])
                stops.append(event[1])
                labels.append(event[2])

        # exit gracefully
        #
        return [labels, starts, stops]

    #
    # end of method

    # method: NedcOverlap::compute_performance
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
    #
    # Note that, like the NIST algorithm, the overlap method does not give
    # us a confusion matrix.
    #
    def compute_performance(self):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: computing the performance"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
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
                    NedcOverlap.__CLASS_NAME__,
                    ndt.__NAME__,
                    "number of events is zero",
                    num_total_ref_events,
                )
            )
            return False

        # ----------------------------------------------------------------------
        # (1) The first block of parameters count events such as hits,
        #     missses and false alarms. The overlap algorithm provides
        #     these directly.
        #
        for key1 in self.hit_d:
            self.ins_d[key1] = self.fal_d[key1]
            self.del_d[key1] = self.mis_d[key1]

        # ----------------------------------------------------------------------
        # (2) The second block of computations are the derived measures
        #     such as sensitivity. These are computed using a two-step
        #     approach:
        #      (2.2) compute true positives, etc. (tp, tn, fp, fn)
        #      (2.3) compute the derived measures (e.g., sensitivity)
        #
        # loop over all labels
        #
        for key1 in self.hit_d:

            # ------------------------------------------------------------------
            # (2.2) The overlap algorithm outputs hits, misses and false alarms
            #       directly. These must be converted to (tp, tn, fp, fn).
            #
            # compute true positives (tp)
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
                        NedcOverlap.__CLASS_NAME__,
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
                    "Warning: %s (line: %s) %s::%s: %s (%f)"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NedcOverlap.__CLASS_NAME__,
                        ndt.__NAME__,
                        "duration is zero",
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
                        NedcOverlap.__CLASS_NAME__,
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
                        NedcOverlap.__CLASS_NAME__,
                        ndt.__NAME__,
                        "mcc ratio divide by zero",
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
                        NedcOverlap.__CLASS_NAME__,
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

        if round(f1s_denom, ndt.MAX_PRECISION) == 0:
            print(
                "Warning: %s (line: %s) %s::%s: %s (%s)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    NedcOverlap.__CLASS_NAME__,
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
                    NedcOverlap.__CLASS_NAME__,
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
                    NedcOverlap.__CLASS_NAME__,
                    ndt.__NAME__,
                    "zero duration",
                    "summary",
                )
            )
            self.sum_flr_d = float(0)
        else:
            self.sum_flr_d = float(self.sum_fp_d) / self.total_dur_d * (60 * 60 * 24)

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NedcOverlap::display_results
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
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
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
            fp.write(nft.DELIM_NEWLINE)

        # display a summary of the results
        #
        fp.write(("Summary:" + nft.DELIM_NEWLINE).upper())
        fp.write(nft.DELIM_NEWLINE)

        # display the standard derived values
        #
        fp.write(
            "   %30s: %12.0f   <**" % ("Total", float(self.sum_tgt_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f   <**" % ("Hits", float(self.sum_hit_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f   <**" % ("Misses", float(self.sum_mis_d))
            + nft.DELIM_NEWLINE
        )
        fp.write(
            "   %30s: %12.0f   <**" % ("False Alarms", float(self.sum_fal_d))
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

        # exit gracefully
        #
        return True

    #
    # end of method

    # --------------------------------------------------------------------------
    #
    # class-specific methods go here:
    #  these methods support ROC curve generation
    #
    # --------------------------------------------------------------------------

    # method: NedcOverlap::score_roc
    #
    # arguments:
    #  events_ref: a reference list
    #  events_hyp: a hypothesis list
    #
    # return: a boolean value indicating status
    #
    # This method computes a confusion matrix for an roc/det curve.
    #
    def score_roc(self, events_ref, events_hyp):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: computing an roc/det curve"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
            )

        # declare local variables
        #
        status = True
        ann = nat.Ann()

        # loop over all event lists (corresponding to files)
        #
        for ann_ref, ann_hyp in zip(events_ref, events_hyp):

            # update the total duration
            #
            self.total_dur_d += ann_ref[-1][1]

            # add this to the confusion matrix
            #
            refo, hypo, hit, mis, fal = self.compute(ann_ref, ann_hyp)
            if refo == None:
                print(
                    "Error: %s (line: %s) %s::%s: %s"
                    % (
                        __FILE__,
                        ndt.__LINE__,
                        NedcOverlap.__CLASS_NAME__,
                        ndt.__NAME__,
                        "error computing confusions",
                    )
                )
                return False

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NedcOverlap::compute_performance_roc
    #
    # arguments:
    #  key: the class to be scored
    #
    # return: a boolean value indicating status
    #
    # This is a stripped down version of compute_performance that is
    # focused on the data needed for an ROC or DET curve.
    #
    # Note that because of the way this method is used, error messages
    # are suppressed.
    #
    def compute_performance_roc(self, key):

        # display informational message
        #
        if self.dbgl_d > ndt.BRIEF:
            print(
                "%s (line: %s) %s::%s: computing performance for an ROC"
                % (__FILE__, ndt.__LINE__, NedcOverlap.__CLASS_NAME__, ndt.__NAME__)
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
                    NedcOverlap.__CLASS_NAME__,
                    ndt.__NAME__,
                    "number of events is zero",
                    num_total_ref_events,
                )
            )
            return False

        # ----------------------------------------------------------------------
        # (1) The first block of parameters count events such as hits,
        #     missses and false alarms. The overlap algorithm provides
        #     these directly.
        #
        for key1 in self.hit_d:
            self.ins_d[key1] = self.fal_d[key1]
            self.del_d[key1] = self.mis_d[key1]

        # ----------------------------------------------------------------------
        # (2) The second block of computations are the derived measures
        #     such as sensitivity. These are computed using a two-step
        #     approach:
        #      (2.2) compute true positives, etc. (tp, tn, fp, fn)
        #      (2.3) compute the derived measures (e.g., sensitivity)
        #
        # ------------------------------------------------------------------
        # (2.2) The overlap algorithm outputs hits, misses and false alarms
        #       directly. These must be converted to (tp, tn, fp, fn).
        #
        # compute true positives (tp)
        #
        self.tp_d[key] = self.hit_d[key]

        # compute true negatives (tn):
        #  sum the hits that are not the current label
        #
        tn_sum = int(0)
        for key2 in self.hit_d:
            if key != key2:
                tn_sum += self.hit_d[key2]
        self.tn_d[key] = tn_sum

        # compute false positives (fp): copy false alarms
        #
        self.fp_d[key] = self.fal_d[key]

        # compute false negatives (fn): copy misses
        #
        self.fn_d[key] = self.mis_d[key]

        # check the health of the confusion matrix
        #
        tp = self.tp_d[key]
        fp = self.fp_d[key]
        tn = self.tn_d[key]
        fn = self.fn_d[key]
        tdur = self.total_dur_d

        # (2.3) compute derived measures
        #
        if (tp + fn) != 0:
            self.tpr_d[key] = float(self.tp_d[key]) / float(tp + fn)
        else:
            self.tpr_d[key] = float(0)

        if (tn + fp) != 0:
            self.tnr_d[key] = float(self.tn_d[key]) / float(tn + fp)
        else:
            self.tnr_d[key] = float(0)

        self.fnr_d[key] = 1 - float(self.tpr_d[key])
        self.fpr_d[key] = 1 - float(self.tnr_d[key])

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: NedcOverlap::get_roc
    #
    # arguments:
    #  key: the symbol for which the values are needed
    #
    # return: a boolean value indicating status
    #
    # This method simply returns the quanities needed for an roc curve:
    # true positive rate (tpr) as a function of the false positive rate (fpr).
    #
    def get_roc(self, key):
        return self.fpr_d[key], self.tpr_d[key]

    # method: NedcOverlap::get_det
    #
    # arguments:
    #  key: the symbol for which the values are needed
    #
    # return: a boolean value indicating status
    #
    # This method simply returns the quanities needed for a det curve:
    # false negative rate (fnr) as a function of the false positive rate (fpr).
    #
    def get_det(self, key):
        return self.fpr_d[key], self.fnr_d[key]


# end of file
#
