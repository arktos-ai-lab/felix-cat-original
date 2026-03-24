#coding: UTF8
"""
Unit tests for chunker module

"""

from segmenter import chunker

from nose.tools import raises
import segmenter.AppUtils

@raises(AssertionError)
def test_module():
    assert False

def test_SegLinesToRules():
    """Make sure we excercise all the line types"""

    lines = ["spam = true\n", "eggs = false\n", "bacon = Norwegian Blue\n"]

    rules = chunker.seg_lines2rules(lines)

    assert rules["spam"] == True
    assert rules["eggs"] == False
    assert rules["bacon"] == "Norwegian Blue"

def test_getSegmentationRules():
    """Make sure that get_segmentation_rules returns the expected dictionary"""

    rules = chunker.get_segmentation_rules()

    assert len(rules.keys()) == 3, rules.keys()

    for char in u".!?。．！？":
        assert char in rules["StopChars"], rules["StopChars"]
    assert rules["SegControlChars"] == True


def test_is_num():

    # numbers
    assert chunker.is_num(35)
    assert chunker.is_num(1.35)
    assert chunker.is_num("35")
    assert chunker.is_num("1.35")

    assert chunker.is_num(-35)
    assert chunker.is_num(-1.35)
    assert chunker.is_num("-35")
    assert chunker.is_num("-1.35")

def test_is_num_comma():
    # numbers with commas
    assert chunker.is_num("1,000")
    assert chunker.is_num("1,001.35")

def test_is_num_non_numbers():
    # non-numbers
    assert not chunker.is_num("spam 35")
    assert not chunker.is_num("spam 1.35")

    assert not chunker.is_num("35a")
    assert not chunker.is_num("1.35a")

    assert not chunker.is_num("35 spam")
    assert not chunker.is_num("1.35 spam")

def test_is_asian():

    idb = chunker.is_asian

    assert idb(u'漢'), ord(u'漢')
    assert not idb(unichr(0x03A6)), unichr(0x03A6)

def test_is_asian_half_kata():
    idb = chunker.is_asian

    for char in u"ｶﾀｶﾅ":
        assert idb(char), ord(char)

def test_is_asian_hiragana():
    idb = chunker.is_asian

    for char in u"ひらがなあいうえおかきくけこ":
        assert idb(char), ord(char)

def dest_is_asian_katakana():
    idb = chunker.is_asian

    for char in u"カタカナアメリカヨーロッパ":
        assert idb(char), ord(char)

def dest_is_asian_jpunct():
    idb = chunker.is_asian

    for char in u"。「」『』【】、，．（）・／":
        assert idb(char), ord(char)

def test_is_asian_kanji():
    idb = chunker.is_asian

    for char in u"日本語中国南米":
        assert idb(char), "%s %d" % (char, ord(char))

def test_is_asian_ascii():
    idb = chunker.is_asian

    for char in u"AZ! \n~=ac123":
        assert not idb(char), char

