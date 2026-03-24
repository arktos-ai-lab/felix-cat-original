# coding: UTF8
"""
Command-line utility to extract segments into text files

"""
import logging
import argparse
import sys
import logging
import segmenter
import model

_ = model._
LOGGER = logging.getLogger(__name__)
VERSION = '1.1'


def extract(args, infiles):
    """Extract the segments from files into files file+ext"""

    segmenter_dict = segmenter.getSegmenterClasses(infiles)

    for seg_class, files in segmenter_dict.items():

        segger = seg_class()
        segger.chunking_strategy.analyze_numbers = args.numbers
        LOGGER.debug(u'segmenter is %s', segger)

        for filename in files:
            LOGGER.debug(u"Segmenting file: %s" % filename)
            outfile = filename + args.extension

            with open(outfile, "w") as out:
                for seg in segger.get_sentences(filename):
                    try:
                        print >> out, seg.encode('utf8')
                    except AttributeError:
                        LOGGER.exception("Failed to output segment")


def main(argv):
    """
    Run if called as main
    """

    LOGGER.info("extract_segments version %s", VERSION)

    parser = argparse.ArgumentParser(
        description=_('Output the segments in the specified files to text files').encode('utf-8'))

    analyze_numbers = model.get_analyze_numbers()

    parser.add_argument('-n',
                        default=False,
                        required=False,
                        action='store_true',
                        help=_("extract number-only segments").encode('utf-8'),
                        dest="numbers")

    # Extension
    extension_helptext = _("the extension to add to outfiles").encode('utf-8')
    parser.add_argument('-e',
                        #                        nargs=1,
                        metavar="extension",
                        default=".segs.txt",
                        help=extension_helptext,
                        dest="extension")

    # Files
    extension_helptext = _("one or more files to process").encode('utf-8')
    parser.add_argument('-f',
                        nargs="+",
                        metavar="filename",
                        required=True,
                        help=extension_helptext,
                        dest="files")

    args = parser.parse_args(argv)

    LOGGER.debug(u'arguments: %s', args)

    if analyze_numbers != args.numbers:
        model.set_analyze_numbers(args.numbers)
        analyze_numbers = args.numbers

    extract(args, [unicode(filename, "mbcs")
                             for filename in args.files])

    if analyze_numbers != args.numbers:
        model.set_analyze_numbers(analyze_numbers)

    LOGGER.debug("...Done!")


if __name__ == '__main__':

    main(sys.argv[1:])
