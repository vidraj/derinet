import pandas as pd
from derinet.lexicon import Lexicon

#TODO: POUŽÍVAT JEN NA DATASETY VYTAŽENÉ Z DERINETU - MAŽE TO VĚCI, CO V DERINETU NEJSOU

lexicon = Lexicon()
lexicon = lexicon.load("derinet/tools/build/cs/2.0.6/derinet-2-0-6.tsv")

def check_if_in_derinet(x):
    lst = []
    for i in x:
        if lexicon.get_lexemes(i) == []:
            lst.append(False)
        else:
            lst.append(True)
    return(lst)

df = pd.read_csv("COMPOUND_train_annotated_REV.csv")
df = df.fillna("")
df = df[check_if_in_derinet(df['index'])]
df = df[df['není.kompozitum'] == 0]

compounds = list(df['index'])
first_parents = list(df['první.rodič'])
second_parents = list(df['druhý.rodič'])
third_parents = list(df['třetí.rodič'])
fourth_parents = list(df['čtvrtý.rodič'])

parents = []

for i in range(0, len(first_parents)):
     parents.append(".".join([first_parents[i].split(".")[-1],
                              second_parents[i].split(".")[-1],
                              third_parents[i].split(".")[-1],
                              fourth_parents[i].split(".")[-1]]))


parents = [i.strip(".") for i in parents]

pos = []

for i in compounds:
    pos.append(lexicon.get_lexemes(i)[0].pos)

newdf = pd.DataFrame()
newdf['compounds'] = compounds
newdf['pos'] = pos
newdf['parents'] = parents

newdf.to_csv("compounds.tsv", sep="\t", header=False, index=False)

for i in range(0, len(newdf)):
    parentlist = newdf['parents'][i].split(".")
    word = newdf['compounds'][i]

    lex = []
    for parent in parentlist:
        lst = lexicon.get_lexemes(parent)
        if lst == []:
            lexicon.create_lexeme(parent, 'Unknown')
            lst = lexicon.get_lexemes(parent)
        lex.append(lst[0])

    word = lexicon.get_lexemes(word)[0]
    lexicon.add_composition(lex, lex[-1], word)