# coding: UTF8
"""
Unit test the output_format module

"""

from nose.tools import raises
import AnalyzeAssist.output_format as of
import cStringIO


@raises(AssertionError)
def test_module():
    """Make sure that our module is being picked up in unit tests"""
    assert False


def test_format_num_list():
    formatted = of.format_num([3, 4, 5])
    assert formatted == u"[3, 4, 5]", formatted


def test_format_num_13():
    formatted = of.format_num(13)
    assert formatted == u"13", formatted


def test_format_num_13001():
    formatted = of.format_num(13001)
    assert formatted == u"13,001", formatted


def test_format_num_str_201():
    formatted = of.format_num("201")
    assert formatted == u"201", formatted


def test_format_num_str_20191():
    formatted = of.format_num("20191")
    assert formatted == u"20,191", formatted


def test_format_num_ustr_201():
    formatted = of.format_num(u"201")
    assert formatted == u"201", formatted


def test_format_num_ustr_20101():
    formatted = of.format_num(u"20101")
    assert formatted == u"20,101", formatted


def test_format_num_with_commas():
    formatted = of.format_num(u"20,101")
    assert formatted == u"20,101", formatted


def test_format_num_words():
    formatted = of.format_num(u"spam")
    assert formatted == u"spam", formatted


def test_format_num_jwords():
    formatted = of.format_num("ポーク")
    assert formatted == u"ポーク", formatted


def test_format_num_nums_then_words():
    formatted = of.format_num(u"123spam")
    assert formatted == u"123spam", formatted


def test_col_len_english():
    cl = of.col_len
    assert cl("spam") == 4, cl("spam")
    assert cl(u"eggs") == 4, cl(u"eggs")


def test_col_len_japanese():
    cl = of.col_len
    assert cl(u"日本語") == 6, cl(u"日本語")
    assert cl(u"日本") == 4, cl(u"日本")
    assert cl(u"本") == 2, cl(u"本")


def test_col_len_mixed():
    cl = of.col_len
    assert cl(u"日本語 spam") == 11, cl(u"日本語 spam")
    assert cl(u"eggs and 日本") == len(u"eggs and 日本") + 2, cl(u"日本")
    assert cl(u"my 本") == 5, cl(u"本")


def test_print_row():
    out = cStringIO.StringIO()
    row = [u"spam", u"eggs", u"bacon", u"beans"]
    of.print_row(row, out)

    val = out.getvalue()

    assert val == u'''<tr>
<td><b>spam</b></td>
<td align="right">eggs</td>
<td align="right">bacon</td>
<td align="right">beans</td>
</tr>
''', "\n[%s]" % val


def test_printRow2():
    buffer = cStringIO.StringIO()

    row = ["abc", "1234"]

    of.print_row(row, buffer)

    val = buffer.getvalue()

    assert val == """<tr>
<td><b>abc</b></td>
<td align="right">1,234</td>
</tr>
""", val
