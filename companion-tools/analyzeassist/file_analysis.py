# coding: UTF8
"""
File-analysis routines.
"""
import logging
import segmenter
import docstats
import segmatches
from AnalyzeAssist import broker
from AnalyzeAssist.broker import BrokerRequestHandler
from AnalyzeAssist import broadcaster
import os
from streamencode import OutStreamEncoder
import urlparse
import model

_ = model._
LOGGER = logging.getLogger(__name__)


class Bunch(object):
    """
    Turns dictionaries into objects

    >>> bunch = Bunch(spam="eggs")
    >>> bunch.spam
    'eggs'
    """

    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def is_url(filename):
    return filename.startswith("http")


def make_full_path(path_to_analysis_file, fuzzy_options):
    """Create the full path for the output file"""

    if is_url(path_to_analysis_file):
        scheme, net, path, params, query, frag = urlparse.urlparse(path_to_analysis_file)
        file_path = net
        file_name = net + path.replace("/", "_")

    else:
        file_path, file_name = os.path.split(path_to_analysis_file)

    extension = fuzzy_options["extension"]
    directory = fuzzy_options["directory"]
    if not directory:
        directory = file_path

    partial_path = os.path.join(directory, file_name)
    full_path = ".".join((partial_path, extension, "txt"))
    return full_path


class NomatchWriter(object):
    """Writes non-matching segments to file"""

    def __init__(self, filename, fuzzy_options):
        self.fp = None
        self.init_fp(make_full_path(filename, fuzzy_options))

    def init_fp(self, filename):
        """Open up the file handle"""
        self.fp = OutStreamEncoder(open(filename, "w"), "utf-8")

    def __del__(self):
        """Paranoid, but..."""
        self.close_fp()

    def close_fp(self):
        """Cleanup"""
        self.fp.close()

    def __call__(self, segment):
        """Write the segment to the out file, one segment per line"""
        print >> self.fp, segment


def devnull_nomatch(segment):
    """When we don't want to write non-matches"""
    pass


def get_nomatch_writer(filename, fuzzy_options):
    """Get the no-match writer function:
        A wrapper of a file handle or devnull sink
    """

    if fuzzy_options and fuzzy_options.get("extract"):
        return NomatchWriter(filename, fuzzy_options)
    else:
        return devnull_nomatch


def get_results(infiles, memories, prefs):
    """
    Analyze infiles against memories, and return list of results
    
    @param infiles: list of input files to analyze
    @param memories: list of memories to analyze them against
    
    @return: list of analysis results, in format (title, DocStats class)
    """
    LOGGER.debug('get_results')
    progress = None

    try:
        progress = Bunch(total=2 + len(infiles),
                         title=_("Analyzing files"),
                         message=_("Loading memory files"),
                         current=0,
                         cancel=False)
        broadcaster.Broadcast("progress", "start", progress)

        segmenterDict = segmenter.getSegmenterClasses(infiles)

        progress.current = 1
        progress.message = "Analyzing files"
        broadcaster.Broadcast("progress", "progress", progress)

        docstats.MINSCORE = 1.0
        totalstats = docstats.DocStats()
        segmatches.MINSCORE = docstats.MINSCORE
        matcher = segmatches.get_seg_matcher(memories)

        fuzzy_options = model.get_fuzzy_options()

        results = []

        for segClass, files in segmenterDict.items():

            segger = segClass()

            for filename in files:
                LOGGER.debug(u"Analyzing [%s]" % repr(filename))
                if is_url(filename):
                    base_name = filename
                else:
                    base_name = os.path.basename(filename)
                progress.message = _("Analyzing file %s") % repr(base_name)
                broadcaster.Broadcast("progress",
                                      "progress",
                                      progress)
                progress.current += 1

                if progress.cancel:
                    progress.message = _("Cancelled analsysis")
                    broadcaster.Broadcast("progress", "end", progress)
                    return None

                result = get_result(fuzzy_options,
                                    segger,
                                    filename,
                                    totalstats,
                                    matcher)
                LOGGER.debug(repr(result))
                results.append(result)

        if len(results) > 1:
            results.append((u"TOTAL", totalstats))

        progress.current = progress.total - 1
        progress.message = _("Finished analyzing files")
        broadcaster.Broadcast("progress",
                              "end",
                              progress)

        return results

    except Exception:
        import traceback

        traceback.print_exc()

        # If we don't end the progress, it'll freeze the program!
        if progress:
            progress.current = 0
            progress.message = _("An error occurred while analyzing files")
            broadcaster.Broadcast("progress",
                                  "end",
                                  progress)
        return None


def get_result(fuzzy_options, segger, filename, totalstats, matcher):
    """Get the analysis results for the filename"""

    filestats = docstats.DocStats()

    write_nomatch = get_nomatch_writer(filename, fuzzy_options)
    LOGGER.debug("Getting result for [%s]" % repr(filename))

    for seg in segger.get_sentences(filename):

        match = matcher.best_match(seg)
        if match < 100:
            write_nomatch(seg)
        segstat = docstats.Segment(seg)
        totalstats.add_seg(segstat, match)
        filestats.add_seg(segstat, match)

    return filename, filestats


@BrokerRequestHandler("analyze files")
def brokerAnalyzeFiles():
    """Broker provider of file-analysis function
    """

    infiles, memories = broker.CurrentData()
    return get_results(infiles, memories)


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()