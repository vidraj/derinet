import pandas as pd

df = pd.read_csv("./compounds.csv", sep="\t")

new_df = df[["lemma", "Best_parents"]]
new_df = new_df[df.Annotated]
new_df.columns = ["lemma", "parents"]
new_df = new_df[[i[0] != "!" for i in new_df.parents]]

new_df.to_csv("compounds.tsv", sep="\t", index=False)