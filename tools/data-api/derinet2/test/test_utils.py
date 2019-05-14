import unittest
import derinet.utils as u


class TestUtils(unittest.TestCase):
    def test_parse_v1_id(self):
        self.assertEqual(u.parse_v1_id("0"), 0)
        self.assertEqual(u.parse_v1_id("1"), 1)
        self.assertEqual(u.parse_v1_id("123"), 123)
        self.assertEqual(u.parse_v1_id("10000000"), 10000000)

        with self.assertRaises(ValueError):
            u.parse_v1_id("")

        with self.assertRaises(ValueError):
            u.parse_v1_id("-1")

        with self.assertRaises(ValueError):
            u.parse_v1_id("- 1")

        with self.assertRaises(ValueError):
            u.parse_v1_id("   ")

        with self.assertRaises(ValueError):
            u.parse_v1_id("\n")

        with self.assertRaises(ValueError):
            u.parse_v1_id("0x10")

        with self.assertRaises(ValueError):
            u.parse_v1_id("16h")

        with self.assertRaises(ValueError):
            u.parse_v1_id("abc")

        with self.assertRaises(ValueError):
            u.parse_v1_id("10A")

        with self.assertRaises(ValueError):
            u.parse_v1_id("A15")

    def test_parse_v2_id(self):
        self.assertTupleEqual(u.parse_v2_id("0.0"), (0, 0))
        self.assertTupleEqual(u.parse_v2_id("1.2"), (1, 2))
        self.assertTupleEqual(u.parse_v2_id("1000000.6000000"), (1000000, 6000000))

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            u.parse_v2_id(123.1)

        with self.assertRaises(ValueError):
            u.parse_v2_id("0")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0.0")

        with self.assertRaises(ValueError):
            u.parse_v2_id(".1")

        with self.assertRaises(ValueError):
            u.parse_v2_id("1.")

        with self.assertRaises(ValueError):
            u.parse_v2_id("a.1")

        with self.assertRaises(ValueError):
            u.parse_v2_id("1.a")

        with self.assertRaises(ValueError):
            u.parse_v2_id("  0.0")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0  ")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0\n")

        with self.assertRaises(ValueError):
            u.parse_v2_id("")

        with self.assertRaises(ValueError):
            u.parse_v2_id("  ")

        with self.assertRaises(ValueError):
            u.parse_v2_id(".")

        with self.assertRaises(ValueError):
            u.parse_v2_id(" . ")

    def test_parse_v2_id_roundtrip(self):
        """
        The following tests may fail with disabled asserts. They are here to
        ensure that the ID roundtrips properly. Otherwise, you could refer
        to a lexeme with ID 0.0 using "00.00", or not, depending on the internal
        representation. We do not want to force a particular representation on
        implementers.
        """
        with self.assertRaises(AssertionError):
            u.parse_v2_id("00.1")

        with self.assertRaises(AssertionError):
            u.parse_v2_id("0.01")

    def test_range_overlap(self):
        # Trivial cases.
        self.assertTrue(u.range_overlaps((0, 1), (0, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (0, 10)))

        # Not so trivial cases.
        self.assertTrue(u.range_overlaps((0, 10), (0, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (-3, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (3, 5)))
        self.assertTrue(u.range_overlaps((0, 10), (9, 10)))
        self.assertTrue(u.range_overlaps((0, 10), (9, 12)))

        # The same in reverse.
        self.assertTrue(u.range_overlaps((0, 1), (0, 10)))
        self.assertTrue(u.range_overlaps((-3, 1), (0, 10)))
        self.assertTrue(u.range_overlaps((3, 5), (0, 10)))
        self.assertTrue(u.range_overlaps((9, 10), (0, 10)))
        self.assertTrue(u.range_overlaps((9, 12), (0, 10)))

    def test_range_nonoverlap(self):
        self.assertFalse(u.range_overlaps((0, 10), (-3, -1)))
        self.assertFalse(u.range_overlaps((0, 10), (12, 50)))
        self.assertFalse(u.range_overlaps((0, 10), (-1, 0)))
        self.assertFalse(u.range_overlaps((0, 10), (10, 15)))

    def test_range_invalid(self):
        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (0, 0),
            (1, 5)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (0, 5),
            (0, 0)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (3, 2),
            (1, 5)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (1, 5),
            (10, 7)
        )

    def test_print_kwstring_empty(self):
        """
        The empty kwstring can be produced in several different ways, making the format ambiguous.
        """
        self.assertEqual("", u.format_kwstring([]))
        self.assertEqual("", u.format_kwstring([{}]))
        self.assertEqual("|", u.format_kwstring([{}, {}]))


    def test_print_kwstring(self):
        self.assertEqual(
            "k1=v1&k2=v2&k3=v3|k1=v1&k5=v5",
            u.format_kwstring([{"k1": "v1", "k3": "v3", "k2": "v2"},
                               {"k5": "v5", "k1": "v1"}])
        )

    def test_parse_kwstring_empty(self):
        self.assertListEqual([], u.parse_kwstring(""))

    def test_parse_kwstring(self):
        d = u.parse_kwstring("k1=v1&k2=v2&k3=v3|k1=v1&k5=v5")
        self.assertEqual(2, len(d))
        self.assertDictEqual({"k1": "v1", "k3": "v3", "k2": "v2"}, d[0])
        self.assertDictEqual({"k5": "v5", "k1": "v1"}, d[1])

    def test_kwstring_illegal_chars_eq_key(self):
        d = [{"ke=y": "val"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_kwstring_illegal_chars_eq_val(self):
        d = [{"key": "v=al"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_kwstring_illegal_chars_amp_key(self):
        d = [{"ke&y": "val"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_kwstring_illegal_chars_amp_val(self):
        d = [{"key": "v&al"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_kwstring_illegal_chars_or_key(self):
        d = [{"ke|y": "val"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_kwstring_illegal_chars_or_val(self):
        d = [{"key": "v|al"}]
        self.assertRaises(
            ValueError,
            u.format_kwstring,
            d
        )

    def test_techlemma_to_lemma(self):
        self.assertEqual("ninety", u.techlemma_to_lemma("ninety`90"))
        self.assertEqual("bank", u.techlemma_to_lemma("bank-1"))
        self.assertEqual("Aachen", u.techlemma_to_lemma("Aachen_;S"))
        self.assertEqual("Aaheimův", u.techlemma_to_lemma("Aaheimův-1_;S_^(*4-1)"))
        self.assertEqual("čtrnácteronásobnost", u.techlemma_to_lemma("čtrnácteronásobnost`14_,s_^(*3ý)"))


if __name__ == '__main__':
    unittest.main()
