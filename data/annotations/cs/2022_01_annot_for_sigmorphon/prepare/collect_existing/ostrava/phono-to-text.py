#!/usr/bin/env python3

import re
import sys

def main():
    for line in sys.stdin:
        line = line.rstrip()
        form, seg = line.split(";")

        if seg.replace("-", "") != form:
            print("Form {} is not found in seg {}".format(form, seg), file=sys.stderr)
            continue

        # X == ch
        # KS == x
        # KW == q
        # A == au
        # E == eu
        # O == ou
        # MŇE == mě
        # ŇE == ně
        # JE == ě
        # ďe, ťe, ňe == dě, tě, ně
        # iji == ii, ijí == ií, ije == ie (existují protipříklady?)

        amended_seg = seg.replace("M-Ň-E", "m-ě").replace("M-ŇE", "m-ě").replace("MŇ-E", "m-ě").replace("MŇE", "mě")
        # J-E doesn't occur in the corpus.
        amended_seg = amended_seg.replace("Ň-E", "n-ě").replace("ŇE", "ně")
        amended_seg = amended_seg.replace("JE", "ě")

        amended_seg = amended_seg.replace("KS", "x")
        amended_seg = amended_seg.replace("KW", "q")

        amended_seg = amended_seg.replace("X", "ch")

        amended_seg = amended_seg.replace("A", "au")
        amended_seg = amended_seg.replace("E", "eu")
        amended_seg = amended_seg.replace("O", "ou")

        amended_seg = amended_seg.replace("ď-e", "d-ě").replace("ďe", "dě")
        amended_seg = amended_seg.replace("ť-e", "t-ě").replace("ťe", "tě")
        amended_seg = amended_seg.replace("ň-e", "n-ě").replace("ňe", "ně")

        print(amended_seg)

        # i-ji, i-jí and i-je is the other paradigm, not to be replaced ("přijít").
        alt_seg = amended_seg.replace("ij-i", "i-i").replace("iji", "ii")
        alt_seg = alt_seg.replace("ij-í", "i-í").replace("ijí", "ií")
        alt_seg = alt_seg.replace("ij-e", "i-e").replace("ije", "ie")

        if alt_seg != amended_seg:
            print(alt_seg)

if __name__ == "__main__":
    main()
