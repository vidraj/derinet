import pandas as pd
import numpy as np

parent_output = pd.read_csv("./PaReNT_output/PaReNT_UDer-1.1-cs-DeriNet.tsv", sep="\t")
derinet = pd.read_csv("./derinet/data/releases/cs/derinet-2-1.tsv.gz", sep="\t", header=None)

if not all(derinet[2] == parent_output.lemma):
    raise Exception("not the same lemma list")

roots = parent_output[derinet[7].isnull()]
roots_sorted = roots.sort_values(by="PaReNT_Derivative_probability", ascending=False)

roots_sorted = roots_sorted.to_csv("./false_roots.tsv", sep="\t")