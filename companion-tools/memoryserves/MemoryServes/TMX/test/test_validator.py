#coding: UTF8

from MemoryServes.TMX import validator
from cStringIO import StringIO as si
from nose.tools import raises

SAMPLEDOC = r"""<?xml version="1.0"?>
<!-- Example of TMX document -->
<tmx version="1.4">
 <header
  creationtool="XYZTool"
  creationtoolversion="1.01-023"
  datatype="PlainText"
  segtype="sentence"
  adminlang="en-us"
  srclang="EN"
  o-tmf="ABCTransMem"
  creationdate="20020101T163812Z"
  creationid="ThomasJ"
  changedate="20020413T023401Z"
  changeid="Amity"
  o-encoding="iso-8859-1"
 >
  <note>This is a note at document level.</note>
  <prop type="RTFPreamble">{\rtf1\ansi\tag etc...{\fonttbl}</prop>
  <ude name="MacRoman" base="Macintosh">
   <map unicode="#xF8FF" code="#xF0" ent="Apple_logo" subst="[Apple]"/>
  </ude>
 </header>
 <body>
  <tu
   tuid="0001"
   datatype="Text"
   usagecount="2"
   lastusagedate="19970314T023401Z"
  >
   <note>Text of a note at the TU level.</note>
   <prop type="x-Domain">Computing</prop>
   <prop type="x-Project">P&#x00E6;gasus</prop>
   <tuv
    xml:lang="EN"
    creationdate="19970212T153400Z"
    creationid="BobW"
   >
    <seg>data (with a non-standard character: &#xF8FF;).</seg>
   </tuv>
   <tuv
    xml:lang="FR-CA"
    creationdate="19970309T021145Z"
    creationid="BobW"
    changedate="19970314T023401Z"
    changeid="ManonD"
   >
    <prop type="Origin">MT</prop>
    <seg>donn&#xE9;es (avec un caract&#xE8;re non standard: &#xF8FF;).</seg>
   </tuv>
  </tu>
  <tu
   tuid="0002"
   srclang="*all*"
  >
   <prop type="Domain">Cooking</prop>
   <tuv xml:lang="EN">
    <seg>menu</seg>
   </tuv>
   <tuv xml:lang="FR-CA">
    <seg>menu</seg>
   </tuv>
   <tuv xml:lang="FR-FR">
    <seg>menu</seg>
   </tuv>
  </tu>
 </body>
</tmx>"""

class TestSampleDoc:
    def test_validate_data(self):
        assert validator.validate_data(si(SAMPLEDOC)), "Sample file should validate"
    def test_rule_1_1_xml_compliance(self):
        assert validator.rule_1_1_xml_compliance(si(SAMPLEDOC)), "Sample file should validate"
    def test_rule_1_2_character_encoding(self):
        assert validator.rule_1_2_character_encoding(si(SAMPLEDOC)), "Sample file should validate"
    def test_rule_2_general_structure(self):
        assert validator.rule_2_general_structure(si(SAMPLEDOC)), "Sample file should validate"

class TestRuleCharacterEncoding:
    def test_utf16(self):
        text = chr(0xFF) + chr(0xFE) + chr(0x34) + chr(0x02)
        assert validator.rule_1_2_character_encoding(si(text)), text.decode("utf-16").encode("utf-8")
    def test_utf8(self):
        text = "日本語"
        assert validator.rule_1_2_character_encoding(si(text)), text.decode("utf-16").encode("utf-8")
    @raises(validator.TmxValidationError)
    def test_sjis(self):
        text = u"日本語".encode("sjis")
        validator.rule_1_2_character_encoding(si(text))

class TestRuleGeneralStructure:
    def test_basic(self):
        text = """<?xml version="1.0"?>
    <!-- Example of TMX document -->
    <tmx version="1.4">
    <header></header>
    <body></body>
    </tmx>"""
        validator.rule_2_general_structure(si(text))

    @raises(validator.TmxValidationError)
    def test_no_root(self):
        text = """<?xml version="1.0"?>
    <!-- Example of TMX document -->
    <not_tmx>
    <header></header>
    <body></body>
    </not_tmx>"""
        validator.rule_2_general_structure(si(text))

    @raises(validator.TmxValidationError)
    def test_three_children(self):
        text = """<?xml version="1.0"?>
    <!-- Example of TMX document -->
    <tmx version="1.4">
    <header></header>
    <body></body>
    <other></other>
    </tmx>"""
        validator.rule_2_general_structure(si(text))

    @raises(validator.TmxValidationError)
    def test_no_header(self):
        text = """<?xml version="1.0"?>
    <!-- Example of TMX document -->
    <tmx version="1.4">
    <not_header></not_header>
    <body></body>
    </tmx>"""
        validator.rule_2_general_structure(si(text))

    @raises(validator.TmxValidationError)
    def test_no_body(self):
        text = """<?xml version="1.0"?>
    <!-- Example of TMX document -->
    <tmx version="1.4">
    <header></header>
    <not_body></not_body>
    </tmx>"""
        validator.rule_2_general_structure(si(text))

