# coding: UTF8
"""Unit test the module, with coverage
"""

import os
import glob
import sys
import model


def ok_file(filename):
    for prefix in '__init__', 'test', 'setup':
        if filename.lower().startswith(prefix):
            return False
    return True


def coverFromList(files):
    """e.g. [module.py] -> [module]"""
    out = []
    for name in files:
        if ok_file(name):
            module = name.split('.')[0]
            out.append('--cover-package=AnalyzeAssist.' + module)
    out.append('--cover-package=AnalyzeAssist.segmenter')
    out.append('--cover-package=AnalyzeAssist.controller')
    out.append('--cover-package=AnalyzeAssist.view')
    return out


#Get the packages we want to get coverage for
def getCoverPackages():
    """Retrieve the python files in the current working directory
    that do not start with "test."
    
    These are the files for which we will collect coverage stats
    """

    os.chdir(os.path.dirname(__file__))

    return coverFromList(glob.glob("*.py"))


def main():
    import nose

    import psyco

    psyco.full()

    sys.exit(nose.main(argv=['--with-coverage'] + getCoverPackages()))


if __name__ == '__main__':
    from AnalyzeAssist import AppUtils

    main()