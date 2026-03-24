__author__ = 'Ryan'

import string
import itertools
import wchartype

def has_asian(text):
    """
    `text` is a Unicode string.
    """

    is_asian = wchartype.is_asian # hoist for speed
    return any(is_asian(x) for x in text)

def get_ascii_char_type(c):
    if c.isdigit():
        return "digit"
    if c.isalpha():
        return "letter"
    if c in string.punctuation:
        return "punctuation"
    if c.isspace():
        return "space"

    return "sbc"

def get_char_type(c):
    # dbc "ascii"
    if wchartype.is_full_digit(c):
        return "full digit"
    if wchartype.is_full_letter(c):
        return "full letter"
    if wchartype.is_full_punct(c):
        return "full punctuation"

    # Japanese (Chinese for kanji)
    if wchartype.is_half_katakana(c):
        return "half katakana"
    if wchartype.is_katakana(c):
        return "katakana"
    if wchartype.is_hiragana(c):
        return "hiragana"
    if wchartype.is_kanji(c):
        return "kanji"

    # Korean
    if wchartype.is_hangul(c):
        return "hangul"

    # dbc space
    if ord(c) == wchartype.IDEOGRAPHIC_SPACE:
        return "dbc space"

    return get_ascii_char_type(c)

def tokenize_chunk(chunk):
    tokens = []
    current_token = []
    current_char_type = None
    for c in chunk:
        char_type = get_char_type(c)
        if char_type != current_char_type:
            if current_token:
                tokens.append(u"".join(current_token))
                current_token = []
            current_char_type = char_type
        current_token.append(c)
    if current_token:
        tokens.append(u"".join(current_token))
    return tokens

def tokenize(text):
    return list(itertools.chain(*[tokenize_chunk(chunk) for chunk in text.split()]))
