import derinet.lexicon as dlex

def read_etym_data(filename: str) -> dict[str, list[str]]:
    '''
    Parses a tsv file containing words and their etymological information.
    
    Parameters:
    - filename (str): The path to the tsv file containing data.
    
    Returns:
    - dict[str, list[str]]: A dictionary where each key is a word and each value 
    is a list of abbreviations of countries from which the word came to czech.
    '''
    etym_data = {}
    with open(filename, 'r') as etym_file:
        for line in etym_file.readlines():
            line = line.split('\t')
            word = line[0].strip()
            etymology = line[1].split(',')
            etym_data[word] = etymology
    return etym_data
    

def main(filename: str):
    '''
    Writes etymological information to root lexeme
    to new feature Etymology as a list of abbreviations
    of countries.
    '''
    lexicon = dlex.Lexicon()  
    lexicon.load(data_source='derinet-2-1-1.tsv', on_err='continue')
    data = read_etym_data(filename)
    for word, etymology in data.items():
        lexemes = lexicon.get_lexemes(lemma=word)
        for lexeme in lexemes:
            root_lexeme = lexeme.get_tree_root()
            if 'Etymology' not in root_lexeme.feats:
                root_lexeme.add_feature('Etymology', etymology)
    lexicon.save(data_sink='new-derinet-2-1-1.tsv', fmt=dlex.Format.DERINET_V2)
    del lexicon  # clean RAM
        

if __name__ == "__main__":
    tsv_file = 'parsed_dictionary.tsv'
    main(tsv_file)