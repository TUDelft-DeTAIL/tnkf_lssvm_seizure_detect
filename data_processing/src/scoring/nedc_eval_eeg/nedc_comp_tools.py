#!/usr/bin/env python
#
# file: $NEDC_NFC/class/python/nedc_ann_tools/nedc_ann_tools.py
#
# revision history:
#  20200722 (LV): initial version
#
# usage:
#  import nedc_comp_tools as nec
#
# This class contains a collection of methods that are needed to
# run the competition version of nedc_eval_eeg scoring software
# ------------------------------------------------------------------------------

# import reqired system modules
#
import os
import sys

# import required NEDC modules
#
import nedc_file_tools as nft

# ------------------------------------------------------------------------------
#
# global variables are listed here
#
# ------------------------------------------------------------------------------

# define ref/hyp event constants
#
DEF_CLASS = "seiz"
BCKG_CLASS = "bckg"
DEF_CONF = float(1.0)
FIRST_EVENT_INDEX = 0
LAST_EVENT_INDEX = -1
START_TIME_INDEX = 0
STOP_TIME_INDEX = 1
DUPLICATE_STR = "Duplicate"
OVLP_STR = "Overlapping"

# ------------------------------------------------------------------------------
#
# functions are listed here:
#
# ------------------------------------------------------------------------------

# function: sort_dict
#
# arguments:
#  odict: dictionary mapping of files and events
#
# return: updated dictionary
#
# This function sorts the events in all files by the event start time
#
def sort_dict(odict):

    # for each file
    #
    for key in odict:

        # sort by the start time of the event
        #
        odict[key] = sorted(odict[key], key=lambda event: event[START_TIME_INDEX])

    # exit gracefully
    #
    return odict


#
# end of function


# function: parse_ref
#
# arguments:
#  f_cont: the file content tokenized by newline
#
# return: event dictionary and duration dictionary
#
# This function parses through the ref file and creates
# a dictionary mapping between files and their events
# i.e {'00000258_s002_t000': [[0.0, 10.0, 'bckg', 1.00]..] ... }
# it also returns a duration dictionary with a key/value pair of
# file/duration
#
def parse_ref(f_cont):

    # instatiate the event dictionary
    #
    odict = {}

    # for each line in the file
    #
    for line in f_cont:

        # split the line by whitespace
        #
        tokenized = line.split()

        # ensure we have at least fname start stop lbl
        #
        if len(tokenized) < 4:
            continue

        # collect required values
        #
        fname, start, stop, lbl = tokenized[:4]

        # if we have a confidence value
        #
        if len(tokenized) == 5:
            conf = float(tokenized[4])
        else:
            conf = DEF_CONF

        # convert start stop to float
        #
        start, stop = float(start), float(stop)

        # if this is a new file
        #
        if fname not in odict:

            # the value is a new nested list of events
            #
            odict[fname] = [[start, stop, {lbl: conf}]]

        # if this file is already in the dictionary
        #
        else:

            # add the event to the list
            #
            odict[fname].append([start, stop, {lbl: conf}])

    # sort the dictionary
    #
    odict = sort_dict(odict)

    # create a mapping of fname:duration; duration is simply
    # the stop time of the last event
    #
    dur_dict = {
        fname: odict[fname][LAST_EVENT_INDEX][STOP_TIME_INDEX] for fname in odict
    }

    # exit gracefully
    #
    return odict, dur_dict


#
# end of function


