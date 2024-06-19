#!python3
import sys

affixes = ["ova", "ová","vš","t","á", "čin"]
with open(sys.argv[1], "r") as rid:
    with open(sys.argv[2], "r") as cl:
        for la, lb in zip(rid, cl):
            lsa = la.strip().split("\t")
            lsb = lb.strip().split("\t")
            new_ann = []
            if lsa[0][0] == "-" and lsa[0][-1] == "-":
                print("".join(lsa[0].split()) + "\tR")
                continue

            for rt, cl, mp in zip(lsa[1].split(), lsb[1].split(), lsb[0].split()):
                if rt == "1" and cl == "R":
                    new_ann.append("R")
                elif cl == "R" and mp not in affixes:
                    new_ann.append("R")
                elif cl == "I":
                    new_ann.append("I")
                else:
                    new_ann.append("D")
            if new_ann.count("R") == 0:
                print(lb)
            else:
                print(lsa[0] + "\t" + " ".join(new_ann))
                                                       
