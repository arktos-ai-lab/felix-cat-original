#coding: UTF8
"""
Enter module description here.

"""
import os
import hotshot, hotshot.stats

os.chdir(os.path.dirname(__file__))

stats = hotshot.stats.load("unittest.prof")
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(40)
