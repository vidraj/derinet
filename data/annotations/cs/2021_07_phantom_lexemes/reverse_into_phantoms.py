import pandas as pd
import numpy as np

df = pd.read_csv("reverse_df_chunks.tsv", sep ="\t")

chunks = df['chunks']
marks = np.repeat("+", len(df))
parents = np.repeat("", len(df))

newdf = pd.DataFrame()
newdf['Marks'] = marks
newdf['chunks'] = chunks
newdf['parents'] = parents

newdf.to_csv("phantom_chunks.tsv", sep='\t', index=False, header=False)

print("done")
