# coding: UTF8
"""
Command-line utility to count words in arbitrary files

count_words.py -h for help
"""

import argparse
import segmenter
import docstats
from docstats import get_doc_seg
import sys
import model
import os
from AnalyzeAssist import broadcaster
from output_format import max_width
from output_format import print_row_txt as print_row
from streamencode import OutStreamEncoder


class ProgressReporter(object):
    """Convenience class for defining properties in
    constructor"""

    def __init__(self, **kwds):
        self.message = None
        self.current = None
        self.cancel = None
        self.__dict__.update(kwds)

    def start(self, msg):
        """Begin progress"""
        self.message = msg
        broadcaster.Broadcast("progress",
                              "start",
                              self)

    def progress(self, msg):
        """Give progress update"""
        self.current += 1
        self.message = msg
        broadcaster.Broadcast("progress",
                              "progress",
                              self)

    def cancel_progress(self, msg):
        """Cancel progress"""
        self.message = msg
        broadcaster.Broadcast("progress",
                              "end",
                              self)

    def end(self, msg):
        """End progress"""
        self.message = msg
        broadcaster.Broadcast("progress",
                              "end",
                              self)


def get_results(infiles):
    """Retrieve the word count for the input files as a tuple
    columns, data
    
    @param infiles: A list of files to process
    """

    progress = ProgressReporter(total=2 + len(infiles),
                                title=_("Analyzing files"),
                                message=_("Loading memory files"),
                                current=0,
                                cancel=False)

    progress.start(_("Loading files"))

    segmenter_dict = segmenter.getSegmenterClasses(infiles)

    columns = [_("File"),
               _("Words"),
               _("Chars"),
               _("Chars (no spaces)"),
               _("Asian"),
               _("Non-Asian Words")]

    data = [columns]

    total_seg = docstats.Segment("")

    for segmenter_class, files in segmenter_dict.items():

        segger = segmenter_class()

        if hasattr(segger, "get_all_text"):
            segger.get_sentences = segger.get_all_text

        # We include numbers in the word count in all cases
        segger.chunking_strategy.filterNums = False

        for filename in files:
            progress.progress(_("Analyzing filename %s") \
                              % os.path.basename(filename))

            if progress.cancel:
                progress.cancel_progress(_("Cancelled analsysis"))
                return None

            doc_seg = get_doc_seg(filename, segger)

            total_seg.accumulate(doc_seg)

            data.append([os.path.basename(filename),
                         doc_seg.words,
                         doc_seg.characters,
                         doc_seg.chars_no_spaces,
                         doc_seg.asian_chars,
                         doc_seg.non_asian_words])

    progress.end(_("Finished analyzing files"))

    return data, total_seg


def print_results(out, results):
    """Print the results to filename-like object out
    
    @param out: A filename-like object
    @param results: The wordcount results
    """

    data, total_seg = results
    col_paddings = []

    columns = data[0]

    for i in range(len(columns)):
        col_paddings.append(max_width(data, i))

    for row in data:
        print_row(row, col_paddings, out)

    print >> out, u"=" * (sum(col_paddings) + len(col_paddings) * 3)

    row = [_("Total"),
           total_seg.words,
           total_seg.characters,
           total_seg.chars_no_spaces,
           total_seg.asian_chars,
           total_seg.non_asian_words]

    print_row(row, col_paddings, out)


def countwords(out, infiles):
    """Extract the segments from files into files filename+ext"""

    results = get_results(infiles)
    print_results(out, results)


def main(argv):
    """When called as main (e.g. console app)"""

    parser = argparse.ArgumentParser(
        description='Count the words/characters in the specified input files')

    # Extension
    parser.add_argument('-o',
                        #                        nargs=1,
                        metavar="outfile",
                        default="wordcount.txt",
                        help="The output filename (default is 'wordcount.txt')",
                        dest="outfile")

    # Files
    parser.add_argument('-f',
                        nargs="+",
                        metavar="filename",
                        required=True,
                        help="One or more files to process",
                        dest="files")

    args = parser.parse_args(argv)

    print "Performing wordcounts on files..."

    outfile = open(args.outfile, "w")
    filenames = [os.path.abspath(fn) for fn in args.files]
    countwords(OutStreamEncoder(outfile, "utf-8"), filenames)
    outfile.close()

    print "...Done!"


if __name__ == '__main__':

    try:
        import psyco

        psyco.full()
    except ImportError, e:
        print "No psyco! May run a bit slower"

    main(sys.argv[1:])

