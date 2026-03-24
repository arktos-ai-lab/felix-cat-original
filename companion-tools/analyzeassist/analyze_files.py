# coding: UTF8
"""
Command-line utility to count words in arbitrary files

"""
import logging
import argparse
import sys

from file_analysis import get_results
from output_format import max_width
from output_format import print_row_txt as print_row
from streamencode import OutStreamEncoder
from AnalyzeAssist import model

_ = model._
LOGGER = logging.getLogger(__name__)


def segstat2list(segstat):
    """Converts a Segment class instance into a list of integers"""

    return [segstat.words,
            segstat.characters,
            segstat.chars_no_spaces,
            segstat.asian_chars,
            segstat.non_asian_words]


def range2item(match_range):
    """Converts a match range into a formatted string for output.
    
    @param match_range: A tuple of ints representing match percentages
    """

    left, right = match_range

    if left == right:
        return "%i%%" % left

    return "%i-%i%%" % match_range


def print_results(stats, title, outfile):
    """Prints the analysis results
    
    @param stats: The match statistics
    @param title: The output file title
    @param outfile: A file-like object for output
    """
    columns = [_("Score"),
               _("Words"),
               _("Chars"),
               _("Chars (no spaces)"),
               _("Asian"),
               _("Non-Asian Words")]

    repetitions_row = [_("Repetitions")] + segstat2list(stats.repetitions)

    data = []
    for key, segstat in stats.match_ranges.items():
        data.append([key] + segstat2list(segstat))

    data.sort()
    data.reverse()

    totals = [_("Totals")]

    data = [repetitions_row] + data

    for i in range(1, len(columns)):
        totals.append(sum([row[i] for row in data]))

    print >> outfile
    print >> outfile, title

    output_data = [columns] + data
    col_paddings = []

    for i in range(len(columns)):
        col_paddings.append(max_width(output_data, i))

    print_row(columns, col_paddings, outfile)
    print_row(repetitions_row, col_paddings, outfile)

    for row in output_data[2:]:
        row[0] = range2item(row[0])
        print_row(row, col_paddings, outfile)

    print >> outfile, "=" * (sum(col_paddings) + 2 * len(col_paddings) + 5)
    print_row(totals, col_paddings, outfile)

    print >> outfile


def analyze(outfile_name, infiles, memories):
    """
    Analyze infiles against memories, and output results to outfile
    """

    results = get_results(infiles, memories, {})

    outfile = open(outfile_name, "w")
    outfile = OutStreamEncoder(outfile, "utf-8")

    for result in results:
        title, stats = result

        print_results(stats, title, outfile)

    outfile.close()


def main(argv):
    """Called when analyze_files run as the main script"""

    print
    print "=" * 30
    print "| analyze_files version 1.0"
    print "=" * 30

    # We need these two to set up
    # with the broker for segmenter
    import model

    sys.stdout = OutStreamEncoder(sys.stdout)
    sys.stderr = OutStreamEncoder(sys.stderr)

    parser = argparse.ArgumentParser(
        description=_('Analyzes input files against supplied memories'))

    # Extension
    fuzzy_options = model.get_fuzzy_options()
    analyze_numbers = model.get_analyze_numbers()

    parser.add_argument('-e',
                        metavar="extension",
                        default=None,
                        required=False,
                        help=_("Extension for extracting fuzzy segments"),
                        dest="extension")

    parser.add_argument('-d',
                        metavar="directory",
                        default=None,
                        required=False,
                        help=_("Directory to save extracted fuzzy match files"),
                        dest="directory")

    parser.add_argument('-n',
                        metavar="numbers",
                        default=False,
                        required=False,
                        help=_("Analyze number-only segments"),
                        dest="numbers")

    parser.add_argument('-o',
                        metavar="outfile",
                        default="analysis.txt",
                        help=_("The output file (default is 'analysis.txt')"),
                        dest="outfile")

    # Memories
    parser.add_argument('-m',
                        nargs="+",
                        metavar="memory",
                        required=True,
                        help=_("One or more memory files"),
                        dest="memories")

    # Files
    parser.add_argument('-f',
                        nargs="+",
                        metavar="filename",
                        required=True,
                        help=_("One or more files to process"),
                        dest="files")

    args = parser.parse_args(argv)

    new_fuzzy_options = dict(extension=args.extension,
                             directory=args.directory)

    if new_fuzzy_options != fuzzy_options:
        model.set_fuzzy_options(new_fuzzy_options)

    if analyze_numbers != args.numbers:
        model.set_analyze_numbers(args.numbers)

    outfile = args.outfile
    infiles = args.files
    memories = args.memories
    print
    print _("Analyzing files:"), infiles
    print _("Memories:"), memories
    print _("Writing results to %s") % outfile

    analyze(outfile, infiles, memories)

    # change the options back
    if new_fuzzy_options != fuzzy_options:
        model.set_fuzzy_options(fuzzy_options)

    if analyze_numbers != args.numbers:
        model.set_analyze_numbers(analyze_numbers)

    print _("...Done!")


if __name__ == '__main__':

    main(sys.argv[1:])

