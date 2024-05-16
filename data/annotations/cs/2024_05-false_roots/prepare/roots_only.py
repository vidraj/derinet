import pandas as pd

parent_output = pd.read_csv("./PaReNT_UDer-1.1-cs-DeriNet.tsv.gz", sep="\t")
derinet = pd.read_csv("../../../../releases/cs/derinet-2-1.tsv.gz", sep="\t", header=None)

if not all(derinet[2] == parent_output.lemma):
    raise Exception("not the same lemma list")

roots = parent_output[derinet[7].isnull()]
roots_sorted = roots.sort_values(by="PaReNT_Derivative_probability", ascending=False)

###FILTR
#zakomentujte, jestli si přejete v souboru mít i mužská vlastní jména
def is_male_name(x: str) -> bool:
    capitalized = x[0].isupper()
    ends_in_a = x[-1] == "á"

    return True if capitalized and not ends_in_a else False

roots_sorted = roots_sorted[[not is_male_name(i) for i in roots_sorted.lemma]]
##

roots_sorted["UDer_id"] = [0 for i in range(len(roots_sorted))]
roots_sorted = roots_sorted.rename(columns={"UDer_id": "Correct_candidate"})
roots_sorted = roots_sorted.drop(["PaReNT_retrieval_best", "PaReNT_retrieval_greedy"], axis=1)

roots_sorted.to_csv("./false_roots.tsv", sep="\t", index=False, index_label=False)
print("Potential false root dataset ready!")