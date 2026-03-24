# coding: UTF8
"""
Enter module description here.

"""

import pycallgraph
import main


if __name__ == '__main__':
    pycallgraph.start_trace()
    main.main()
    pycallgraph.make_dot_graph('callgraph.png')


