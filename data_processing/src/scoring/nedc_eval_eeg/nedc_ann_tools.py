#!/usr/bin/env python
#
# file: $NEDC_NFC/class/python/nedc_ann_tools/nedc_ann_tools.py
#
# revision history:
#
# 20200610 (LV): refactored code
# 20200607 (JP): refactored code
# 20170728 (JP): added compare_durations and load_annotations
# 20170716 (JP): upgraded to use the new annotation tools
# 20170714 (NC): created new class structure
# 20170709 (JP): refactored the code
# 20170612 (NC): added parsing and displaying methods
# 20170610 (JP): initial version
#
# This class contains a collection of methods that provide
# the infrastructure for processing annotation-related data.
# ------------------------------------------------------------------------------

# import reqired system modules
#
import os
import sys

# import required NEDC modules
#
import nedc_debug_tools as ndt
import nedc_file_tools as nft

# ------------------------------------------------------------------------------
#
# global variables are listed here
#
# ------------------------------------------------------------------------------

# set the filename using basename
#
__FILE__ = os.path.basename(__file__)

# define a data structure that encapsulates all file types:
#  we use this data structure to access lower-level objects. the key
#  is the type name, the first value is the magic sequence that should
#  appear in the file and the second value is the name of class data member
#  that is used to dynamically bind the subclass based on the type.
#
#  we also need a list of supported versions for utilities to use.
#
FTYPE_LBL = "lbl_v1.0.0"
FTYPE_TSE = "tse_v1.0.0"
FTYPES = {"lbl": [FTYPE_LBL, "lbl_d"], "tse": [FTYPE_TSE, "tse_d"]}
VERSIONS = [FTYPE_LBL, FTYPE_TSE]

# define numeric constants
#
DEF_CHANNEL = int(-1)

# ---
# define constants associated with the Annotation class
#

# ---
# define constants associated with the Lbl class
#

# define a default montage file
#
DEFAULT_MAP_FNAME = "$NEDC_NFC/lib/nedc_ann_tools_map_v00.txt"

# define symbols that appear as keys in an lbl file
#
DELIM_LBL_MONTAGE = "montage"
DELIM_LBL_NUM_LEVELS = "number_of_levels"
DELIM_LBL_LEVEL = "level"
DELIM_LBL_SYMBOL = "symbols"
DELIM_LBL_LABEL = "label"

# define a list of characters we need to parse out
#
REM_CHARS = [
    nft.DELIM_BOPEN,
    nft.DELIM_BCLOSE,
    nft.DELIM_NEWLINE,
    nft.DELIM_SPACE,
    nft.DELIM_QUOTE,
    nft.DELIM_SEMI,
    nft.DELIM_SQUOTE,
]

# ---
# define constants associated with the Tse class
#

# ------------------------------------------------------------------------------
#
# functions listed here
#
# ------------------------------------------------------------------------------

# declare a global debug object so we can use it in functions
#
dbgl = ndt.Dbgl()

# function: get_unique_events
#
# arguments:
#  events: events to aggregate
#
# return: a list of unique events
#
# This method combines events if they are of the same start/stop times.
#
def get_unique_events(events):

    # display an informational message
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: creating a list of unique events"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    # list to store unique events
    #
    events = []

    # make sure events are sorted
    #
    events = sorted(events, key=lambda x: (x[0], x[1]))

    # loop until we have checked all events
    #
    while len(events) != 0:

        # reset flag
        #
        is_unique = True
        n_start = int(-1)
        n_stop = int(-1)

        # get this event's start/stop times
        #
        start = events[0][0]
        stop = events[0][1]

        # if we are not at the last event
        #
        if len(events) != 1:

            # get next event's start/stop times
            #
            n_start = events[1][0]
            n_stop = events[1][1]

        # if this event's start/stop times are the same as the next event's,
        #  (only do this if we are not at the last event)
        #
        if (n_start == start) and (n_stop == stop) and (len(events) != 1):

            # combine this event's dict with the next event's symbol dict
            #
            for symb in events[1][2]:

                # if the symb is not found in this event's dict
                #
                if symb not in events[0][2]:

                    # add symb to this event's dict
                    #
                    events[0][2][symb] = events[1][2][symb]

                # else if the symb in the next event has a higher prob
                #
                elif events[1][2][symb] > events[0][2][symb]:

                    # update this event's symb with prob from the next event
                    #
                    events[0][2][symb] = events[1][2][symb]

            # delete the next event, it is not unique
            #
            del events[1]

        # loop over unique events
        #
        for unique in events:

            # if the start/stop times of this event is found in unique events
            #
            if (start == unique[0]) and (stop == unique[1]):

                # combine unique event's dict with this event's dict:
                #  iterate over symbs in this event's dict
                #
                for symb in events[0][2]:

                    # if the symb is not found in the unique event's dict
                    #
                    if symb not in unique[2]:

                        # add symb to the unique event's dict
                        #
                        unique[2][symb] = events[0][2][symb]

                    # else if the symb in this event has a higher prob
                    #
                    elif events[0][2][symb] > unique[2][symb]:

                        # update unique event's symb with prob from this event
                        #
                        unique[2][symb] = events[0][2][symb]

                # delete this event, it is not unique
                #
                del events[0]
                is_unique = False
                break

        # if this event is still unique
        #
        if is_unique is True:

            # add this event to the unique events
            #
            events.append(events[0])

            # delete this event, it is now stored as unique
            #
            del events[0]

    # exit gracefully
    #
    return events


