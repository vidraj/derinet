import unittest
import io

from nose.tools import assert_raises

from derinet import DeriNetError, LexemeNotFoundError, LexemeAlreadyExistsError
from derinet.derinet import DeriNet
from derinet.utils import Node


class TestFiles(unittest.TestCase):

    def setUp(self):
        data_v1 = """0\tAaasen\tAaasen_;S\tN\t
1\tAaasenův\tAaasenův_;S_^(*2)\tA\t0
2\tAabar\tAabar_;S\tN\t
3\tAabarův\tAabarův_;S_^(*2)\tA\t2
4\tAabarův\tAabarův_;X_^(*2)\tX\t2
"""
        data_v2 = """
        """
        data_v3 = """455709	pes	pes_^(zvíře)	N	
580101	psice	psice_^(*3ík)	N	580107
580102	psíček	psíček	N	580107
580103	psičin	psičin_^(*3ce)	A	580101
580106	psíčkův	psíčkův_^(*3ek)	A	580102
580107	psík	psík	N	455709
580111	psíkův	psíkův_^(*2)	A	580107
580178	psovitě	psovitě_^(*1ý)	D	580180
580179	psovitost	psovitost_^(*3ý)	N	580180
580180	psovitý	psovitý	A	455709
580230	psův	psův_^(zvíře)_(*3es)	A	455709
"""
        self.data_stream_v1 = io.StringIO(data_v1)
        self.data_stream_v2 = io.StringIO(data_v2)
        self.data_stream_v3 = io.StringIO(data_v3)


    def test_data_v1_loaded(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        desired_data = [Node(lex_id=0, pretty_id='0', lemma='Aaasen', morph='Aaasen_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[1]),
                        Node(lex_id=1, pretty_id='1', lemma='Aaasenův', morph='Aaasenův_;S_^(*2)', pos='A', tag_mask='', parent_id=0, composition_parents=[], misc={}, children=[]),
                        Node(lex_id=2, pretty_id='2', lemma='Aabar', morph='Aabar_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[3,4]),
                        Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[]),
                        Node(lex_id=4, pretty_id='4', lemma='Aabarův', morph='Aabarův_;X_^(*2)', pos='X', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])
                        ]
        self.assertEqual(derinet._data, desired_data)

    def test_proper_id_is_get_by_lemma(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aaasen')
        self.assertEqual(nid, 0)

    def test_proper_id_is_get_by_lemma_pos(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aabarův', pos='A')
        self.assertEqual(nid, 3)
        nid = derinet.get_id('Aabarův', pos='X')
        self.assertEqual(nid, 4)

    def test_proper_id_is_get_by_lemma_morph(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aabarův', morph='Aabarův_;S_^(*2)')
        self.assertEqual(nid, 3)
        nid = derinet.get_id('Aabarův', morph='Aabarův_;X_^(*2)')
        self.assertEqual(nid, 4)

    def test_lexeme_not_found_raised(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Neexistujici')
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Aabarův', morph='Neexistujici')
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Aabarův', pos='Neexistujici')

    def test_lexeme_exists(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        self.assertTrue(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=1, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=None, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask=None, parent_id=None, composition_parents=None, misc=None, children=None)))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=None, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='abcd', parent_id=1, composition_parents=[2, 0], misc={"gender": "F"}, children=[4])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=3, pretty_id=None, lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))

        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='2', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarůvovo', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2a)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='D', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))

    def test_add_lexeme(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        test_lexeme = Node(lex_id=None, pretty_id='5', lemma='lexém', morph='lexém', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[])
        self.assertFalse(derinet.lexeme_exists(test_lexeme))
        derinet.add_lexeme(test_lexeme)
        self.assertTrue(derinet.lexeme_exists(test_lexeme))

        with assert_raises(LexemeAlreadyExistsError):
            derinet.add_lexeme(Node(lex_id=None, pretty_id='5', lemma='lexém', morph='lexém', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[]))

        with assert_raises(DeriNetError): # It is possible for this to raise a different error. But it must be a subclass of DeriNetError anyway.
            derinet.add_lexeme(Node(lex_id=None, pretty_id='5', lemma='pseudolexém', morph='lexém-2', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[]))

        # TODO test inserting malformatted lexemes.

    def test_database_load_pretty_ids(self):
        derinet = DeriNet(fname=self.data_stream_v3)

        id_pes = derinet.get_id("pes", "N")
        id_psovite = derinet.get_id("psovitě", "D")
        id_psik = derinet.get_id("psík", "N")
        id_psickuv = derinet.get_id("psíčkův", "A")

        self.assertTrue(derinet._is_valid_lex_id(id_pes))
        self.assertTrue(derinet._is_valid_lex_id(id_psovite))
        self.assertTrue(derinet._is_valid_lex_id(id_psik))
        self.assertTrue(derinet._is_valid_lex_id(id_psickuv))

        self.assertEqual(id_pes, derinet.get_parent(id_psik).lex_id)
        self.assertEqual(id_psik, derinet.get_parent(derinet.get_parent(id_psickuv).lex_id).lex_id)