class test_Chunker:
    """test the Chunker class"""

    def setup(self):
        self.splitter = chunker.Chunker()

    def test_simplecreate(self):
        assert not 'B' in self.splitter.sentence_end_markers

        assert not '1' in self.splitter.stop_chars

        assert u'。' in self.splitter.stop_chars

    def test_get_sentences(self):

        assert self.splitter.seg_on_control_chars

        assert [x for x in self.splitter.get_sentences("spam and eggs\n")] == ["spam and eggs"]

        chunks = [x for x in self.splitter.get_sentences("my name is\tgeorge\n")]
        assert chunks == ["my name is", "george"], chunks

    def test_mid_sentence_period(self):

        chunks = [x for x in self.splitter.get_sentences("I own 1.3 mansions")]
        assert chunks == ["I own 1.3 mansions"], chunks

    def test_getChunkSentences(self):

        text = "abc. def."
        chunks = [x for x in self.splitter.get_sentences(text)]
        assert chunks == ["abc.", "def."], chunks

    def test_get_sentencesWithQuotes(self):

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it."')]
        assert chunks == ['I said, "stop it."'], chunks

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it." Really')]
        assert chunks == ['I said, "stop it."', 'Really'], chunks

    def test_get_sentencesWithQuotesExlamation(self):

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it!" Really.')]
        assert chunks == ['I said, "stop it!"', "Really."], chunks

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it!" Like, dude!')]
        assert chunks == ['I said, "stop it!"', 'Like, dude!'], chunks

    def test_get_sentencesWithQuotesExlamation(self):

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it?" Really.')]
        assert chunks == ['I said, "stop it?"', "Really."], chunks

        chunks = [x for x in self.splitter.get_sentences('I said, "stop it?" Like, dude?')]
        assert chunks == ['I said, "stop it?"', 'Like, dude?'], chunks

    def test_JapaneseChunks(self):

        chunks = [x for x in self.splitter.get_sentences(u'日本語')]
        assert len(chunks) == 1, len(chunks)
        assert chunks[0] == u'日本語', chunks[0].encode('utf8')

        chunks = [x for x in self.splitter.get_sentences(u'日本語。日本語')]
        print
        assert chunks == [u'日本語。',u'日本語'], chunks

    def test_get_sentencesWithOKEndings(self):

        chunks = [x for x in self.splitter.get_sentences('This is Mr. Smith.')]
        expected = ['This is Mr. Smith.']
        assert chunks == expected, "Expected %s but actually %s" % (str(expected), str(chunks))

        chunks = [x for x in self.splitter.get_sentences('Bananas, etc. are cool.')]
        assert chunks == ['Bananas, etc.', 'are cool.']

    def test_AbbreviationEndOneSentence(self):

        text = u"I live in the U.S.A."
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"I live in the U.S.A."]
        assert sentences == expected, sentences

    def test_AbbreviationEndTwoSentences(self):

        text = u"I live in the U.S.A. It is in North America"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"I live in the U.S.A.", u"It is in North America"]
        assert sentences == expected, sentences

    def test_AbbreviationMiddle(self):

        text = u"The U.S. is in North America"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"The U.S. is in North America"]
        assert sentences == expected, sentences

    def test_sentence_then_parens(self):

        text = u"The U.S. is in North America. (Not that you'd notice)"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"The U.S. is in North America.", u"(Not that you'd notice)"]
        assert sentences == expected, sentences

    def test_qm_then_parens(self):

        text = u"The U.S. is in North America? (Not that you'd notice)"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"The U.S. is in North America?", u"(Not that you'd notice)"]
        assert sentences == expected, sentences

    def test_sentence_with_tabs(self):

        text = u"Come to papa\tNo, come to butthead!"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"Come to papa", u"No, come to butthead!"]
        assert sentences == expected, sentences

    def test_rightquotes_single(self):
        text = u"'Come to papa.' No, come to butthead!"
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u"'Come to papa.'", u"No, come to butthead!"]
        assert sentences == expected, sentences

    def test_rightquotes_double(self):
        text = u'"Come to papa." No, come to butthead!'
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u'"Come to papa."', u"No, come to butthead!"]
        assert sentences == expected, sentences

    def test_rightquotes_ascii_smart(self):
        text = u'"Come to papa.%s No, come to butthead!' % unichr(0x133)
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u'"Come to papa.\u0133',
                    u"No, come to butthead!"]
        assert sentences == expected, sentences

    def test_rightquotes_uni_smart(self):
        text = u'"Come to papa.%s No, come to butthead!' % unichr(0x8230)
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u'"Come to papa.\u8230',
                    u"No, come to butthead!"]
        assert sentences == expected, sentences

    def test_simple_dot_dot_dot_one(self):
        text = u'I luv New York...'
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u'I luv New York...']
        assert sentences == expected, sentences

    def test_simple_dot_dot_dot_two(self):
        text = u'I luv New York... And so does I'
        sentences = [x for x in self.splitter.get_sentences(text)]
        expected = [u'I luv New York...', u'And so does I']
        assert sentences == expected, sentences


class TestHasOkEnding(object):

    def test_mr(self):
        assert chunker.has_ok_ending("Hello Mr.")
    def test_mrs(self):
        assert chunker.has_ok_ending("Hello Mrs.")
    def test_ms(self):
        assert chunker.has_ok_ending("Hello Ms.")
    def test_dr(self):
        assert chunker.has_ok_ending("Hello Dr.")
    def test_etc(self):
        assert not chunker.has_ok_ending("Fishes, etc.")
    def test_smith(self):
        assert not chunker.has_ok_ending("Hello Mr. Smith.")
    def test_bob(self):
        assert not chunker.has_ok_ending("Hello Bob.")