#
# end of function

# function: compare_durations
#
# arguments:
#  l1: the first list of files
#  l2: the second list of files
#
# return: a boolean value indicating status
#
# This method goes through two lists of files and compares the durations
# of the annotations. If they don't match, it returns false.
#
def compare_durations(l1, l2):

    # display an informational message
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: comparing durations of annotations"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    # create an annotation object
    #
    ann = Ann()

    # check the length of the lists
    #
    if len(l1) != len(l2):
        return False

    # loop over the lists together
    #
    for l1_i, l2_i in zip(l1, l2):

        # load the annotations for l1
        #
        if ann.load(l1_i) == False:
            print(
                "Error: %s (line: %s) %s: error loading annotation (%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, l1_i)
            )
            return False

        # get the events for l1
        #
        events_l1 = ann.get()
        if events_l1 == None:
            print(
                "Error: %s (line: %s) %s: error getting annotation ((%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, l1_i)
            )
            return False

        # load the annotations for l2
        #
        if ann.load(l2_i) == False:
            print(
                "Error: %s (line: %s) %s: error loading annotation (%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, l2_i)
            )
            return False

        # get the events for l2
        #
        events_l2 = ann.get()
        if events_l2 == None:
            print(
                "Error: %s (line: %s) %s: error getting annotation: (%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, l2_i)
            )
            return False

        # check the durations
        #
        if round(events_l1[-1][1], ndt.MAX_PRECISION) != round(
            events_l2[-1][1], ndt.MAX_PRECISION
        ):
            print(
                "Error: %s (line: %s) %s: durations do not match"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            print("\t%s (%f)" % (l1_i, events_l1[-1][1]))
            print("\t%s (%f)" % (l2_i, events_l2[-1][1]))
            return False

    # exit gracefully
    #
    return True


#
# end of function

# function: load_annotations
#
# arguments:
#  list: a list of filenames
#
# return: a list of lists containing all the annotations
#
# This method loops through a list and collects all the annotations.
#
def load_annotations(flist, level=int(0), sublevel=int(0), channel=DEF_CHANNEL):

    # display an informational message
    #
    if dbgl > ndt.BRIEF:
        print(
            "%s (line: %s) %s: loading annotations"
            % (__FILE__, ndt.__LINE__, ndt.__NAME__)
        )

    # create an annotation object
    #
    events = []
    ann = Ann()

    # loop over the list
    #
    for fname in flist:

        # load the annotations
        #
        if ann.load(fname) == False:
            print(
                "Error: %s (line: %s) %s: loading annotation for file (%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, fname)
            )
            return None

        # get the events
        #
        events_tmp = ann.get(level, sublevel, channel)
        if events_tmp == None:
            print(
                "Error: %s (line: %s) %s: error getting annotation (%s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, fname)
            )
            return None
        events.append(events_tmp)

    # exit gracefully
    #
    return events


#
# end of function

# ------------------------------------------------------------------------------
#
# classes are listed here:
#  there are four classes in this file arranged in this hierarchy
#   Ann -> {Tse, Lbl} -> AnnGr
#
# ------------------------------------------------------------------------------

# class: AnnGr
#
# This class implements the main data structure used to hold an annotation.
#
class AnnGr:

    # method: AnnGr::constructor
    #
    # arguments: none
    #
    # return: none
    #
    def __init__(self):

        # set the class name
        #
        AnnGr.__CLASS_NAME__ = self.__class__.__name__

        # declare a data structure to hold a graph
        #
        self.graph_d = {}

    #
    # end of method

    # method: AnnGr::create
    #
    # arguments:
    #  lev: level of annotation
    #  sub: sublevel of annotation
    #  chan: channel of annotation
    #  start: start time of annotation
    #  stop: stop time of annotation
    #  symbols: dict of symbols/probabilities
    #
    # return: a boolean value indicating status
    #
    # This method create an annotation in the AG data structure
    #
    def create(self, lev, sub, chan, start, stop, symbols):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: %s"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    ndt.__NAME__,
                    "creating annotation in AG data structure",
                )
            )

        # try to access sublevel dict at level
        #
        try:
            self.graph_d[lev]

            # try to access channel dict at level/sublevel
            #
            try:
                self.graph_d[lev][sub]

                # try to append values to channel key in dict
                #
                try:
                    self.graph_d[lev][sub][chan].append([start, stop, symbols])

                # if appending values failed, finish data structure
                #
                except:

                    # create empty list at chan key
                    #
                    self.graph_d[lev][sub][chan] = []

                    # append values
                    #
                    self.graph_d[lev][sub][chan].append([start, stop, symbols])

            # if accessing channel dict failed, finish data structure
            #
            except:

                # create dict at level/sublevel
                #
                self.graph_d[lev][sub] = {}

                # create empty list at chan
                #
                self.graph_d[lev][sub][chan] = []

                # append values
                #
                self.graph_d[lev][sub][chan].append([start, stop, symbols])

        # if accessing sublevel failed, finish data structure
        #
        except:

            # create dict at level
            #
            self.graph_d[lev] = {}

            # create dict at level/sublevel
            #
            self.graph_d[lev][sub] = {}

            # create empty list at level/sublevel/channel
            #
            self.graph_d[lev][sub][chan] = []

            # append values
            #
            self.graph_d[lev][sub][chan].append([start, stop, symbols])

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: AnnGr::get
    #
    # arguments:
    #  level: level of annotations
    #  sublevel: sublevel of annotations
    #
    # return: events by channel at level/sublevel
    #
    # This method returns the events stored at the level/sublevel argument
    #
    def get(self, level, sublevel, channel):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: getting events stored at level/sublevel"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # declare local variables
        #
        events = []

        # try to access graph at level/sublevel/channel
        #
        try:
            events = self.graph_d[level][sublevel][channel]

            # exit gracefully
            #
            return events

        # exit (un)gracefully: if failed, return False
        #
        except:
            print(
                "Error: %s (line: %s) %s::%s %s (%d/%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    AnnGr.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublevel/channel not found",
                    level,
                    sublevel,
                    channel,
                )
            )
            return False

    #
    # end of method

    # method: AnnGr::sort
    #
    # arguments: none
    #
    # return: a boolean value indicating status
    #
    # This method sorts annotations by level, sublevel,
    # channel, start, and stop times
    #
    def sort(self):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: %s %s"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    ndt.__NAME__,
                    "sorting annotations by",
                    "level, sublevel, channel, start and stop times",
                )
            )

        # sort each level key by min value
        #
        self.graph_d = {sorted(self.graph_d.items())}

        # iterate over levels
        #
        for lev in self.graph_d:

            # sort each sublevel key by min value
            #
            self.graph_d[lev] = {sorted(self.graph_d[lev].items())}

            # iterate over sublevels
            #
            for sub in self.graph_d[lev]:

                # sort each channel key by min value
                #
                self.graph_d[lev][sub] = {sorted(self.graph_d[lev][sub].items())}

                # iterate over channels
                #
                for chan in self.graph_d[lev][sub]:

                    # sort each list of labels by start and stop times
                    #
                    self.graph_d[lev][sub][chan] = sorted(
                        self.graph_d[lev][sub][chan], key=lambda x: (x[0], x[1])
                    )

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: AnnGr::add
    #
    # arguments:
    #  dur: duration of events
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method adds events of type sym.
    #
    def add(self, dur, sym, level, sublevel):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: adding events of type sym"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # try to access level/sublevel
        #
        try:
            self.graph_d[level][sublevel]
        except:
            print(
                "Error: %s (line: %s) %s::%s %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    AnnGr.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublevel not found",
                    level,
                    sublevel,
                )
            )
            return False

        # variable to store what time in the file we are at
        #
        mark = 0.0

        # make sure events are sorted
        #
        self.sort()

        # iterate over channels at level/sublevel
        #
        for chan in self.graph_d[level][sublevel]:

            # reset list to store events
            #
            events = []

            # iterate over events at each channel
            #
            for event in self.graph_d[level][sublevel][chan]:

                # ignore if the start or stop time is past the duration
                #
                if (event[0] > dur) or (event[1] > dur):
                    pass

                # ignore if the start time is bigger than the stop time
                #
                elif event[0] > event[1]:
                    pass

                # ignore if the start time equals the stop time
                #
                elif event[0] == event[1]:
                    pass

                # if the beginning of the event is not at the mark
                #
                elif event[0] != mark:

                    # create event from mark->starttime
                    #
                    events.append([mark, event[0], {sym: 1.0}])

                    # add event after mark->starttime
                    #
                    events.append(event)

                    # set mark to the stop time
                    #
                    mark = event[1]

                # if the beginning of the event is at the mark
                #
                else:

                    # store this event
                    #
                    events.append(event)

                    # set mark to the stop time
                    #
                    mark = event[1]
            #
            # end of for

            # after iterating through all events, if mark is not at dur
            #
            if mark != dur:

                # create event from mark->dur
                #
                events.append([mark, dur, {sym: 1.0}])

            # store events as the new events in self.graph_d
            #
            self.graph_d[level][sublevel][chan] = events
        #
        # end of for

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: AnnGr::delete
    #
    # arguments:
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method deletes events of type sym
    #
    def delete(self, sym, level, sublevel):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: deleting events of type sym"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # try to access level/sublevel
        #
        try:
            self.graph_d[level][sublevel]
        except:
            print(
                "Error: %s (line: %s) %s::%s %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    AnnGr.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublevel not found",
                    level,
                    sublevel,
                )
            )
            return False

        # iterate over channels at level/sublevel
        #
        for chan in self.graph_d[level][sublevel]:

            # get events at chan
            #
            events = self.graph_d[level][sublevel][chan]

            # keep only the events that do not contain sym
            #
            events = [e for e in events if sym not in e[2].keys()]

            # store events in self.graph_d
            #
            self.graph_d[level][sublevel][chan] = events
        #
        # end of for

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: AnnGr::get_graph
    #
    # arguments: none
    #
    # return: entire graph data structure
    #
    # This method returns the entire graph, instead of a
    # level/sublevel/channel.
    #
    def get_graph(self):
        return self.graph_d

    #
    # end of method

    # method: AnnGr::set_graph
    #
    # arguments:
    #  graph: graph to set
    #
    # return: a boolean value indicating status
    #
    # This method sets the class data to graph.
    #
    def set_graph(self, graph):
        self.graph_d = graph
        return True

    #
    # end of method


