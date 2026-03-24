#coding: UTF8
"""
Unit test the html segmenter

"""

from nose.tools import raises

from segmenter import htmlseg
from segmenter.htmlseg import Segmenter
import cStringIO

@raises(AssertionError)
def test_module():
    """Make sure the module's tests are getting picked up"""

    assert False


def test_normalize():
    """test function normalize"""

    assert htmlseg.normalize(u'foo\tbar') == u'foo bar'
    assert htmlseg.normalize(u'foo') == u'foo'
    assert htmlseg.normalize(u'foo  bar') == u'foo bar'
    assert htmlseg.normalize(u'foo\t\n\tbar') == u'foo bar'


class TestGetEncoding:
    def test_sjis(self):
        text = u"""<html><body><p>日本語は難しい！</p></body></html>""".encode("sjis")
        actual = htmlseg.get_encoding(text)
        assert "SHIFT_JIS" == actual, actual

    def test_ascii(self):
        text = """<html><body><p>hello</p></body></html>"""
        actual = htmlseg.get_encoding(text)
        assert "ascii" == actual, actual


class TestHtml:
    """test class htmlseg.Segmenter"""

    def setup(self):
        wanted = ["a title".split(),
                  "img alt".split(),
                  "input value".split(),
                  "meta description".split(),
                  "meta keywords".split()]

        self.segmenter = Segmenter(wanted_attrs=wanted)

    def testStr(self):

        assert u"HTML" == str(self.segmenter)

    def test_nbsp(self):

        text = "<html><body>Here is a sentence.&nbsp;Here is another.</body></html>"

        chunks = list(self.segmenter.parseChunks(cStringIO.StringIO(text), "sjis"))

        assert chunks == [u"Here is a sentence.", u"Here is another."], chunks

    def test_withTitle(self):

        text = """
        <html>
            <head>
                <title>foo</title>
            </head>
            <body>
                <p>bar</p>
            </body>
        </html>"""

        segs = list(self.segmenter.parseChunks(text, "ascii"))

        expected = [u"foo", u"bar"]

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_attributes(self):

        text = """
        <html>
            <head>
                <title>abc</title>
            </head>
            <body>
                <p><img src="img.jpg" alt="abcdef" /></p>
                <p><a href="foo.html" title="def">def</a></p>
                <form method="post" action="." name="searchform">
                        <input type="submit" value="ghi" class="submit" />
                </form>
            </body>
        </html>"""

        segs = set(self.segmenter.parseChunks(text, "ascii"))

        expected = set([u"abc",
                    u"abcdef", # <img alt
                    u"def", # <a title
                    u"ghi", # <input value
                    u"def"])

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_with_newline(self):

        text = """<html>
<body>
<p>This should be one
sentence.</p>
</body>
</html>"""

        segs = list(self.segmenter.parseChunks(text, "ascii"))

        expected = [u"This should be one sentence."]

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_with_tab(self):

        text = """<html>
<body>
<p>This should be one	sentence.</p>
</body>
</html>"""

        segs = list(self.segmenter.parseChunks(text, "ascii"))

        expected = [u"This should be one sentence."]

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_empty(self):

        segs = list(self.segmenter.parseChunks("", "ascii"))

        expected = []

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_list(self):

        text = """<html>
<body>
<ol>
<li>abc
<li>def
<li>123
</ol>
<ul>
<li class="foo">foo</li>
<li class="bar">bar</li>
</ul>
</body>
</html>"""
        self.segmenter.chunking_strategy.analyze_numbers = False

        segs = list(self.segmenter.parseChunks(text, "ascii"))

        expected = [u"abc",u"def",u"foo",u"bar"]

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_table(self):
        text = """
        <html>
            <head>
            </head>
            <body>
                <table>
                    <tr><th>abc</th><th>def</th></tr>
                    <tr><td>foo</td><td>bar</td</tr>
                </table>
            </body>
        </html>
        """
        segs = set(self.segmenter.parseChunks(text, "ascii"))

        expected = set([u"abc",u"def",u"foo",u"bar"])

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))


    def test_tag_without_attributes(self):

        text = """<html>
        <head>
        </head>
        <body>
        <p><img src="img.jpg" /></p>
        <p><a href="foo.html">def</a></p>
        <form method="post" action="." name="searchform">
                <input type="submit" value="ghi" class="submit" />
        </form>
        </body>
        </html>"""

        segs = list(self.segmenter.parseChunks(text, "ascii"))

        expected = u"ghi def".split()

        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_description_and_keywords(self):
        text = """
        <html>
            <head>
                <meta description="spam" />
                <meta keywords="egg" />
            </head>
            <body>
            </body>
        </html>
        """
        segs = set(self.segmenter.parseChunks(text, "ascii"))
        expected = set("spam egg".split())
        assert segs == expected, (segs, expected)
    def test_input_value(self):
        text = """
        <html>
            <head>
            </head>
            <body>
               <input value="spam" />
            </body>
        </html>
        """
        segs = list(self.segmenter.parseChunks(text, "ascii"))
        expected = ["spam"]
        assert segs == expected, (segs, expected)

