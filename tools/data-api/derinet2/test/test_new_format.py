import unittest
import io
from derinet import Lexicon, DerinetError, DerinetFileParseError, Format
from derinet.relation import CompoundRelation, ConversionRelation


class TestNewFormat(unittest.TestCase):
    def test_load_empty(self):
        db = ""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 0)

    def test_load_single_lexeme(self):
        db = """0.0	0	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 1)
        self.assertEqual(list(lexicon.iter_lexemes())[0].lemma, "lexeme")

    def test_load_missing_json_error(self):
        db = """0.0	lexeme#N	lexeme	N						
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_missing_lemma_error(self):
        db = """0.0	lexeme#N		N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_missing_lemid_error(self):
        """
        The lemids are not strictly necessary. They may actually be empty.
        """
        db = """0.0		lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

    def test_load_no_trailing_newline(self):
        db = """0.0	0	lexeme							{}"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_malformed_id_1(self):
        db = """0	lexeme#N	lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_malformed_id_2(self):
        db = """	lexeme#N	lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_two_lexemes(self):
        db = """0.0	0	lexeme							{}
0.1	1	lexemer				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 2)

    def test_load_duplicate_lemid(self):
        """
        Duplicate lemids are to be expected, at least in Czech, given that
        they are constructed as a lemma+tagmask combination. Many homonyms
        share the same lemid.
        """
        db = """0.0	0	lexeme							{}
0.1	0	lexemer				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

    def test_load_duplicate_id_1(self):
        db = """0.0	0	lexeme							{}
0.1	1	lexemer				0.0	Type=Derivation		{}
0.1	2	lexemes				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_id_2(self):
        db = """0.0	0	lexeme							{}

0.0	1	lexemer							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_load(self):
        """
        Since there is no distinguishing feature to the lexeme, there is no way
        of detecting duplicities. If we used the ID for that, we would effectively
        disable loading multiple databases into a single Lexicon instance.
        """
        db = """0.0	0	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)
        db_file.seek(0)

        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 2)

    def test_load_two_dbs(self):
        db1 = """0.0	0	lexeme							{}
"""
        db2 = """1.0	1	word							{}
"""

        lexicon = Lexicon()
        db_file_1 = io.StringIO(db1)
        db_file_2 = io.StringIO(db2)

        lexicon.load(db_file_1)
        lexicon.load(db_file_2)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 2)

    def test_load_conjoined_trees_1(self):
        """
        In this test, we check that the loader rejects a file in which
        two trees are written without a blank line between them.
        """
        db = """0.0	0	lexeme							{}
1.1	1	word							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_conjoined_trees_2(self):
        db = """0.0	0	lexeme							{}
1.1	1	word				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_id(self):
        db = """0.0	0	lexeme							{}
0.0	1	word							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_self_reference(self):
        db = """0.0	0	lexeme				0.0	Type=Derivation		{}
        """

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_forward_reference(self):
        db = """0.0	0	lexemer				0.1	Type=Derivation		{}
0.1	1	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_out_of_tree_reference(self):
        """
        Cross-tree references are only allowed in secondary links, not in primary ones.
        """
        db = """0.0	0	lexeme							{}

1.0	1	lexemer				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_split_tree_1(self):
        db = """0.0	0	lexeme							{}

