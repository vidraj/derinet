import derinet.lexicon as dlex  # importing DeriNet API
import sys
sys.path.append("false_roots")
def main():
    groups_endings = ['ová', "ový", "ký", "mus", "vat","xx"]
    analise_false_filtred("false_roots_filtred_all.tsv",groups_endings,"false_roots_one_candidate.tsv","false_roots_rest.tsv")
    return
    lexicon = dlex.Lexicon()  # creating empty lexical network
    lexicon.load('derinet-2-1-1.tsv',on_err='continue')  # short notation of loading data (automatically loads data in dlex.Format.DERINET_V2)
    print("LOADED")
    filter_non_existent("false_roots.tsv","false_roots_filtred.tsv",lexicon)
    print("FILTERED")
    del lexicon  # clean RAM

def interactive(file_filtred:str):
    with open(file_filtred, 'rt') as filtred:
        query = input("Enter ending to look for: ")
        while query != "end":
            with open("false_roots_ending_" + query+ ".tsv", 'wt') as output:
                for line in filtred:
                    lemma, candidates = line.split('\t')
                    candidates_list = parse_list_from_string(candidates.strip())
                    if len(candidates_list) == 0: continue
                    if lemma.endswith(query):
                        print(line.strip(),file=output)
            query = input("Enter ending to look for: ")

def analise_false_filtred(file_filtred:str, groups_endings:list[str], file_one_candidate:str, file_rest:str):
    endings_dict = {}
    with (
        open(file_filtred, 'rt') as filtred,
        open(file_rest, 'wt') as rest,
        open(file_one_candidate, 'wt') as one_candidate
    ):
        for ending in groups_endings:
            endings_dict[ending] = []
        for line in filtred:
            lemma, candidates = line.split('\t')
            candidates_list = parse_list_from_string(candidates.strip())
            in_endings = False
            for ending in groups_endings:
                if lemma.endswith(ending):
                    in_endings = True
                    if ending == 'ová': # if the ending is 'ová' we want the first letter to be the same
                        checked_candidates_list = [candidate for candidate in candidates_list if candidate[0] == lemma[0]]
                    else: # in other case just so the first letter has the same case as candidate
                        checked_candidates_list = [candidate for candidate in candidates_list if candidate[0].isupper() == lemma[0].isupper()]
                    if len(checked_candidates_list) > 0:
                        endings_dict[ending].append(lemma + '\t' + ", ".join(checked_candidates_list))

            if not in_endings: # the line isnt in any ending group
                if len(candidates_list) == 1:
                    print(lemma, ", ".join(candidates_list), sep='\t',file=one_candidate)
                elif len(candidates_list) > 1:
                    print(lemma, ", ".join(candidates_list), sep='\t',file=rest)
    
    # Write the collected data to the respective files
    for ending, lines in endings_dict.items():
        with open(f"false_roots_{ending}_ending.tsv", 'wt') as file:
            for line in lines:
                print(line, file=file)



def parse_list_from_string(string_representation):
    """
    Converts a string representation of a list into an actual list without using ast or any other imports.
    
    Args:
        string_representation (str): The string representation of the list.
        
    Returns:
        list: The actual list parsed from the string representation.
    """
    # Ensure the string starts with '[' and ends with ']'
    if not (string_representation.startswith('[') and string_representation.endswith(']')):
        raise ValueError("The provided string does not represent a list.")
    
    # Remove the surrounding brackets and split by ','
    elements = string_representation[1:-1].split(',')
    
    # Strip whitespace and quotes from each element
    parsed_list = [element.strip().strip("'").strip('"') for element in elements if element != '']
    
    return parsed_list

def filter_non_existent(file_false_roots:str,file_false_roots_filtred:str,lexicon:dlex.Lexicon):
    # lemma	Correct_candidate	PaReNT_retrieval_candidates	PaReNT_classification	PaReNT_Compound_probability	PaReNT_Derivative_probability	PaReNT_Unmotivated_probability
    with open(file_false_roots, "rt") as false_roots, open(file_false_roots_filtred, "wt") as filtred, open("skipped.tsv", "wt") as not_found:
        next(false_roots)  # Skip the first line
        for line in false_roots:
            columns = line.split("\t")
            if len(columns) != 7:
                continue # skip lines which arent in right format
            lemma,correct_num, candidates_list, classification, compound_prob, derivation_prob, unmotivated_prob = columns

            try:
                candidates_list = parse_list_from_string(candidates_list)
            except:
                continue # skip invalid lines
            filtered_list = [candidate for candidate in candidates_list if candidate != lemma and lexicon.get_lexemes(candidate) != []]
            if len(filtered_list) == 0:
                print("Candidates list empty after filter",line.strip(),sep='\t',file=not_found)
            elif len(filtered_list) == 1:
                # there is just one valid candidate left
                print(lemma,filtered_list,file=filtred, sep='\t')
                pass
            else:
                print(lemma,filtered_list,file=filtred, sep='\t')
                pass
            #print(lemma,filtered_list,file=filtred, sep='\t')

if __name__ == "__main__":
    main()