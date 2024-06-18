import sys
sys.path.append('../../../../derinet/tools/data-api/derinet2/')
import derinet.lexicon as dlex

def read_etym_data(filename: str) -> dict[str, (list[str], bool)]:
    '''
    Parses a tsv file containing words and their etymological information.
    
    Parameters:
    - filename (str): The path to the tsv file containing data.
    
    Returns:
    - dict[str, (list[str], bool)]: A dictionary where each key is a word and each value 
    is a tuple, containig a list of abbreviations of countries from which the word came 
    to czech and a bool value describing whether a word is loan or not.
    '''
    etym_data = {}
    with open(filename, 'r') as etym_file:
        for line in etym_file.readlines():
            line = line.split('\t')
            word = line[0].strip()
            etymology = line[1].strip().split(', ')
            loan = line[2].strip()
            etym_data[word] = (etymology, loan)
    return etym_data
    

def main(filename: str):
    '''
    Writes etymological information to root lexeme
    to new feature Etymology as a list of abbreviations
    of countries.
    '''

    lexicon = dlex.Lexicon()  
    lexicon.load(data_source='../../../../derinet/data/releases/cs/derinet-2-1.tsv', on_err='continue')
    data = read_etym_data(filename)
    with open('loan_in_etymol_not_loan_derinet.tsv', 'w') as f_loan_etymol:
        with open('loan_in_derinet_not_loan_etymol.tsv', 'w') as f_loan_derinet:
            with open('different_info_for_root.tsv', 'w') as f_different_info:

                for word, (etymology, loan) in data.items():
                    lexemes = lexicon.get_lexemes(lemma=word)
                    for lexeme in lexemes:
                        root_lexeme = lexeme.get_tree_root()
                        if loan == 'True':
                            if 'Etymology' not in root_lexeme.feats:
                                
                                root_lexeme.add_feature('Etymology', etymology)
                                root_lexeme.add_feature('Etymology_base_word', word)
                               
                                if 'Loanword' in root_lexeme.feats:
                                    if root_lexeme.feats['Loanword'] == 'False':
                                        root_lexeme.feats['Loanword'] = 'True'
                                        f_loan_etymol.write(word + '\t' + root_lexeme.lemma + '\n')
                                else:
                                    root_lexeme.add_feature('Loanword', 'True')

                            else:
                                if not ( set(root_lexeme.feats['Etymology']).issubset(set(etymology))
                                    or set(etymology).issubset(set(root_lexeme.feats['Etymology']))):
                                    if root_lexeme.feats['Loanword'] == 'False':
                                        f_different_info.write("DIFF" + '\t' + root_lexeme.lemma + '\t' + 
                                                           word + '\t' + str(etymology) + '\t' 
                                                           + root_lexeme.feats['Etymology_base_word']
                                                           + '\t' + str(root_lexeme.feats['Etymology']) + '\n')
                                    else:
                                        f_different_info.write("SAME" + '\t' + root_lexeme.lemma + '\t' + 
                                                           word + '\t' + str(etymology) + '\t' 
                                                           + root_lexeme.feats['Etymology_base_word']
                                                           + '\t' + str(root_lexeme.feats['Etymology']) + '\n')

                        else:
                            if 'Etymology' not in root_lexeme.feats:
                                
                                root_lexeme.add_feature('Etymology', etymology)
                                root_lexeme.add_feature('Etymology_base_word', word)
                                if 'Loanword' in root_lexeme.feats:
                                    if root_lexeme.feats['Loanword'] == 'True':
                                        root_lexeme.feats['Loanword'] = 'False'
                                        f_loan_derinet.write(word + '\t' + root_lexeme.lemma + '\n')
                                else:
                                    root_lexeme.add_feature('Loanword', 'False')
                            else:
                                if not ( set(root_lexeme.feats['Etymology']).issubset(set(etymology))
                                    or set(etymology).issubset(set(root_lexeme.feats['Etymology']))):
                                    if root_lexeme.feats['Loanword'] == 'True':
                                        f_different_info.write("DIFF" + '\t' + root_lexeme.lemma + '\t' + 
                                                           word + '\t' + str(etymology) + '\t' 
                                                           + root_lexeme.feats['Etymology_base_word']
                                                           + '\t' + str(root_lexeme.feats['Etymology']) + '\n')
                                    else:
                                        f_different_info.write("SAME" + '\t' + root_lexeme.lemma + '\t' + 
                                                           word + '\t' + str(etymology) + '\t' 
                                                           + root_lexeme.feats['Etymology_base_word']
                                                           + '\t' + str(root_lexeme.feats['Etymology']) + '\n')

        

if __name__ == "__main__":
    tsv_file = 'all_etym_columns.tsv'
    main(tsv_file)
