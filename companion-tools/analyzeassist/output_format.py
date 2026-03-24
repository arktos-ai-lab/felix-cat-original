# coding: UTF8
"""
Various functions for formatting output.

"""
import locale
from segmenter.chunker import is_asian


def format_num(num):
    """Format a number according to given places

    @param num: A number (either string or int) to format

    Format a number according to locality and given places

    >>> format_num("spam日本語")
    u'spam\\u65e5\\u672c\\u8a9e'

    """
    locale.setlocale(locale.LC_ALL, "English_US")
    try:
        inum = int(num)
        return locale.format("%.*f", (0, inum), True)

    except (ValueError, TypeError):
        if not isinstance(num, unicode):
            return unicode(str(num), "utf8")
        else:
            return num


def num_asian_chars(col):
    """Returns the number of Asian characters in col

    >>> num_asian_chars(u'spam\u65e5\u672c')
    2
    """

    formatted_num = format_num(col)
    return sum(1 for c in formatted_num if is_asian(c))


def col_len(column):
    """Returns the length of the column.

    The length of the column is the number of total characters plus
    the number of Asian characters (so each Asian character is counted as 2)

    >>> col_len("spam")
    4
    >>> col_len(u'spam\u65e5\u672c')
    8
    """

    formatted_num = format_num(column)
    return len(formatted_num) + num_asian_chars(column)


def max_width(data, index):
    """Returns the maximum width of the table for column index

    >>> data = [["a", "ab", "abc"], ["abcd", "abcde", "ab"]]
    >>> max_width(data, 0)
    4
    >>> max_width(data, 1)
    5
    >>> max_width(data, 2)
    3

    """

    return max(col_len(row[index]) for row in data)


def print_row_txt(row, col_paddings, out, encoding="utf-8"):
    """Prints a table row

    @param row: The sequence of row columns. The first element is the row heading
    @param outfile: a file-like object for output
    @param col_paddings: Column paddings for pretty output
    """

    pad = col_paddings[0] - num_asian_chars(row[0])
    print >> out, row[0].ljust(pad + 2).encode(encoding),
    for i in range(1, len(row)):
        pad = col_paddings[i] - num_asian_chars(row[i])
        col = format_num(row[i]).rjust(pad + 2)
        print >> out, col,
    print >> out


def print_row(row, out, col_tag="td", encoding="utf-8"):
    """Prints a table row for HTML output

    @param row: The row of data to print
    @param out: The output file-like object
    @param col_tag: The tag to give each column (e.g. th/td)
    """

    title, cols = row[0], row[1:]
    print >> out, "<tr>"
    print >> out, "<%s><b>%s</b></%s>" % (col_tag,
                                          title.encode(encoding),
                                          col_tag)
    for col in cols:
        col_text = format_num(col).encode("utf8")
        print >> out, "<%s align=\"right\">%s</%s>" % (col_tag,
                                                       col_text,
                                                       col_tag)
    print >> out, "</tr>"


def _test():
    """Run doctests on module"""
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