0.1	1	lexemer				0.0	Type=Derivation		{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_split_tree_2(self):
        db = """0.0	0	lexeme							{}

0.1	1	lexemer							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_child_before_parent(self):
        db = """0.1	0	lexemer				0.0	Type=Derivation		{}
0.0	1	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_segmentation(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Start=0&Type=Prefix|End=8&Start=6|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 3)

    def test_load_segmentation_noninteger_start(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Start=0.1&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_noninteger_end(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6a&Morph=aachen&Start=0&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 3)

    def test_load_segmentation_missing_end(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Start=0&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 3)

    def test_load_segmentation_missing_start_end(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=sk&Type=Root|Morph=ost&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 3)

    def test_load_segmentation_missing_start_end_nonmatching_1(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=sko&Type=Root|Morph=ost&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start_end_nonmatching_2(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=s&Type=Root|Morph=ost&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start_end_nonmatching_3(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=k&Type=Root|Morph=ost&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start_end_nonmatching_4(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=sko&Type=Root|Morph=os&Type=Suffix|Morph=t&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start_end_noncontiguous_1(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|Morph=os&Start=8&Type=Suffix|Morph=t&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 4)
        self.assertEqual(10, lexeme.segmentation[2]["End"])

    def test_load_segmentation_missing_start_end_noncontiguous_2(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Type=Prefix|End=10&Morph=os&Type=Suffix|Morph=t&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 4)
        self.assertEqual(8, lexeme.segmentation[2]["Start"])

    def test_save_segmentation(self):
        db = """0.0	Aachen#N	Aachen	N						{}

1.0	aachenskost#N	aachenskost	N		Morph=aachen&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}

2.0	aachenský#A	aachenský	A		End=8&Morph=sk&Start=6&Type=Suffix|Morph=ý&Type=Suffix				{}
"""

        lexicon = Lexicon()
        lexeme_a = lexicon.create_lexeme("Aachen", "N")
        lexeme_b = lexicon.create_lexeme("aachenský", "A")
        lexeme_c = lexicon.create_lexeme("aachenskost", "N")

        lexeme_b.add_morph(8, 9, {"Type": "Suffix"})
        lexeme_b.add_morph(6, 8, {"Type": "Suffix"})

        lexeme_c.add_morph(0, 6, {"Type": "Root"})
        lexeme_c.add_morph(8, 11, {"Type": "Suffix"})

        db_file = io.StringIO()
        lexicon.save(db_file, fmt=Format.DERINET_V2)

        self.assertMultiLineEqual(db, db_file.getvalue())

    def test_save_segmentation_json(self):
        db = """0.0	Aachen#N	Aachen	N						{}

1.0	aachenskost#N	aachenskost	N		[{"morph": "aachen", "type": "Root"}, {"end": 11, "morph": "ost", "start": 8, "type": "Suffix"}]				{}

2.0	aachenský#A	aachenský	A		[{"end": 8, "morph": "sk", "start": 6, "type": "Suffix"}, {"morph": "ý", "type": "Suffix"}]				{}
"""

        lexicon = Lexicon()
        lexeme_a = lexicon.create_lexeme("Aachen", "N")
        lexeme_b = lexicon.create_lexeme("aachenský", "A")
        lexeme_c = lexicon.create_lexeme("aachenskost", "N")

        lexeme_b.add_morph(8, 9, {"Type": "Suffix"})
        lexeme_b.add_morph(6, 8, {"Type": "Suffix"})

        lexeme_c.add_morph(0, 6, {"Type": "Root"})
        lexeme_c.add_morph(8, 11, {"Type": "Suffix"})

        db_file = io.StringIO()
        lexicon.save(db_file, fmt=Format.DERINET_V2_JSONSEG)

        self.assertMultiLineEqual(db, db_file.getvalue())

    def test_load_relation_features(self):
        db = """0.0	0	lexeme							{}
0.1	1	lexemer				0.0	SemanticLabel=Actor&Type=Derivation		{}
"""

        db_file = io.StringIO(db)
        lexicon = Lexicon()
        lexicon.load(db_file, fmt=Format.DERINET_V2)

        self.assertEqual(2, len(list(lexicon.iter_lexemes())))
        lexemers = lexicon.get_lexemes("lexemer")
        self.assertEqual(1, len(lexemers))
        lexemer = lexemers[0]
        self.assertDictEqual({"SemanticLabel": "Actor"}, lexemer.parent_relation.feats)

    def test_load_compounding(self):
        db = """0.0	buněčný#AA???----??---?	buněčný	A						{}
0.1	vnitrobuněčný#AA???----??---?	vnitrobuněčný	A			0.0	Sources=1.0,0.0&Type=Compounding		{}

1.0	vnitro#NNN??-----A---?	vnitro	N	Gender=Neut					{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        lexicon.load(db_file, fmt=Format.DERINET_V2)

        compound = lexicon.get_lexemes("vnitrobuněčný")[0]
        self.assertIsInstance(compound.parent_relation, CompoundRelation)
        self.assertEqual(2, len(compound.parent_relation.sources))

    def test_load_conversion(self):
        db = """0.0	hajný#AA???----??---?	hajný	A						{}
0.1	hajný#NN???----??---?	hajný	N			0.0	Type=Conversion		{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        lexicon.load(db_file, fmt=Format.DERINET_V2)

        noun = lexicon.get_lexemes("hajný", "N")[0]
        self.assertIsInstance(noun.parent_relation, ConversionRelation)

    def test_load_unknown_reltype(self):
        db = """0.0	hajný#AA???----??---?	hajný	A						{}
0.1	hajný#NN???----??---?	hajný	N			0.0	Type=Blargh		{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file, fmt=Format.DERINET_V2)

    def test_load_unknown_reltype_permissive(self):
        db = """0.0	hajný#AA???----??---?	hajný	A						{}
0.1	hajný#NN???----??---?	hajný	N			0.0	Type=Blargh		{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        with self.assertLogs("derinet", level="WARNING"):
            lexicon.load(db_file, fmt=Format.DERINET_V2, on_err="continue")

        lexemes = lexicon.get_lexemes("hajný")
        self.assertEqual(2, len(lexemes))

    def test_load_missing_reltype(self):
        db = """0.0	hajný#AA???----??---?	hajný	A						{}
0.1	hajný#NN???----??---?	hajný	N			0.0			{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file, fmt=Format.DERINET_V2)

    def test_load_missing_reltype_permissive(self):
        db = """0.0	hajný#AA???----??---?	hajný	A						{}
0.1	hajný#NN???----??---?	hajný	N			0.0			{}
"""
        db_file = io.StringIO(db)
        lexicon = Lexicon()
        with self.assertLogs("derinet", level="WARNING"):
            lexicon.load(db_file, fmt=Format.DERINET_V2, on_err="continue")

        nouns = lexicon.get_lexemes("hajný", "N")
        self.assertEqual(1, len(nouns))

        noun = nouns[0]
        self.assertIsNotNone(noun.parent)
        self.assertEqual("A", noun.parent.pos)

    def test_roundtrip_complex(self):
        db = """0.0	Aachen#NNM??-----A---?	Aachen	N	Animacy=Anim&Gender=Masc&NameType=Sur					{"techlemma": "Aachen_;S"}
0.1	Aachenův#AU???M--------?	Aachenův	A	NameType=Sur&Poss=Yes		0.0	SemanticLabel=Possessive&Type=Derivation		{"techlemma": "Aachenův_;S_^(*2)"}
0.2	aachenský#AA???----??---?	aachenský	A	NameType=Geo		0.0	Type=Derivation		{"techlemma": "aachenský_;G"}
0.3	aachenskost#NNF??-----?---?	aachenskost	N	Gender=Fem&NameType=Geo		0.2	Type=Derivation		{"techlemma": "aachenskost_;G_^(*3ý)"}
0.4	aachensky#Dg-------??---?	aachensky	D	NameType=Geo		0.2	Type=Derivation		{"techlemma": "aachensky_;G_^(*1ý)"}

1.0	buňka#NNF??-----A---?	buňka	N	Gender=Fem					{"techlemma": "buňka"}
1.1	buničina#NNF??-----A---?	buničina	N	Gender=Fem		1.0	Type=Derivation		{"techlemma": "buničina"}
1.2	buničinový#AA???----??---?	buničinový	A			1.1	Type=Derivation		{"techlemma": "buničinový"}
1.3	buničinovost#NNF??-----?---?	buničinovost	N	Gender=Fem		1.2	Type=Derivation		{"techlemma": "buničinovost_^(*3ý)"}
1.4	buničinově#Dg-------??---?	buničinově	D			1.2	Type=Derivation		{"techlemma": "buničinově_^(*1ý)"}
1.5	buněčný#AA???----??---?	buněčný	A			1.0	Type=Derivation		{"techlemma": "buněčný"}
1.6	buněčnost#NNF??-----?---?	buněčnost	N	Gender=Fem		1.5	Type=Derivation		{"techlemma": "buněčnost_^(*3ý)"}
1.7	buněčně#Dg-------??---?	buněčně	D			1.5	Type=Derivation		{"techlemma": "buněčně_^(*1ý)"}
1.8	vnitrobuněčný#AA???----??---?	vnitrobuněčný	A			1.5	Sources=2.12,1.5&Type=Compounding		{"is_compound": true, "techlemma": "vnitrobuněčný"}
1.9	vnitrobuněčnost#NNF??-----?---?	vnitrobuněčnost	N	Gender=Fem		1.8	Type=Derivation		{"techlemma": "vnitrobuněčnost_^(*3ý)"}
1.10	vnitrobuněčně#Dg-------??---?	vnitrobuněčně	D			1.8	Type=Derivation		{"techlemma": "vnitrobuněčně_^(*1ý)"}
1.11	buňkovitý#AA???----??---?	buňkovitý	A			1.0	Type=Derivation		{"techlemma": "buňkovitý"}
1.12	buňkovitost#NNF??-----?---?	buňkovitost	N	Gender=Fem		1.11	Type=Derivation		{"techlemma": "buňkovitost_^(*3ý)"}
1.13	buňkovitě#Dg-------??---?	buňkovitě	D			1.11	Type=Derivation		{"techlemma": "buňkovitě_^(*1ý)"}
1.14	buňkový#AA???----??---?	buňkový	A			1.0	Type=Derivation		{"techlemma": "buňkový"}
1.15	buňkovost#NNF??-----?---?	buňkovost	N	Gender=Fem		1.14	Type=Derivation		{"techlemma": "buňkovost_^(*3ý)"}
1.16	buňkově#Dg-------??---?	buňkově	D			1.14	Type=Derivation		{"techlemma": "buňkově_^(*1ý)"}
1.17	mikrobuňka#NNF??-----A---?	mikrobuňka	N	Gender=Fem		1.0	Type=Derivation		{"techlemma": "mikrobuňka"}

2.0	nitro#NNN??-----A---?	nitro	N	Gender=Neut					{"techlemma": "nitro-1"}
2.1	niterný#AA???----??---?	niterný	A			2.0	Type=Derivation		{"techlemma": "niterný"}
2.2	niternost#NNF??-----?---?	niternost	N	Gender=Fem		2.1	Type=Derivation		{"techlemma": "niternost_^(*3ý)"}
2.3	niterně#Dg-------??---?	niterně	D			2.1	Type=Derivation		{"techlemma": "niterně_^(*1í)"}
2.4	nitrný#AA???----??---?	nitrný	A	Style=Arch		2.0	Type=Derivation		{"techlemma": "nitrný_,a"}
2.5	nitrnost#NNF??-----?---?	nitrnost	N	Gender=Fem&Style=Arch		2.4	Type=Derivation		{"techlemma": "nitrnost_,a_^(*3ý)"}
2.6	nitrně#Dg-------??---?	nitrně	D	Style=Arch		2.4	Type=Derivation		{"techlemma": "nitrně_,a_^(*1ý)"}
2.7	uvnitř#Db-------------	uvnitř	D			2.0	Type=Derivation		{"techlemma": "uvnitř-2"}
2.8	vnitřek#NNI??-----A---?	vnitřek	N	Animacy=Inan&Gender=Masc		2.7	Type=Derivation		{"techlemma": "vnitřek"}
2.9	vnitřkový#AA???----??---?	vnitřkový	A			2.8	Type=Derivation		{"techlemma": "vnitřkový"}
2.10	vnitřkovost#NNF??-----?---?	vnitřkovost	N	Gender=Fem		2.9	Type=Derivation		{"techlemma": "vnitřkovost_^(*3ý)"}
2.11	vnitřkově#Dg-------??---?	vnitřkově	D			2.9	Type=Derivation		{"techlemma": "vnitřkově_^(*1ý)"}
2.12	vnitro#NNN??-----A---?	vnitro	N	Gender=Neut		2.0	Type=Derivation		{"techlemma": "vnitro"}
2.13	dovnitř#Db-------------	dovnitř	D			2.12	Type=Derivation		{"techlemma": "dovnitř-2"}
2.14	vnitrák#NNM??-----A---?	vnitrák	N	Animacy=Anim&Gender=Masc&Style=Slng		2.12	Type=Derivation		{"techlemma": "vnitrák_,l"}
2.15	vnitrácký#AA???----??---?	vnitrácký	A			2.14	Type=Derivation		{"techlemma": "vnitrácký_,h_,l"}
2.16	vnitráckost#NNF??-----?---?	vnitráckost	N	Gender=Fem		2.15	Type=Derivation		{"techlemma": "vnitráckost_,h_,l_^(*3ý)"}
2.17	vnitrácky#Dg-------??---?	vnitrácky	D			2.15	Type=Derivation		{"techlemma": "vnitrácky_,h_,l_^(*1ý)"}
2.18	vnitrákův#AU???M--------?	vnitrákův	A	Poss=Yes&Style=Slng		2.14	SemanticLabel=Possessive&Type=Derivation		{"techlemma": "vnitrákův_,l_^(*2)"}
2.19	vnitřní#AA???----??---?	vnitřní	A			2.12	Type=Derivation		{"techlemma": "vnitřní"}
2.20	vnitřně#Dg-------??---?	vnitřně	D			2.19	Type=Derivation		{"techlemma": "vnitřně_^(*1í)"}
2.21	zevnitř#Db-------------	zevnitř	D			2.12	Type=Derivation		{"techlemma": "zevnitř-2"}
"""
        db_file_in = io.StringIO(db)
        db_file_out = io.StringIO()
        lexicon = Lexicon()
        lexicon.load(db_file_in, fmt=Format.DERINET_V2)
        lexicon.save(db_file_out, fmt=Format.DERINET_V2)
        self.maxDiff = None
        self.assertMultiLineEqual(db, db_file_out.getvalue())

    def test_reduplication(self):
        lexicon = Lexicon()

        cerny = lexicon.create_lexeme("černý", "A")
        cernocerny = lexicon.create_lexeme("černočerný", "A")

        lexicon.add_composition([cerny, cerny], cerny, cernocerny)

        db_file_out = io.StringIO()
        lexicon.save(db_file_out, fmt=Format.DERINET_V2)
        self.maxDiff = None
        self.assertMultiLineEqual("""0.0	černý#A	černý	A						{}
0.1	černočerný#A	černočerný	A			0.0	Sources=0.0,0.0&Type=Compounding		{}
""", db_file_out.getvalue())


if __name__ == '__main__':
    unittest.main()