class TestAttributeSettings:
    def test_a_title_true(self):
        text = """
        <html>
        <body><a href="foo.html" title="foo">bar</a></body>
        </html>"""

        htmlseg.WANT_A_TITLE = True
        segs = set(htmlseg.Segmenter().parseChunks(text, "ascii"))
        expected = set("foo bar".split())
        assert segs == expected, (segs, expected)

    def test_a_title_false(self):
        text = """
        <html>
        <body><a href="foo.html" title="foo">bar</a></body>
        </html>"""

        htmlseg.WANT_A_TITLE = False
        segs = list(htmlseg.Segmenter().parseChunks(text, "ascii"))
        expected = ["bar"]
        assert segs == expected, (segs, expected)

    def test_a_title_true_params(self):
        text = """
        <html>
        <body><a href="foo.html" title="foo">bar</a></body>
        </html>"""

        htmlseg.WANT_A_TITLE = False
        segs = set(htmlseg.Segmenter(wanted_attrs=["a title".split()]).parseChunks(text, "ascii"))
        expected = set("foo bar".split())
        assert segs == expected, (segs, expected)

    def test_a_title_false_params(self):
        text = """
        <html>
        <body><a href="foo.html" title="foo">bar</a></body>
        </html>"""

        htmlseg.WANT_A_TITLE = True
        segs = list(htmlseg.Segmenter(wanted_attrs=[]).parseChunks(text, "ascii"))
        expected = ["bar"]
        assert segs == expected, (segs, expected)

    def test_meta_description_true(self):
        text = """
        <html>
        <head><meta description="foo" /></head>
        <body><p>bar</p></body>
        </html>"""

        htmlseg.WANT_META_DESCRIPTION = True
        segs = set(htmlseg.Segmenter().parseChunks(text, "ascii"))
        expected = set("foo bar".split())
        assert segs == expected, (segs, expected)

    def test_meta_description_false(self):
        text = """
        <html>
        <head><meta description="foo" /></head>
        <body><p>bar</p></body>
        </html>"""

        htmlseg.WANT_META_DESCRIPTION = False
        segs = list(htmlseg.Segmenter().parseChunks(text, "ascii"))
        expected = ["bar"]
        assert segs == expected, (segs, expected)

    def test_meta_description_true_params(self):
        text = """
        <html>
        <head><meta description="foo" /></head>
        <body><p>bar</p></body>
        </html>"""

        htmlseg.WANT_META_DESCRIPTION = False
        segs = set(htmlseg.Segmenter(wanted_attrs=["meta description".split()]).parseChunks(text, "ascii"))
        expected = set("foo bar".split())
        assert segs == expected, (segs, expected)

    def test_meta_description_false_params(self):
        text = """
        <html>
        <head><meta description="foo" /></head>
        <body><p>bar</p></body>
        </html>"""

        htmlseg.WANT_META_DESCRIPTION = True
        segs = list(htmlseg.Segmenter(wanted_attrs=[]).parseChunks(text, "ascii"))
        expected = ["bar"]
        assert segs == expected, (segs, expected)


class TestStripTags:

    def test_bold(self):

        expected = u"Hello, world!"
        actual = htmlseg.strip_tags(u"<b>Hello, world!</b>")

        assert actual == expected, (actual,expected)

    def test_bold_italic(self):
        expected = u"Hello, world!"
        actual = htmlseg.strip_tags(u"<b><i>Hello, world!</i></b>")

        assert actual == expected, (actual,expected)

    def test_bold_br(self):
        expected = u"Hello, world!"
        actual = htmlseg.strip_tags(u"<b>Hello, world!</b><br />")

        assert actual == expected, (actual,expected)

    def test_bold_italic_nested(self):
        expected = u"Hello, world!"
        actual = htmlseg.strip_tags(u"<b>Hello, <i>world!</i></b>")

        assert actual == expected, (actual,expected)

    def test_comment(self):
        expected = u"Hello, world!"
        actual = htmlseg.strip_tags(u"<!-- comment here -->Hello, world!")

        assert actual == expected, (actual,expected)

    def test_nbsp(self):
        expected = u"Hello,&nbsp;world!"
        actual = htmlseg.strip_tags(u"Hello,&nbsp;world!")

        assert actual == expected, (actual,expected)

class TestHtml2Plain:

    def test_nbsp(self):
        expected = u"Hello,\xa0world!"
        actual = htmlseg.html2plain(u"Hello,&nbsp;world!")

        assert actual == expected, (actual,expected)

    def test_ndash(self):
        expected = u"spam\u2013eggs"
        actual = htmlseg.html2plain(u"spam&ndash;eggs")

        assert actual == expected, (actual,expected)
