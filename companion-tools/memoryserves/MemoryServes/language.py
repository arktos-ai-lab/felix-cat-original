#!/usr/bin/env python

LANG_CODES = (("Afrikaans", "AF"),
    ("Albanian", "SQ"),
    ("Arabic", "AR"),
    ("Basque", "EU"),
    ("Bulgarian", "BG"),
    ("Byelorussian", "BE"),
    ("Catalan", "CA"),
    ("Chinese Simplified", "ZH-CN"),
    ("Chinese Traditional", "ZH-TW"),
    ("Croatian", "HR"),
    ("Czech", "CS"),
    ("Danish", "DA"),
    ("Dutch", "NL"),
    ("English", "EN"),
    ("English (United States)", "EN-US"),
    ("English (United Kingdom)", "EN-GB"),
    ("English (Australia)", "EN-AU"),
    ("English (Canada)", "EN-CA"),
    ("English (New Zealand)", "EN-NZ"),
    ("English (Ireland)", "EN-IE"),
    ("Estonian", "ET"),
    ("Faeroese", "FO"),
    ("Finnish", "FI"),
    ("French", "FR"),
    ("Gaelic", "GA"),
    ("Gaelic (Ireland)", "GA-IE"),
    ("German", "DE"),
    ("Greek", "EL"),
    ("Hebrew", "IW"),
    ("Hungarian", "HU"),
    ("Icelandic", "IS"),
    ("Indonesian", "IN"),
    ("Italian", "IT"),
    ("Japanese", "JA"),
    ("Kampuchean", "KA"),
    ("Korean", "KO"),
    ("Laothian", "LO"),
    ("Latvian, Lettish", "LV"),
    ("Lithuanian", "LT"),
    ("Macedonian", "MK"),
    ("Maltese", "MT"),
    ("Maori", "MI"),
    ("Norwegian", "NO"),
    ("Polish", "PL"),
    ("Portuguese", "PT"),
    ("Punjabi", "PA"),
    ("Rhaeto-Romance", "RM"),
    ("Romanian", "RO"),
    ("Russian", "RU"),
    ("Serbo-Croatian", "SH"),
    ("Slovak", "SK"),
    ("Slovenian", "SL"),
    ("Serbian", "SO"),
    ("Spanish", "ES"),
    ("Swedish", "SV"),
    ("Thai", "TH"),
    ("Tsonga", "TS"),
    ("Turkish", "TR"),
    ("Ukrainian", "UK"),
    ("Urdu", "UR"),
    ("Vietnamese", "VI"),
    )


def get_code(lang):
    """
    Get the language code for a given lanugage string
    """

    if lang == "Default":
        return None
    for name, code in LANG_CODES:
        if lang == name or lang == code:
            return code
    return None

def get_codes(source, trans):
    """
    Get the language codes for the source and translation
    """

    return get_code(source), get_code(trans)
