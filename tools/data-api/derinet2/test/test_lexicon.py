import unittest
import io
import itertools
from derinet.lexeme import Lexeme
from derinet.lexicon import Lexicon, Format
from derinet.utils import DerinetError, DerinetFileParseError


class TestLexicon(unittest.TestCase):
    def test_add_lexeme(self):
        lexicon = Lexicon()

        lex = lexicon.create_lexeme("dog", "N")
        self.assertIsInstance(lex, Lexeme)

        self.assertEqual(lex.lemma, "dog")
        self.assertEqual(lex.pos, "N")

    def test_add_multiple(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        self.assertIsInstance(lex_a, Lexeme)

        lex_b = lexicon.create_lexeme("dog", "N")
        self.assertIsInstance(lex_b, Lexeme)

        self.assertIsNot(lex_a, lex_b)

    def test_get_lexeme_simple(self):
        lexicon = Lexicon()

        lex = lexicon.create_lexeme("dog", "N")
        lexicon.create_lexeme("cat", "N")

        lex_a = lexicon.get_lexemes("dog")
        lex_b = lexicon.get_lexemes("dog", "N")
        lex_c = lexicon.get_lexemes("dog", "N", techlemma="dog")
        lex_d = lexicon.get_lexemes("dog", "N", techlemma="dog", techlemma_match_fuzzy=True)

        self.assertEqual(lex_a, [lex])
        self.assertEqual(lex_b, [lex])
        self.assertEqual(lex_c, [lex])
        self.assertEqual(lex_d, [lex])

    def test_get_lexeme_homonymous(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N", misc={"techlemma": "dog-1"})
        lex_b = lexicon.create_lexeme("dog", "N", misc={"techlemma": "dog-2"})
        lex_c = lexicon.create_lexeme("dog", "A")

        list_a = lexicon.get_lexemes("dog")
        list_b = lexicon.get_lexemes("dog", "N")
        list_c = lexicon.get_lexemes("dog", "N", techlemma="dog-1")
        list_d = lexicon.get_lexemes("dog", "N", techlemma="dog-1", techlemma_match_fuzzy=True)
        list_e = lexicon.get_lexemes("dog", "N", techlemma="dog-3", techlemma_match_fuzzy=True)

        self.assertSetEqual(set(list_a), {lex_a, lex_b, lex_c})
        self.assertSetEqual(set(list_b), {lex_a, lex_b})
        self.assertSequenceEqual(list_c, [lex_a])
        self.assertSequenceEqual(list_d, [lex_a])
        self.assertSetEqual(set(list_e), {lex_a, lex_b})

    def test_iter_lexemes_empty(self):
        lexicon = Lexicon()
        self.assertListEqual(list(lexicon.iter_lexemes()), [])

    def test_iter_lexemes(self):
        lexicon = Lexicon()

        lexicon.create_lexeme("dog", "N")
        lexicon.create_lexeme("dog", "N")
        lexicon.create_lexeme("dog", "N")
        lexicon.create_lexeme("dog", "N")
        lexicon.create_lexeme("cat", "N")

        for lexeme in lexicon.iter_lexemes():
            self.assertIsInstance(lexeme, Lexeme)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 5)

    # TODO test that iter_lexemes() works correctly with concurrent changes to the datastore.

    def test_add_derivation_basic(self):
        lexicon = Lexicon()

        dog = lexicon.create_lexeme("dog", "N")
        doggie = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(dog, doggie)

        self.assertIs(doggie.parent, dog)
        self.assertEqual(len(dog.children), 1)
        self.assertIs(dog.children[0], doggie)

    def test_add_multiple_conflicting_derivations(self):
        lexicon = Lexicon()
        dog = lexicon.create_lexeme("dog", "N")
        god = lexicon.create_lexeme("god", "N")
        doggie = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(dog, doggie)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(god, doggie)

        self.assertIs(doggie.parent, dog)

    def test_relation_circularity_detection_reflexive(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        with self.assertRaises(DerinetError):
            lexicon.add_derivation(lex_a, lex_a)

    def test_relation_circularity_detection_small(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        lex_b = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(lex_a, lex_b)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(lex_b, lex_a)

    def test_relation_circularity_detection_large(self):
        lexicon = Lexicon()

        pes = lexicon.create_lexeme("pes", "N")
        psice = lexicon.create_lexeme("psice", "N")
        psicek = lexicon.create_lexeme("psíček", "N")
        psicin = lexicon.create_lexeme("psičin", "A")
        psickuv = lexicon.create_lexeme("psíčkův", "A")
        psik = lexicon.create_lexeme("psík", "N")
        psikuv = lexicon.create_lexeme("psíkův", "A")
        psovite = lexicon.create_lexeme("psovitě", "D")
        psovitost = lexicon.create_lexeme("psovitost", "N")
        psovity = lexicon.create_lexeme("psovitý", "A")
        psuv = lexicon.create_lexeme("psův", "A")

        lexicon.add_derivation(psik, psice)
        lexicon.add_derivation(psik, psicek)
        lexicon.add_derivation(psice, psicin)
        lexicon.add_derivation(psicek, psickuv)
        lexicon.add_derivation(pes, psik)
        lexicon.add_derivation(psik, psikuv)
        lexicon.add_derivation(psovity, psovite)
        lexicon.add_derivation(psovity, psovitost)
        lexicon.add_derivation(pes, psovity)
        lexicon.add_derivation(pes, psuv)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(psovite, pes)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(psik, pes)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(psickuv, pes)

        with self.assertRaises(DerinetError):
            lexicon.add_derivation(psickuv, psik)

    def test_load_old_basic(self):
        db = ("0\tdog\tdog-1\tN\t\n", "1\tcat\tcat\tN\t\n")
        lexicon = Lexicon()
        lexicon.load(db, Format.DERINET_V1)

        lex_dog = lexicon.get_lexemes("dog", "N")
        self.assertEqual(len(lex_dog), 1)
        self.assertEqual(lex_dog[0].techlemma, "dog-1")

        lex_cat = lexicon.get_lexemes("cat", "N")
        self.assertEqual(len(lex_cat), 1)
        self.assertEqual(lex_cat[0].techlemma, "cat")

        lexemes = list(lexicon.iter_lexemes())
        self.assertEqual(len(lexemes), 2)

    def test_load_old_deriv(self):
        db = ("0\tdog\tdog-1\tN\t\n", "1\tdoggie\tdoggie\tN\t0\n", "2\tkitten\tkitten-1\tN\t3\n", "3\tcat\tcat\tN\t\n")
        lexicon = Lexicon()
        lexicon.load(db, Format.DERINET_V1)

        lexemes = list(lexicon.iter_lexemes())
        self.assertEqual(len(lexemes), 4)

        dogs = lexicon.get_lexemes("dog")
        doggies = lexicon.get_lexemes("doggie")
        kittens = lexicon.get_lexemes("kitten")
        cats = lexicon.get_lexemes("cat")

        self.assertEqual(len(dogs), 1)
        self.assertEqual(len(doggies), 1)
        self.assertEqual(len(kittens), 1)
        self.assertEqual(len(cats), 1)

        dog = dogs[0]
        doggie = doggies[0]
        kitten = kittens[0]
        cat = cats[0]

        self.assertIsNotNone(dog)
        self.assertIsNotNone(doggie)
        self.assertIsNotNone(kitten)
        self.assertIsNotNone(cat)

        self.assertIs(doggie.parent, dog)
        self.assertEqual(len(dog.children), 1)
        self.assertIs(kitten.parent, cat)
        self.assertEqual(len(cat.children), 1)

    def test_load_old_return(self):
        db = ("0\tdog\tdog-1\tN\t\n",)
        lexicon_1 = Lexicon()
        lexicon_2 = lexicon_1.load(db, Format.DERINET_V1)

        self.assertIs(lexicon_2, lexicon_1)

    def test_load_old_nonseq(self):
        db = ("2\tdog\tdog-1\tN\t\n", "1\tdoggie\tdoggie\tN\t2\n", "10000\tkitten\tkitten-1\tN\t666\n", "666\tcat\tcat\tN\t\n")
        lexicon = Lexicon()
        lexicon.load(db, Format.DERINET_V1)

        lexemes = list(lexicon.iter_lexemes())
        self.assertEqual(len(lexemes), 4)

        dogs = lexicon.get_lexemes("dog")
        doggies = lexicon.get_lexemes("doggie")
        kittens = lexicon.get_lexemes("kitten")
        cats = lexicon.get_lexemes("cat")

        self.assertEqual(len(dogs), 1)
        self.assertEqual(len(doggies), 1)
        self.assertEqual(len(kittens), 1)
        self.assertEqual(len(cats), 1)

        dog = dogs[0]
        doggie = doggies[0]
        kitten = kittens[0]
        cat = cats[0]

        self.assertIsNotNone(dog)
        self.assertIsNotNone(doggie)
        self.assertIsNotNone(kitten)
        self.assertIsNotNone(cat)

        self.assertIs(doggie.parent, dog)
        self.assertEqual(len(dog.children), 1)
        self.assertIs(kitten.parent, cat)
        self.assertEqual(len(cat.children), 1)

    def test_load_old_negative(self):
        db = ("-1\tdog\tdog-1\tN\t\n",)
        lexicon = Lexicon()

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db, Format.DERINET_V1)

    def test_load_old_reflexive(self):
        db = ("0\tdog\tdog-1\tN\t0\n",)
        lexicon = Lexicon()

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db, Format.DERINET_V1)

    def test_load_old_missing_parent(self):
        db = ("0\tdog\tdog-1\tN\t1\n",)
        lexicon = Lexicon()

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db, Format.DERINET_V1)

    def test_load_old_multiple(self):
        """
        Test that multiple databases with identical IDs don't clobber one another when loaded into a single Lexicon.
        Instead, they should coexist nicely.
        """
        db_1 = ("0\tdog\tdog-1\tN\t\n", "1\tdoggie\tdoggie\tN\t0\n", "2\tkitten\tkitten-1\tN\t3\n", "3\tcat\tcat\tN\t\n")
        db_2 = ("0\tman\tman-1\tN\t\n", "1\tMAN\tman-2\tN\t0\n")

        lexicon = Lexicon()
        lexicon.load(db_1, Format.DERINET_V1)
        lexicon.load(db_2, Format.DERINET_V1)

        lexemes = list(lexicon.iter_lexemes())
        self.assertEqual(len(lexemes), 6)

        dogs = lexicon.get_lexemes("dog")
        doggies = lexicon.get_lexemes("doggie")
        kittens = lexicon.get_lexemes("kitten")
        cats = lexicon.get_lexemes("cat")
        men_lc = lexicon.get_lexemes("man")
        men_uc = lexicon.get_lexemes("MAN")

        self.assertEqual(len(dogs), 1)
        self.assertEqual(len(doggies), 1)
        self.assertEqual(len(kittens), 1)
        self.assertEqual(len(cats), 1)
        self.assertEqual(len(men_lc), 1)
        self.assertEqual(len(men_uc), 1)

        dog = dogs[0]
        doggie = doggies[0]
        kitten = kittens[0]
        cat = cats[0]
        man_lc = men_lc[0]
        man_uc = men_uc[0]

        self.assertIsNotNone(dog)
        self.assertIsNotNone(doggie)
        self.assertIsNotNone(kitten)
        self.assertIsNotNone(cat)
        self.assertIsNotNone(man_lc)
        self.assertIsNotNone(man_uc)

        self.assertIs(doggie.parent, dog)
        self.assertEqual(len(dog.children), 1)
        self.assertIs(kitten.parent, cat)
        self.assertEqual(len(cat.children), 1)
        self.assertIs(man_uc.parent, man_lc)
        self.assertEqual(len(man_lc.children), 1)

    def test_save(self):
        lexicon = Lexicon()

        pes = lexicon.create_lexeme("pes", "N")
        psice = lexicon.create_lexeme("psice", "N")
        psicek = lexicon.create_lexeme("psíček", "N")
        psicin = lexicon.create_lexeme("psičin", "A")
        psickuv = lexicon.create_lexeme("psíčkův", "A")
        psik = lexicon.create_lexeme("psík", "N")
        psikuv = lexicon.create_lexeme("psíkův", "A")
        psovite = lexicon.create_lexeme("psovitě", "D")
        psovitost = lexicon.create_lexeme("psovitost", "N")
        psovity = lexicon.create_lexeme("psovitý", "A")
        psuv = lexicon.create_lexeme("psův", "A")

        dog = lexicon.create_lexeme("dog", "N")
        doggie = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(psik, psice)
        lexicon.add_derivation(psik, psicek)
        lexicon.add_derivation(psice, psicin)
        lexicon.add_derivation(psicek, psickuv)
        lexicon.add_derivation(pes, psik)
        lexicon.add_derivation(psik, psikuv)
        lexicon.add_derivation(psovity, psovite)
        lexicon.add_derivation(psovity, psovitost)
        lexicon.add_derivation(pes, psovity)
        lexicon.add_derivation(pes, psuv)

        lexicon.add_derivation(dog, doggie)

        saved_data = io.StringIO()
        lexicon.save(saved_data, Format.DERINET_V2)

        self.maxDiff = None

        self.assertMultiLineEqual(saved_data.getvalue(), """0.0	dog#N	dog	N						{}
0.1	doggie#N	doggie	N			0.0			{}

1.0	pes#N	pes	N						{}
1.1	psovitý#A	psovitý	A			1.0			{}
1.2	psovitě#D	psovitě	D			1.1			{}
1.3	psovitost#N	psovitost	N			1.1			{}
1.4	psík#N	psík	N			1.0			{}
1.5	psice#N	psice	N			1.4			{}
1.6	psičin#A	psičin	A			1.5			{}
1.7	psíček#N	psíček	N			1.4			{}
1.8	psíčkův#A	psíčkův	A			1.7			{}
1.9	psíkův#A	psíkův	A			1.4			{}
1.10	psův#A	psův	A			1.0			{}
""")
        saved_data.close()

    def test_pickle_roundtrip(self):
        lexicon = Lexicon()

        pes = lexicon.create_lexeme("pes", "N")
        psice = lexicon.create_lexeme("psice", "N")
        psicek = lexicon.create_lexeme("psíček", "N")
        psicin = lexicon.create_lexeme("psičin", "A")
        psickuv = lexicon.create_lexeme("psíčkův", "A")
        psik = lexicon.create_lexeme("psík", "N")
        psikuv = lexicon.create_lexeme("psíkův", "A")
        psovite = lexicon.create_lexeme("psovitě", "D")
        psovitost = lexicon.create_lexeme("psovitost", "N")
        psovity = lexicon.create_lexeme("psovitý", "A")
        psuv = lexicon.create_lexeme("psův", "A")

        dog = lexicon.create_lexeme("dog", "N")
        doggie = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(psik, psice)
        lexicon.add_derivation(psik, psicek)
        lexicon.add_derivation(psice, psicin)
        lexicon.add_derivation(psicek, psickuv)
        lexicon.add_derivation(pes, psik)
        lexicon.add_derivation(psik, psikuv)
        lexicon.add_derivation(psovity, psovite)
        lexicon.add_derivation(psovity, psovitost)
        lexicon.add_derivation(pes, psovity)
        lexicon.add_derivation(pes, psuv)

        lexicon.add_derivation(dog, doggie)

        saved_data = io.BytesIO()
        lexicon.save(saved_data, fmt=Format.PICKLE_V4)
        saved_data.seek(0)
        loaded_lexicon = Lexicon()
        loaded_lexicon.load(saved_data, fmt=Format.PICKLE_V4)
        saved_data.close()

        for lexeme_a, lexeme_b in itertools.zip_longest(lexicon.iter_lexemes(), loaded_lexicon.iter_lexemes()):
            self.assertIsNotNone(lexeme_a)
            self.assertIsNotNone(lexeme_b)

            self.assertEqual(lexeme_a.lemma, lexeme_b.lemma)
            self.assertEqual(lexeme_a.pos, lexeme_b.pos)
            if lexeme_a.parent is None:
                self.assertIsNone(lexeme_b.parent)
            else:
                self.assertIsNotNone(lexeme_b.parent)
                self.assertEqual(lexeme_a.parent.lemma, lexeme_b.parent.lemma)

    def test_save_v1_roundtrip(self):
        db = """0	psí	psí-1	A	
1	psí	psí-2_,t_^(název_písmene_řecké_abecedy)	N	
2	psice	psice_^(*3ík)	N	11
3	psíček	psíček	N	11
4	psičin	psičin_^(*3ce)	A	2
5	psíčkař	psíčkař	N	
6	psíčkařův	psíčkařův_^(*2)	A	5
7	psíčkův	psíčkův_^(*3ek)	A	3
8	Pšikalová	Pšikalová_;S	N	9
9	Pšikal	Pšikal_;S	N	
10	Pšikalův	Pšikalův_;S_^(*2)	A	9
11	psík	psík	N	
12	Psíková	Psíková_;S	N	14
13	Pšikovová	Pšikovová_;S	N	
14	Psík	Psík_;S	N	
15	psíkův	psíkův_^(*2)	A	11
16	Psíkův	Psíkův_;S_^(*2)	A	14
"""
        db_file_in = io.StringIO(db)
        db_file_out = io.StringIO()
        lexicon = Lexicon()
        lexicon.load(db_file_in, fmt=Format.DERINET_V1)
        lexicon.save(db_file_out, fmt=Format.DERINET_V1)
        self.assertMultiLineEqual(db_file_out.getvalue(), db)


    def test_iter_trees(self):
        db = """0	psí	psí-1	A	
1	psí	psí-2_,t_^(název_písmene_řecké_abecedy)	N	
2	psice	psice_^(*3ík)	N	11
3	psíček	psíček	N	11
4	psičin	psičin_^(*3ce)	A	2
5	psíčkař	psíčkař	N	
6	psíčkařův	psíčkařův_^(*2)	A	5
7	psíčkův	psíčkův_^(*3ek)	A	3
8	Pšikalová	Pšikalová_;S	N	9
9	Pšikal	Pšikal_;S	N	
10	Pšikalův	Pšikalův_;S_^(*2)	A	9
11	psík	psík	N	
12	Psíková	Psíková_;S	N	14
13	Pšikovová	Pšikovová_;S	N	
14	Psík	Psík_;S	N	
15	psíkův	psíkův_^(*2)	A	11
16	Psíkův	Psíkův_;S_^(*2)	A	14
"""
        db_file_in = io.StringIO(db)
        lexicon = Lexicon()
        lexicon.load(db_file_in, fmt=Format.DERINET_V1)

        trees = list(lexicon.iter_trees())
        self.assertEqual(7, len(trees))

        lemmas = set()
        for root in trees:
            self.assertTrue(isinstance(root, Lexeme))
            lemmas.add(root.lemma)

        self.assertSetEqual({"psí", "psíčkař", "Pšikal", "psík", "Pšikovová", "Psík"}, lemmas)

    def test_parse_extra_pos(self):
        """
        The xC and xU should be parsed and the extra annotation stored into misc.
        """
        db = """0	zelenomodrý	zelenomodrý	AC	
1	text	text	NU	
"""
        db_file_in = io.StringIO(db)
        lexicon = Lexicon()
        lexicon.load(db_file_in, fmt=Format.DERINET_V1)

        z = lexicon.get_lexemes("zelenomodrý")
        self.assertEqual(len(z), 1)
        self.assertEqual(z[0].pos, "A")
        self.assertIn("is_compound", z[0].misc)
        self.assertIs(z[0].misc["is_compound"], True)

        self.assertFalse("is_nonderived" in z[0].misc and z[0].misc["is_nonderived"])

        t = lexicon.get_lexemes("text")
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].pos, "N")
        self.assertIn("is_nonderived", t[0].misc)
        self.assertIs(t[0].misc["is_nonderived"], True)

        self.assertFalse("is_compound" in t[0].misc and t[0].misc["is_compound"])



if __name__ == '__main__':
    unittest.main()