# function: fill_gap
#
# arguments:
#  odict: dictionary mapping of files and events
#  duration_dict: dictionary mapping of files and duration
#
# return:
#  odict: updated dictionary
#
# This function ensures that all events for the duration of
# the hyp files are accounted for
#
def fill_gap(odict, duration_dict):

    # for each hyp file
    #
    for fname in odict:

        # get the start and stop time of the file
        #
        f_start = 0.0
        f_stop = duration_dict[fname]

        # get the start time of the first event and the
        # stop time of the last event
        #
        first_event_start = odict[fname][FIRST_EVENT_INDEX][START_TIME_INDEX]
        last_event_stop = odict[fname][LAST_EVENT_INDEX][STOP_TIME_INDEX]

        # sanity check
        #
        if first_event_start < f_start:
            raise ValueError(
                "[%s]: '%s' event cannot start before time 0.0" % (sys.argv[0], fname)
            )
        if last_event_stop > f_stop:
            raise ValueError(
                "[%s]: '%s' event cannot stop after time %f"
                % (sys.argv[0], fname, last_event_stop)
            )

        # all events not accounted for will be background
        #
        bckg_event = {BCKG_CLASS: 1.0}

        # if the first event didn't start at time 0.0
        #
        if first_event_start != f_start:

            # insert a bckg event from time 0 to the start of
            # the first event
            #
            odict[fname].insert(0, [f_start, first_event_start, bckg_event])

        # if the last event didn't stop at the end of the file
        #
        if last_event_stop != f_stop:

            # insert a bckg event from the stop time of the
            # last event to the end of the file
            #
            odict[fname].append([last_event_stop, f_stop, bckg_event])

        # keep track of the previous event stop time
        # initially, this is the stop time of the first event
        #
        prev_event_stop = odict[fname][FIRST_EVENT_INDEX][STOP_TIME_INDEX]

        # skip the first event
        #
        index = 1

        # while there are events to process
        #
        while index < len(odict[fname]):

            # get the current event
            #
            event = odict[fname][index]

            # get the start/stop time of the current event
            #
            curr_event_start = event[START_TIME_INDEX]
            curr_event_stop = event[STOP_TIME_INDEX]

            # if the stop time of the previous event is not
            # equal to the start time of the current event
            #
            if prev_event_stop != curr_event_start:

                # insert a bckg event in between the two events
                #
                odict[fname].insert(
                    index, [prev_event_stop, curr_event_start, bckg_event]
                )

                # skip the next event
                #
                index += 1

            # update the stop time of the previous event
            #
            prev_event_stop = curr_event_stop

            # increment the index
            #
            index += 1

    # for each fname in the duration dictionary
    #
    for key in duration_dict:

        # if there is a file in the duration dictionary
        # that was not mentioned in the hyp file
        #
        if key not in odict:

            # add the file and set the entire duration as bckg
            #
            odict[key] = [[0.0, duration_dict[key], {BCKG_CLASS: 1.0}]]

    # exit gracefully
    #
    return odict


#
# end of function


# function: parse_hyp
#
# arguments:
#  f_cont: the file content of the hyp file
#  duration_dict: dictionary mapping of files and duration
#
# return: updated dictionary
#
# This function sorts through the hyp file and creates
# a dictionary mapping of file name and events
#
def parse_hyp(f_cont, duration_dict):

    # instantiate the event dictionary
    #
    odict = {}

    # for each line in the file
    #
    for line in f_cont:

        # tokenize the line by whitespace
        #
        tokenized = line.split()

        # ensure we have at least fname, start, stop
        #
        if len(tokenized) < 3:
            continue

        # collect the required values
        #
        fname, start, stop = tokenized[:3]

        # if we have a confidence value
        #
        if len(tokenized) == 4:
            conf = float(tokenized[3])
        else:
            conf = DEF_CONF

        # convert start/stop to floats
        #
        start, stop = float(start), float(stop)

        # if this file was not in the dictionary
        #
        if fname not in odict:

            # the value is a nested list of events
            #
            odict[fname] = [[start, stop, {DEF_CLASS: conf}]]

        # if the file was already in the dictionary
        #
        else:

            # add the event to the list
            #
            odict[fname].append([start, stop, {DEF_CLASS: conf}])

    # sort the dictionary
    #
    odict = sort_dict(odict)

    # make sure there aren't any duplicate or overlapping entries
    #
    fix_duplicates(odict)
    fix_overlaps(odict)

    # exit gracefully
    #
    return fill_gap(odict, duration_dict)


#
# end of function


# function: parse_file
#
# arguments:
#  fname: the name of the annoation file
#  duration_dict: dictionary mapping of files and duration
#
# return: event dictionary
#
# This function returns an event dictionary and duration
# dictionary for ref files or event dictionaries for hyp files
#
def parse_file(fname, duration_dict=None):

    # read the file
    #
    with open(fname, "r") as fp:
        f_cont = fp.read().splitlines()

    # if no duration dict was provided, treat as ref
    #
    if duration_dict is None:

        # return event dictionary and duration dictionary
        #
        return parse_ref(f_cont)

    # return event dictionary
    #
    return parse_hyp(f_cont, duration_dict)


#
# end of function


# function: fix_overlaps
#
# arguments:
#  f_dict: contains the file content stored in a type: list
#
# return: None
#
# This method fixes the annotation entries if there are overlapping
# events with other target events
#
def fix_overlaps(f_dict):

    # initialize variables
    #
    ovlp_idxs = {}

    # find overlaps for each file
    #
    for fname in f_dict.keys():

        ovlp_idxs[fname] = []

        ovlp_idxs[fname] = count_ovlps(f_dict[fname])

    # end of for
    #
    rm_spurious_events(f_dict, ovlp_idxs, OVLP_STR)

    # return gracefully
    #