#
# end of class

# class: Tse
#
# This class contains methods to manipulate time-synchronous event files.
#
class Tse:

    # method: Tse::constructor
    #
    # arguments: none
    #
    # return: none
    #
    def __init__(self):

        # set the class name
        #
        Tse.__CLASS_NAME__ = self.__class__.__name__

        # declare Graph object, to store annotations
        #
        self.graph_d = AnnGr()

    #
    # end of method

    # method: Tse::load
    #
    # arguments:
    #  fname: annotation filename
    #
    # return: a boolean value indicating status
    #
    # This method loads an annotation from a file.
    #
    def load(self, fname):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: loading annotation from file"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # open file
        #
        with open(fname, "r") as fp:

            # loop over lines in file
            #
            for line in fp:

                # clean up the line
                #
                line = line.replace(nft.DELIM_NEWLINE, nft.DELIM_NULL).replace(
                    nft.DELIM_CARRIAGE, nft.DELIM_NULL
                )
                check = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL)

                # throw away commented, blank lines, version lines
                #
                if (
                    check.startswith(nft.DELIM_COMMENT)
                    or check.startswith(nft.DELIM_VERSION)
                    or len(check) == 0
                ):
                    continue

                # split the line
                #
                val = {}
                parts = line.split()

                try:
                    # loop over every part, starting after start/stop times
                    #
                    for i in range(2, len(parts), 2):

                        # create dict with label as key, prob as value
                        #
                        val[parts[i]] = float(parts[i + 1])

                    # create annotation in AG
                    #
                    self.graph_d.create(
                        int(0), int(0), int(-1), float(parts[0]), float(parts[1]), val
                    )
                except:
                    print(
                        "Error: %s (line: %s) %s::%s %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Tse.__CLASS_NAME__,
                            ndt.__NAME__,
                            "invalid annotation",
                            line,
                        )
                    )
                    return False

        # make sure graph is sorted after loading
        #
        self.graph_d.sort

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: Tse::get
    #
    # arguments:
    #  level: level of annotations to get
    #  sublevel: sublevel of annotations to get
    #
    # return: events at level/sublevel by channel
    #
    # This method gets the annotations stored in the AG at level/sublevel.
    #
    def get(self, level, sublevel, channel):
        events = self.graph_d.get(level, sublevel, channel)
        return events

    #
    # end of method

    # method: Tse::display
    #
    # arguments:
    #  level: level of events
    #  sublevel: sublevel of events
    #  fp: a file pointer
    #
    # return: a boolean value indicating status
    #
    # This method displays the events from a flat AG.
    #
    def display(self, level, sublevel, fp=sys.stdout):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: displaying events from flag AG"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # get graph
        #
        graph = self.get_graph()

        # try to access graph at level/sublevel
        #
        try:
            graph[level][sublevel]
        except:
            print(
                "Error: %s (line: %s) %s::%s %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    Tse.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublev not in graph",
                    level,
                    sublevel,
                )
            )
            return False

        # iterate over channels at level/sublevel
        #
        for chan in graph[level][sublevel]:

            # iterate over events for each channel
            #
            for event in graph[level][sublevel][chan]:
                start = event[0]
                stop = event[1]

                # create a string with all symb/prob pairs
                #
                pstr = nft.STRING_EMPTY
                for symb in event[2]:
                    pstr += " %8s %10.4f" % (symb, event[2][symb])

                # display event
                #
                fp.write(
                    "%10s: %10.4f %10.4f%s" % ("ALL", start, stop, pstr)
                    + nft.DELIM_NEWLINE
                )

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: Tse::write
    #
    # arguments:
    #  ofile: output file path to write to
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method writes the events to a .tse file
    #
    def write(self, ofile, level, sublevel):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: writing events to .tse file"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # make sure graph is sorted
        #
        self.graph_d.sort()

        # get graph
        #
        graph = self.get_graph()

        # try to access the graph at level/sublevel
        #
        try:
            graph[level][sublevel]
        except:
            print(
                "Error: %s (line: %s) %s::%s %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    Tse.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublevel not in graph",
                    level,
                    sublevel,
                )
            )
            return False

        # list to collect all events
        #
        events = []

        # iterate over channels at level/sublevel
        #
        for chan in graph[level][sublevel]:

            # iterate over events for each channel
            #
            for event in graph[level][sublevel][chan]:

                # store every channel's events in one list
                #
                events.append(event)

        # remove any events that are not unique
        #
        events = get_unique_events(events)

        # open file with write
        #
        with open(ofile, nft.MODE_WRITE_TEXT) as fp:

            # write version
            #
            fp.write("version = %s" % FTYPES["tse"][0] + nft.DELIM_NEWLINE)
            fp.write(nft.DELIM_NEWLINE)

            # iterate over events
            #
            for event in events:

                # create symb/prob string from dict
                #
                pstr = nft.STRING_EMPTY
                for symb in event[2]:
                    pstr += " %s %.4f" % (symb, event[2][symb])

                # write event
                #
                fp.write("%.4f %.4f%s\n" % (event[0], event[1], pstr))

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: Tse::add
    #
    # arguments:
    #  dur: duration of events
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method adds events of type sym.
    #
    def add(self, dur, sym, level, sublevel):
        return self.graph_d.add(dur, sym, level, sublevel)

    #
    # end of method

    # method: Tse::delete
    #
    # arguments:
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method deletes events of type sym.
    #
    def delete(self, sym, level, sublevel):
        return self.graph_d.delete(sym, level, sublevel)

    #
    # end of method

    # method: Tse::get_graph
    #
    # arguments: none
    #
    # return: entire graph data structure
    #
    # This method accesses self.graph_d and returns the entire graph structure.
    #
    def get_graph(self):
        return self.graph_d.get_graph()

    #
    # end of method

    # method: Tse::set_graph
    #
    # arguments:
    #  graph: graph to set
    #
    # return: a boolean value indicating status
    #
    # This method sets the class data to graph.
    #
    def set_graph(self, graph):
        return self.graph_d.set_graph(graph)

    #
    # end of method


