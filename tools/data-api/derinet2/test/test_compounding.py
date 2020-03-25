import unittest
from derinet.lexicon import Lexicon
from derinet.relation import CompoundRelation
from derinet.utils import DerinetError, DerinetCycleCreationError


class TestCompounding(unittest.TestCase):
    def test_compound_creation(self):
        lexicon = Lexicon()

        pay = lexicon.create_lexeme("pay", "V")
        phone = lexicon.create_lexeme("phone", "N")
        payphone = lexicon.create_lexeme("payphone", "N")

        lexicon.add_composition([pay, phone], phone, payphone)

        self.assertIsNotNone(payphone.parent_relation)
        self.assertIsInstance(payphone.parent_relation, CompoundRelation)

        self.assertIsNotNone(payphone.parent)
        self.assertIs(phone, payphone.parent)

        self.assertEqual(1, len(phone.child_relations))
        self.assertIs(payphone.parent_relation, phone.child_relations[0])

        self.assertEqual(1, len(pay.child_relations))
        self.assertIs(payphone.parent_relation, pay.child_relations[0])

        self.assertEqual(1, len(phone.children))
        self.assertIs(payphone, phone.children[0])

        self.assertEqual(0, len(pay.children))

    def test_compound_not_in_sources(self):
        lexicon = Lexicon()

        pay = lexicon.create_lexeme("pay", "V")
        phone = lexicon.create_lexeme("phone", "N")
        phonology = lexicon.create_lexeme("phonology", "N")
        payphone = lexicon.create_lexeme("payphone", "N")

        with self.assertRaises(ValueError):
            lexicon.add_composition([pay, phonology], phone, payphone)

    def test_target_in_sources(self):
        lexicon = Lexicon()

        pay = lexicon.create_lexeme("pay", "V")
        phone = lexicon.create_lexeme("phone", "N")
        payphone = lexicon.create_lexeme("payphone", "N")

        with self.assertRaises(DerinetError):
            lexicon.add_composition([pay, phone, payphone], phone, payphone)

    def test_reduplication(self):
        lexicon = Lexicon()

        cerny = lexicon.create_lexeme("černý", "A")
        cernocerny = lexicon.create_lexeme("černočerný", "A")

        lexicon.add_composition([cerny, cerny], cerny, cernocerny)

        self.assertEqual(1, len(cerny.children))
        self.assertIs(cernocerny, cerny.children[0])
        self.assertEqual((cerny, cerny), cernocerny.parent_relation.sources)

    def test_cycle_deriv_comp(self):
        lexicon = Lexicon()

        telephone = lexicon.create_lexeme("telephone", "N")
        tele = lexicon.create_lexeme("tele", "A")
        phone = lexicon.create_lexeme("phone", "N")

        lexicon.add_derivation(telephone, phone)
        with self.assertRaises(DerinetCycleCreationError):
            lexicon.add_composition([tele, phone], phone, telephone)

    def test_cycle_comp_deriv(self):
        lexicon = Lexicon()

        telephone = lexicon.create_lexeme("telephone", "N")
        tele = lexicon.create_lexeme("tele", "A")
        phone = lexicon.create_lexeme("phone", "N")

        lexicon.add_composition([tele, phone], phone, telephone)
        with self.assertRaises(DerinetCycleCreationError):
            lexicon.add_derivation(telephone, phone)

    def test_noncycle_secondary_relation(self):
        lexicon = Lexicon()

        telephone = lexicon.create_lexeme("telephone", "N")
        tele = lexicon.create_lexeme("tele", "A")
        phone = lexicon.create_lexeme("phone", "N")

        lexicon.add_derivation(telephone, phone)
        lexicon.add_composition([tele, phone], tele, telephone)

        self.assertIs(telephone, phone.parent)
        self.assertIs(tele, telephone.parent)


if __name__ == '__main__':
    unittest.main()