# end of method
#

# function: count_ovlps
#
# arguments:
#  f_events: list of events related to a file with confidence
#
# return:
#  overlap_events: list of event indices marked for deletion.
#
# This method checks for overlaps between events and returns
#  indices of overlapping events (excluding first occurrence)
#
def count_ovlps(f_events):

    # initialize variables
    #
    overlap_events = []

    # loop through events
    #
    for i in range(len(f_events)):

        # check the remaining events
        #
        for j in range(i + 1, len(f_events)):

            # if event is already marked for delection
            # move to the next one
            #
            if j in overlap_events:
                continue

            # first event start falls between second event start/stop
            #
            if f_events[j][0] <= f_events[i][0] and f_events[i][0] < f_events[j][1]:
                overlap_events.append(j)

            # first event stop falls between second event start/stop
            #
            elif f_events[j][0] < f_events[i][1] and f_events[i][1] <= f_events[j][1]:
                overlap_events.append(j)

            # second event start falls between first event start/stop
            #
            elif f_events[i][0] <= f_events[j][0] and f_events[j][0] < f_events[i][1]:
                overlap_events.append(j)

            # second event stop falls between first event start/stop
            #
            elif f_events[i][0] < f_events[j][1] and f_events[j][1] <= f_events[i][1]:
                overlap_events.append(j)

    # return gracefully
    #
    return overlap_events


# end of method
#

# function: fix_duplicates
#
# arguments:
#  f_dict: contains the file content stored in a type: list
#
# return: None
#
# This method fixes the annotation entries if there are duplicate
# labels with the same start and stop times
#
def fix_duplicates(f_dict):

    # initialize the dictionary showing duplicate entry indices/file
    #
    dup_idxs = {}

    # separate entries based on files and their content
    #
    for fname in f_dict.keys():

        # initialize the variables
        #
        curr_fields = ""
        prev_fields = ""
        st = int(0)
        end = int(0)
        conf = float(0)

        dup_idxs[fname] = []

        # loop per each record/file
        #
        for event_idx in range(len(f_dict[fname])):

            # only deal with the target ("seizure") class
            #
            if DEF_CLASS in f_dict[fname][event_idx][2].keys():

                # collect annotation fields
                st = int(f_dict[fname][event_idx][START_TIME_INDEX])
                end = int(f_dict[fname][event_idx][STOP_TIME_INDEX])
                conf = float(f_dict[fname][event_idx][2][DEF_CLASS])

                curr_fields = "\t".join([str(st), str(end)])

                # if current and previous annotations are the same
                #
                if curr_fields == prev_fields:
                    dup_idxs[fname].append(event_idx)

                    # update the confidence to maximum among the observed
                    #
                    f_dict[fname][event_idx][2][DEF_CLASS] = max(conf, prev_conf)

                # end of if
                #
            # end of if
            #

            prev_fields = curr_fields
            prev_conf = conf

        # end of for
        #

    # end of for
    #

    # remove the duplicate entries
    #
    rm_spurious_events(f_dict, dup_idxs, DUPLICATE_STR)


# end of method
#

# function: rm_spurious_events
#
# arguments:
#  f_dict: contains the file content stored in a type: list
#  del_dict_idxs: contains indices to be deleted for each file
#
# return: None
#
# This method deletes spurious events found at specific indices
#
def rm_spurious_events(f_dict, del_dict_idxs, errtype_str=OVLP_STR):

    # remove the overlapped entries
    #
    for fname, event_idxs in del_dict_idxs.items():

        # remove elements at the indices observed at duplicate entries
        #
        while len(event_idxs) != 0:
            print(
                "Warning: %s entries found for %s: start=%.4f, stop =%.4f"
                % (
                    errtype_str,
                    fname,
                    float(f_dict[fname][event_idxs[0]][START_TIME_INDEX]),
                    float(f_dict[fname][event_idxs[0]][STOP_TIME_INDEX]),
                )
            )
            del f_dict[fname][event_idxs[0]]
            del event_idxs[0]

            # shift the index since the event has been removed
            #
            if len(event_idxs) != 0:
                event_idxs = [idx - 1 for idx in event_idxs]

        # end of while
        #

    # end of for
    #

    # return gracefully
    #


# end of method
#


# end of file
#