#
# end of class

# class: Lbl
#
# This class implements methods to manipulate label files.
#
class Lbl:

    # method: Lbl::constructor
    #
    # arguments: none
    #
    # return: none
    #
    # This method constructs Ag
    #
    def __init__(self):

        # set the class name
        #
        Lbl.__CLASS_NAME__ = self.__class__.__name__

        # declare variables to store info parsed from lbl file
        #
        self.chan_map_d = {int(-1): "all"}
        self.montage_lines_d = []
        self.symbol_map_d = {}
        self.num_levels_d = int(1)
        self.num_sublevels_d = {int(0): int(1)}

        # declare AG object to store annotations
        #
        self.graph_d = AnnGr()

    #
    # end of method

    # method: Lbl::load
    #
    # arguments:
    #  fname: annotation filename
    #
    # return: a boolean value indicating status
    #
    # This method loads an annotation from a file.
    #
    def load(self, fname):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: loading annotation from file"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # open file
        #
        fp = open(fname, nft.MODE_READ_TEXT)

        # loop over lines in file
        #
        for line in fp:

            # clean up the line
            #
            line = line.replace(nft.DELIM_NEWLINE, nft.DELIM_NULL).replace(
                nft.DELIM_CARRIAGE, nft.DELIM_NULL
            )

            # parse a single montage definition
            #
            if line.startswith(DELIM_LBL_MONTAGE):
                try:
                    chan_num, name, montage_line = self.parse_montage(line)
                    self.chan_map_d[chan_num] = name
                    self.montage_lines_d.append(montage_line)
                except:
                    print(
                        "Error: %s (line: %s) %s::%s: %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Lbl.__CLASS_NAME__,
                            ndt.__NAME__,
                            "error parsing montage",
                            line,
                        )
                    )
                    fp.close()
                    return False

            # parse the number of levels
            #
            elif line.startswith(DELIM_LBL_NUM_LEVELS):
                try:
                    self.num_levels_d = self.parse_numlevels(line)
                except:
                    print(
                        "Error: %s (line: %s) %s::%s: %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Lbl.__CLASS_NAME__,
                            ndt.__NAME__,
                            "error parsing number of levels",
                            line,
                        )
                    )
                    fp.close()
                    return False

            # parse the number of sublevels at a level
            #
            elif line.startswith(DELIM_LBL_LEVEL):
                try:
                    level, sublevels = self.parse_numsublevels(line)
                    self.num_sublevels_d[level] = sublevels

                except:
                    print(
                        "Error: %s (line: %s) %s::%s: %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Lbl.__CLASS_NAME__,
                            ndt.__NAME__,
                            "error parsing num of sublevels",
                            line,
                        )
                    )
                    fp.close()
                    return False

            # parse symbol definitions at a level
            #
            elif line.startswith(DELIM_LBL_SYMBOL):
                try:
                    level, mapping = self.parse_symboldef(line)
                    self.symbol_map_d[level] = mapping
                except:
                    print(
                        "Error: %s (line %s) %s::%s: %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Lbl.__CLASS_NAME__,
                            ndt.__NAME__,
                            "error parsing symbols",
                            line,
                        )
                    )
                    fp.close()
                    return False

            # parse a single label
            #
            elif line.startswith(DELIM_LBL_LABEL):
                try:
                    lev, sub, start, stop, chan, symbols = self.parse_label(line)
                except:
                    print(
                        "Error: %s (line %s) %s::%s: %s (%s)"
                        % (
                            __FILE__,
                            ndt.__LINE__,
                            Lbl.__CLASS_NAME__,
                            ndt.__NAME__,
                            "error parsing label",
                            line,
                        )
                    )
                    fp.close()
                    return False

                # create annotation in AG
                #
                status = self.graph_d.create(lev, sub, chan, start, stop, symbols)

        # close file
        #
        fp.close()

        # sort labels after loading
        #
        self.graph_d.sort()

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Lbl::get
    #
    # arguments:
    #  level: level value
    #  sublevel: sublevel value
    #
    # return: events by channel from AnnGr
    #
    # This method returns the events at level/sublevel
    #
    def get(self, level, sublevel, channel):

        # get events from AG
        #
        events = self.graph_d.get(level, sublevel, channel)

        # exit gracefully
        #
        return events

    #
    # end of method

    # method: Lbl::display
    #
    # arguments:
    #  level: level of events
    #  sublevel: sublevel of events
    #  fp: a file pointer
    #
    # return: a boolean value indicating status
    #
    # This method displays the events from a flat AG
    #
    def display(self, level, sublevel, fp=sys.stdout):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: displaying events from flat AG"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # get graph
        #
        graph = self.get_graph()

        # try to access level/sublevel
        #
        try:
            graph[level][sublevel]
        except:
            sys.stdout.write(
                "Error: %s (line: %s) %s::%s: %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    Lbl.__CLASS_NAME__,
                    ndt.__NAME__,
                    "level/sublevel not found",
                    level,
                    sublevel,
                )
            )
            return False

        # iterate over channels at level/sublevel
        #
        for chan in graph[level][sublevel]:

            # iterate over events at chan
            #
            for event in graph[level][sublevel][chan]:

                # find max probability
                #
                max_prob = max(event[2].values())

                # iterate over symbols in dictionary
                #
                for symb in event[2]:

                    # if the value of the symb equals the max prob
                    #
                    if event[2][symb] == max_prob:

                        # set max symb to this symbol
                        #
                        max_symb = symb
                        break

                # display event
                #
                fp.write(
                    "%10s: %10.4f %10.4f %8s %10.4f"
                    % (self.chan_map_d[chan], event[0], event[1], max_symb, max_prob)
                    + nft.DELIM_NEWLINE
                )

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: Lbl::parse_montage
    #
    # arguments:
    #  line: line from label file containing a montage channel definition
    #
    # return:
    #  channel_number: an integer containing the channel map number
    #  channel_name: the channel name corresponding to channel_number
    #  montage_line: entire montage def line read from file
    #
    # This method parses a montage line into it's channel name and number.
    # Splitting a line by two values easily allows us to get an exact
    # value/string from a line of definitions
    #
    def parse_montage(self, line):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: parsing montage by channel name, number"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # split between '=' and ',' to get channel number
        #
        channel_number = int(
            line.split(nft.DELIM_EQUAL)[1].split(nft.DELIM_COMMA)[0].strip()
        )

        # split between ',' and ':' to get channel name
        #
        channel_name = line.split(nft.DELIM_COMMA)[1].split(nft.DELIM_COLON)[0].strip()

        # remove chars from montage line
        #
        montage_line = line.strip().strip(nft.DELIM_NEWLINE)

        # exit gracefully
        #
        return [channel_number, channel_name, montage_line]

    #
    # end of method

    # method: Lbl::parse_numlevels
    #
    # arguments:
    #  line: line from label file containing the number of levels
    #
    # return: an integer containing the number of levels defined in the file
    #
    # This method parses the number of levels in a file.
    #
    def parse_numlevels(self, line):

        # split by '=' and remove extra characters
        #
        return int(line.split(nft.DELIM_EQUAL)[1].strip())

    #
    # end of method

    # method: Lbl::parse_numsublevels
    #
    # arguments:
    #  line: line from label file containing number of sublevels in level
    #
    # return:
    #  level: level from which amount of sublevels are contained
    #  sublevels: amount of sublevels in particular level
    #
    # This method parses the number of sublevels per level in the file
    #
    def parse_numsublevels(self, line):

        # display an informational message
        #
        if dbgl > ndt.BRIEF:
            print(
                "%s (line: %s) %s: parsing number of sublevels per level"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )

        # split between '[' and ']' to get level
        #
        level = int(line.split(nft.DELIM_OPEN)[1].split(nft.DELIM_CLOSE)[0].strip())

        # split by '=' and remove extra characters
        #
        sublevels = int(line.split(nft.DELIM_EQUAL)[1].strip())

        # exit gracefully
        #
        return [level, sublevels]

    #
    # end of method

    # method: Lbl::parse_symboldef
    #
    # arguments:
    #  line: line from label fiel containing symbol definition for a level
    #
    # return:
    #  level: an integer containing the level of this symbol definition
    #  mappings: a dict containing the mapping of symbols for this level
    #
    # This method parses a symbol definition line into a specific level,
    # the corresponding symbol mapping as a dictionary.
    #
    def parse_symboldef(self, line):

        # split by '[' and ']' to get level of symbol map
        #
        level = int(line.split(nft.DELIM_OPEN)[1].split(nft.DELIM_CLOSE)[0])

        # remove all characters to remove, and split by ','
        #
        syms = nft.STRING_EMPTY.join(
            c for c in line.split(nft.DELIM_EQUAL)[1] if c not in REM_CHARS
        )

        symbols = syms.split(nft.DELIM_COMMA)

        # create a dict from string, split by ':'
        #   e.g. '0: seiz' -> mappings[0] = 'seiz'
        #
        mappings = {}
        for s in symbols:
            mappings[int(s.split(nft.DELIM_COLON)[0])] = s.split(nft.DELIM_COLON)[1]

        # exit gracefully
        #
        return [level, mappings]

    #
    # end of method

    # method: Lbl::parse_label
    #
    # arguments:
    #  line: line from label file containing an annotation label
    #
    # return: all information read from .ag file
    #
    # this method parses a label definition into the values found in the label
    #
    def parse_label(self, line):

        # dict to store symbols/probabilities
        #
        symbols = {}

        # remove characters to remove, and split data by ','
        #
        lines = nft.STRING_EMPTY.join(
            c for c in line.split(nft.DELIM_EQUAL)[1] if c not in REM_CHARS
        )

        data = lines.split(nft.DELIM_COMMA)

        # separate data into specific variables
        #
        level = int(data[0])
        sublevel = int(data[1])
        start = float(data[2])
        stop = float(data[3])

        # the channel value supports either 'all' or channel name
        #
        try:
            channel = int(data[4])
        except:
            channel = int(-1)

        # parse probabilities
        #
        probs = (
            lines.split(nft.DELIM_OPEN)[1].strip(nft.DELIM_CLOSE).split(nft.DELIM_COMMA)
        )

        # set every prob in probs to type float
        #
        probs = list(map(float, probs))

        # convert the symbol map values to a list
        #
        map_vals = list(self.symbol_map_d[level].values())

        # iterate over symbols
        #
        for i in range(len(self.symbol_map_d[level].keys())):

            if probs[i] > 0.0:

                # set each symbol equal to the corresponding probability
                #
                symbols[map_vals[i]] = probs[i]

        # exit gracefully
        #
        return [level, sublevel, start, stop, channel, symbols]

    #
    # end of method

    # method: Lbl::write
    #
    # arguments:
    #  ofile: output file path to write to
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method writes events to a .lbl file.
    #
    def write(self, ofile, level, sublevel):

        # make sure graph is sorted
        #
        self.graph_d.sort()

        # get graph
        #
        graph = self.get_graph()

        # try to access graph at level/sublevel
        #
        try:
            graph[level][sublevel]
        except:
            print(
                "Error: %s (line: %s) %s: %s (%d/%d)"
                % (
                    __FILE__,
                    ndt.__LINE__,
                    ndt.__NAME__,
                    "level/sublevel not found",
                    level,
                    sublevel,
                )
            )
            return False

        # open file with write
        #
        with open(ofile, nft.MODE_WRITE_TEXT) as fp:

            # write version
            #
            fp.write(nft.DELIM_NEWLINE)
            fp.write("version = %s" % FTYPES["lbl"][0] + nft.DELIM_NEWLINE)
            fp.write(nft.DELIM_NEWLINE)

            # if montage_lines is blank, we are converting from tse to lbl.
            #
            # create symbol map from tse symbols
            #
            if len(self.montage_lines_d) == 0:

                # variable to store the number of symbols
                #
                num_symbols = 0

                # create a dictionary at level 0 of symbol map
                #
                self.symbol_map_d[int(0)] = {}

                # iterate over all events stored in the 'all' channels
                #
                for event in graph[level][sublevel][int(-1)]:

                    # iterate over symbols in each event
                    #
                    for symbol in event[2]:

                        # if the symbol is not in the symbol map
                        #
                        if symbol not in self.symbol_map_d[0].values():

                            # map num_symbols interger to symbol
                            #
                            self.symbol_map_d[0][num_symbols] = symbol

                            # increment num_symbols
                            #
                            num_symbols += 1

            # write montage lines
            #
            for line in self.montage_lines_d:
                fp.write("%s" % line + nft.DELIM_NEWLINE)

            fp.write(nft.DELIM_NEWLINE)

            # write number of levels
            #
            fp.write("number_of_levels = %d" % self.num_levels_d + nft.DELIM_NEWLINE)
            fp.write(nft.DELIM_NEWLINE)

            # write number of sublevels
            #
            for lev in self.num_sublevels_d:
                fp.write(
                    "level[%d] = %d" % (lev, self.num_sublevels_d[lev])
                    + nft.DELIM_NEWLINE
                )
            fp.write(nft.DELIM_NEWLINE)

            # write symbol definitions
            #
            for lev in self.symbol_map_d:
                fp.write(
                    "symbols[%d] = %s" % (lev, str(self.symbol_map_d[lev]))
                    + nft.DELIM_NEWLINE
                )
            fp.write(nft.DELIM_NEWLINE)

            # iterate over channels at level/sublevel
            #
            for chan in graph[level][sublevel]:

                # iterate over events in chan
                #
                for event in graph[level][sublevel][chan]:

                    # create string for probabilities
                    #
                    pstr = nft.DELIM_OPEN

                    # iterate over symbol map
                    #
                    for symb in self.symbol_map_d[level].values():

                        # if the symbol is found in the event
                        #
                        if symb in event[2]:
                            pstr += (
                                str(event[2][symb]) + nft.DELIM_COMMA + nft.DELIM_SPACE
                            )
                        else:
                            pstr += "0.0" + nft.DELIM_COMMA + nft.DELIM_SPACE

                    # remove the ', ' from the end of pstr
                    #
                    pstr = pstr[: len(pstr) - 2] + "]}"

                    # write event
                    #
                    fp.write(
                        "label = {%d, %d, %.4f, %.4f, %s, %s\n"
                        % (level, sublevel, event[0], event[1], chan, pstr)
                    )

        # exit gracefully
        #
        return True

    #
    # end of method

    # method: Lbl::add
    #
    # arguments:
    #  dur: duration of events
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method adds events of type sym
    #
    def add(self, dur, sym, level, sublevel):
        return self.graph_d.add(dur, sym, level, sublevel)

    # method: Lbl::delete
    #
    # arguments:
    #  sym: symbol of events
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method deletes events of type sym
    #
    def delete(self, sym, level, sublevel):
        return self.graph_d.delete(sym, level, sublevel)

    # method: Lbl::get_graph
    #
    # arguments: none
    #
    # return: entire graph data structure
    #
    # This method accesses self.graph_d and returns the entire graph structure.
    #
    def get_graph(self):
        return self.graph_d.get_graph()

    #
    # end of method

    # method: Lbl::set_graph
    #
    # arguments:
    #  graph: graph to set
    #
    # return: a boolean value indicating status
    #
    # This method sets the class data to graph
    #
    def set_graph(self, graph):
        return self.graph_d.set_graph(graph)

    #
    # end of method


#
# end of class

# class: Ann
#
# This class is the main class of this file. It contains methods to
# manipulate the set of supported annotation file formats including
# label (.lbl) and time-synchronous events (.tse) formats.
#
class Ann:

    # method: Ann::constructor
    #
    # arguments: none
    #
    # return: none
    #
    # This method constructs Ann
    #
    def __init__(self):

        # set the class name
        #
        Ann.__CLASS_NAME__ = self.__class__.__name__

        # declare variables for each type of file:
        #  these variable names must match the FTYPES declaration.
        #
        self.tse_d = Tse()
        self.lbl_d = Lbl()

        # declare variable to store type of annotations
        #
        self.type_d = None

    #
    # end of method

    # method: Ann::load
    #
    # arguments:
    #  fname: annotation filename
    #
    # return: a boolean value indicating status
    #
    # This method loads an annotation from a file.
    #
    def load(self, fname):

        # reinstantiate objects, this removes the previous loaded annotations
        #
        self.lbl_d = Lbl()
        self.tse_d = Tse()

        # determine the file type
        #
        magic_str = nft.get_version(fname)
        self.type_d = self.check_version(magic_str)
        if self.type_d == None:
            print(
                "Error: %s (line: %s) %s: unknown file type (%s: %s)"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, fname, magic_str)
            )
            return False

        # load the specific type
        #
        return getattr(self, FTYPES[self.type_d][1]).load(fname)

    #
    # end of method

    # method: Ann::get
    #
    # arguments:
    #  level: the level value
    #  sublevel: the sublevel value
    #
    # return:
    #  events: a list of ntuples containing the start time, stop time,
    #          a label and a probability.
    #
    # This method returns a flat data structure containing a list of events.
    #
    def get(self, level=int(0), sublevel=int(0), channel=int(-1)):

        if self.type_d is not None:
            events = getattr(self, FTYPES[self.type_d][1]).get(level, sublevel, channel)
        else:
            print(
                "Error: %s (line: %s) %s: no annotation loaded"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            return False

        # exit gracefully
        #
        return events

    #
    # end of method

    # method: Ann::display
    #
    # arguments:
    #  level: level value
    #  sublevel: sublevel value
    #  fp: a file pointer (default = stdout)
    #
    # return: a boolean value indicating status
    #
    # This method displays the events at level/sublevel.
    #
    def display(self, level=int(0), sublevel=int(0), fp=sys.stdout):

        if self.type_d is not None:

            # display events at level/sublevel
            #
            status = getattr(self, FTYPES[self.type_d][1]).display(level, sublevel, fp)

        else:
            sys.stdout.write(
                "Error: %s (line: %s) %s %s"
                % (__NAME__, ndt.__LINE__, ndt.__NAME__, "no annotations to display")
            )
            return False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Ann::write
    #
    # arguments:
    #  ofile: output file path to write to
    #  level: level of annotation to write
    #  sublevel: sublevel of annotation to write
    #
    # return: a boolean value indicating status
    #
    # This method writes annotations to a specified file.
    #
    def write(self, ofile, level=int(0), sublevel=int(0)):

        # write events at level/sublevel
        #
        if self.type_d is not None:
            status = getattr(self, FTYPES[self.type_d][1]).write(ofile, level, sublevel)
        else:
            sys.stdout.write(
                "Error: %s (line: %s) %s: %s"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__, "no annotations to write")
            )
            status = False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Ann::add
    #
    # arguments:
    #  dur: duration of file
    #  sym: symbol of event to be added
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method adds events to the current events based on args.
    #
    def add(self, dur, sym, level, sublevel):

        # add labels to events at level/sublevel
        #
        if self.type_d is not None:
            status = getattr(self, FTYPES[self.type_d][1]).add(
                dur, sym, level, sublevel,
            )
        else:
            print(
                "Error: %s (line: %s) %s: no annotations to add to"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            status = False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Ann::delete
    #
    # arguments:
    #  sym: symbol of event to be deleted
    #  level: level of events
    #  sublevel: sublevel of events
    #
    # return: a boolean value indicating status
    #
    # This method deletes all events of type sym
    #
    def delete(self, sym, level, sublevel):

        # delete labels from events at level/sublevel
        #
        if self.type_d is not None:
            status = getattr(self, FTYPES[self.type_d][1]).delete(sym, level, sublevel)
        else:
            print(
                "Error: %s (line: %s) %s: no annotations to delete"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            status = False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Ann::set_type
    #
    # arguments:
    #  type: type of ann object to set
    #
    # return: a boolean value indicating status
    #
    # This method sets the type and graph in type from self.type_d
    #
    def set_type(self, ann_type):

        # set the graph of ann_type to the graph of self.type_d
        #
        if self.type_d is not None:
            status = getattr(self, FTYPES[ann_type][1]).set_graph(
                getattr(self, FTYPES[self.type_d][1]).get_graph()
            )
            self.type_d = ann_type
        else:
            print(
                "Error: %s (line: %s) %s: no graph to set"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            status = False

        # exit gracefully
        #
        return status

    #
    # end of method

    # method: Ann::get_graph
    #
    # arguments: none
    #
    # return: the entire annotation graph
    #
    # This method returns the entire stored annotation graph
    #
    def get_graph(self):

        # if the graph is valid, get it
        #
        if self.type_d is not None:
            graph = getattr(self, FTYPES[self.type_d][1]).get_graph()
        else:
            print(
                "Error: %s (line: %s) %s: no graph to get"
                % (__FILE__, ndt.__LINE__, ndt.__NAME__)
            )
            graph = None

        # exit gracefully
        #
        return graph

    #
    # end of method

    # method: Ann::check_version
    #
    # arguments:
    #  magic: a magic sequence
    #
    # return: a character string containing the name of the type
    #
    def check_version(self, magic):

        # check for a match
        #
        for key in FTYPES:
            if FTYPES[key][0] == magic:
                return key

        # exit (un)gracefully:
        #  if we get this far, there was no match
        #
        return False

    #
    # end of method


#
# end of class

#
# end of file
