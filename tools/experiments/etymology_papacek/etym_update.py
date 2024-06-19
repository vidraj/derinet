from parse_etym_data_file import parse_data,parse_data_tsv
import derinet.lexicon as dlex  # importing DeriNet API
import time
import re
import sys

def extract_field(dictionary: dict[str, dict[str, any]], field: str, verbose:bool = True) -> dict[str, list[str]]:
    """
    Extracts a specified field for each entry from a dictionary representing the Etymological dictionary.
    
    Args:
        dictionary (dict[str, dict[str, any]]): A dictionary where each key is an entry and each value is another dictionary containing various fields.
        field (str): The field to extract for each entry.
    
    Returns:
        dict[str, list[str]]: A new dictionary with entries as keys and lists of the specified field's values as values.
    """
    field_only_dict = {}
    if verbose:
            print(f"Extracting dictionary with just field: {field}")
    for key in dictionary.keys():
        field_only_dict[key] = dictionary[key].get(field, []) #carefuly when the dictionary[key] contains strings and not lists (but the value should always be there so the default one shouldnt be used ever)
    if verbose:
            print(f"Extraction of field: {field} from the dictionary finished")
    return field_only_dict

def get_dict_without_multiple_word_entries_and_derivations(dictionary:dict[str,list[str]], verbose:bool = True) -> dict[str,list[str]]:
    """Creates new dict with multiple word entries like \'naučit se\' or \'fata morgana\' removed. Same in the list of derivations
        Examples: fata morgána, fifty fifty, happy end, křížem krážem, perpetuum mobile, but mostly 'učit se', 'zpívat si'
    """
    if verbose: print()
    one_word_dict = {}
    shorten_entries_counter = 0
    for entry,derivations in dictionary.items():
        shorten_derivations = [derivation.split()[0] for derivation in derivations if derivation.split()] # if in ["(se)", 'se', 'si', '(si)']:
        shorten_entry = entry.split()[0]
        if len(entry.split()) == 1: # only one word
            one_word_dict[entry] = shorten_derivations
        else:
            if entry.split()[1] not in ["(se)", 'se', 'si', '(si)']:
                #print(entry) 
                # it is some other compound than just ading se or si after verbs
                pass
            shorten_entries_counter += 1
            one_word_dict[shorten_entry] = shorten_derivations
    if verbose:
        print("Entries shorten:", shorten_entries_counter)
    return one_word_dict

def normalize_words(dictionary: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Normalize entries and list of derivations by splitting derivations containing parentheses into two derivations.
    For example, 'učitel(ka)' becomes 'učitel' and 'učitelka'.

    Also removes duplicite words in the lists

    Args:
        dictionary (dict[str, list[str]]): A dictionary where each key is an entry and each value is a list of derivations.
    
    Returns:
        dict[str, list[str]]: A dictionary with the normalized entries.
    """
    normalized_entries_dict = {}
    # Pattern to find words containing parentheses, like "ucitel(ka), (z)bourat"
    pattern = re.compile(r'(\w*)\((\w*)\)(\w*)')
    for entry, derivations in dictionary.items():
        entry = re.sub(r'[^a-zA-ZřščžáéíóúýčďěňřšťůžŘŠČŽÁÉÍÓÚÝČĎĚŇŘŠŤŮŽ]', '', entry)
        modified_derivations = set()
        for derivation in derivations:
            # Search for the pattern in each derivation
            match = pattern.search(derivation)
            if match:
                prefix, infix, suffix = match.groups()
                # Create the two new derivations
                modified_derivations.add(prefix + suffix)
                modified_derivations.add(prefix + infix + suffix)
            elif '/' in derivation:
                # Split words separated by slash into two words
                parts = derivation.split('/')
                for part in parts:
                    modified_derivations.add(part)
            elif not derivation.isalpha():
                # there may be parantheses left at beginning or end or some digit after the word
                modified_derivations.add(re.sub(r'[^a-zA-ZřščžáéíóúýčďěňřšťůžŘŠČŽÁÉÍÓÚÝČĎĚŇŘŠŤŮŽ]', '', derivation))
            else:
                # Add the unmodified derivation
                modified_derivations.add(derivation)        
            normalized_entries_dict[entry] = list(modified_derivations)
    return normalized_entries_dict

def show_entries_by_one(dictionary:dict):
    for entry,value in dictionary.items():
        print(entry, value)
        input("Press enter to continue")

def save_normalized_dict_derivations(dictionary:dict[str,list[str]],filaname:str,omit_empty:bool = True):
    """Saves the dictionary where key is the entry and value is list of potentional derivations
        Parameters: 
            dictionary - the dictionary in normalized form (key: str - entry, value: list[str] - list of potentional derivations for the entry).
                Keys are without '()' and trimted to one word. (koukat se -> koukat, spisovatel(ka) -> 2 entries spisovatel, spisovatelka)
            filename - name of file where to save the dictionary
            omit_empty: bool - if omit or include entries with empty potentional derivations lists. Default True
    """
    with open(filaname, 'wt') as output_file:
        for entry, derivations in dictionary.items():
            if not omit_empty or len(derivations) != 0:
                print(entry, ", ".join(derivations),file=output_file,sep='\t')

def load_normalized_dictionary(filename:str) -> dict[str,list[str]]:
    dictionary = dict()
    with open(filename, 'rt') as file_dict:
        for line in file_dict:
            line_split = line.split('\t')
            if len(line_split) == 2:
                entry,derivations = line_split
                dictionary[entry] = derivations.rstrip().split(', ')
            else:
                dictionary[line] = []
    return dictionary


    
def update_lexicon_slim(lexicon:dlex.Lexicon,filename_normalized_dict:str):
    """
    Processes the lexicon by iterating through its trees and comparing derivations with the normalized dictionary.
    Adds the derivations described in the Etymological dict which are not present in DeriNet.
    Args:
        lexicon: The lexicon object of DeriNet
    """
    added_derivations_counter = 0
    dictionary_normalized = load_normalized_dictionary(filename_normalized_dict)
    for tree_root in lexicon.iter_trees():  # iterate through trees
        # Initialize an empty dict to store derivations as keys and their parent as values
        dict_derivations_from_etym_dictionary = dict()

        # Iterate through each lexeme in the subtree of the tree_root
        # Adding all derivations from etym dict
        for lexeme in tree_root.iter_subtree():
            lemma = lexeme.lemma
            # Get derivations from the normalized dictionary for the current lemma
            lemma_derivations = dictionary_normalized.get(lemma)      
            if lemma_derivations:
                for derivation in lemma_derivations:
                    if derivation.strip():
                        dict_derivations_from_etym_dictionary[derivation] = lexeme # add the derivation - parent pair to the dictionary

        # removing the already present derivations
        if len(dict_derivations_from_etym_dictionary.keys()) != 0:
            for lexeme in tree_root.iter_subtree():
                lemma = lexeme.lemma
                if lemma in dict_derivations_from_etym_dictionary.keys():
                    dict_derivations_from_etym_dictionary.pop(lemma) # remove the derivation because it is already in the DeriNet tree
        
        # adding the missing derivations
        if len(dict_derivations_from_etym_dictionary.keys()) != 0:
            for derivation_not_present in dict_derivations_from_etym_dictionary.keys():
                lexeme = lexicon.get_lexemes(lemma=derivation_not_present)
                if len(lexeme) == 1:  # if there are not homonymous lexemes, return first (only) one
                    lexeme = lexeme[0]
                    if lexeme.parent_relation is None: # the lexeme is root, connect it directly
                        try:
                            lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],lexeme)
                            added_derivations_counter += 1
                        except:
                            # there can be some errors with cyclic relations. Two errors that occured:
                            # Lexeme:játra#NNN??-----A---?, Tree root: celý#AA???----??---?, parent: jitrocel#NNI??-----A---?
                            # Lexeme:don#NNM??-----A---?, Tree root: Quijote#NNMXX-----A----, parent: donkichot#NNM??-----A---?
                            pass
                    else:
                        # the found derivation is not root of a tree, we will connect the whole tree (the root) instead
                        root_of_derivation_lexeme = lexeme.get_tree_root()
                        if root_of_derivation_lexeme != tree_root:
                            lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],root_of_derivation_lexeme)                            
                            added_derivations_counter += 1

                        else:
                            pass
                            # for example for agent we have derivations found in Etym dict ['agentura', 'agenturni'] which are missing in Derinte
                            # However 'agentura' is root of tree containing 'agenturni' so when 'agentura' is added to 'agent' as derivation
                            # the root of 'agenturni' now becomes 'agent' so its already in the tree, we dont add it
    print(added_derivations_counter)

def update_lexicon(lexicon:dlex.Lexicon, file_added_derivations_direct:str, file_added_derivations_with_intermediates:str, dictionary_normalized:dict[str,list[str]], verbose:bool=True):
    """
    Processes the lexicon by iterating through its trees and comparing derivations with the normalized dictionary.
    Outputs information about new derivations and connections to the specified files.

    Args:
        lexicon: The lexicon object of DeriNet
        file_trees_and_not_present_derivations: File path to write information about trees and new derivations not present in the lexicon.
        file_added_derivations: File path to write information about added derivations to the lexicon.
        dictionary_normalized: A dictionary with normalized derivations for comparison.
        verbose (bool): If True, prints additional information about the processing.
    """
    if verbose:
        print(f"Starting to process lexicon with file_added_derivations: {file_added_derivations_with_intermediates}")

    with open(file_added_derivations_with_intermediates, "wt") as added_derivations_intermediates, open(file_added_derivations_direct, "wt") as added_derivations_direct:
        header_not_root = "parent\tgrandparent\tderivation"
        print(header_not_root,file=added_derivations_intermediates)
        header_root = "derivation\tparent"
        print(header_root,file=added_derivations_direct)
        counter = 0  # Trees printed counter
        potentionaly_new_words = 0
        lexeme_not_found_counter = 0
        homonyms_counter = 0
        root_derivation_same_as_tree_root_counter = 0
        not_found_words = set()

        for tree_root in lexicon.iter_trees():  # iterate through trees
            # Initialize an empty dict to store derivations as keys and their parent as values
            dict_derivations_from_etym_dictionary = dict()

            # Iterate through each lexeme in the subtree of the tree_root
            for lexeme in tree_root.iter_subtree():
                lemma = lexeme.lemma
                # Get derivations from the normalized dictionary for the current lemma
                lemma_derivations = dictionary_normalized.get(lemma)      
                if lemma_derivations:
                    for derivation in lemma_derivations:
                        if derivation.strip():
                            dict_derivations_from_etym_dictionary[derivation] = lexeme # add the derivation - parent pair to the dictionary
                       
            if len(dict_derivations_from_etym_dictionary.keys()) != 0:
                for lexeme in tree_root.iter_subtree():
                    lemma = lexeme.lemma
                    if lemma in dict_derivations_from_etym_dictionary.keys():
                        dict_derivations_from_etym_dictionary.pop(lemma) # remove the derivation because it is already in the DeriNet tree
            if len(dict_derivations_from_etym_dictionary.keys()) != 0:
                potentionaly_new_words += len(dict_derivations_from_etym_dictionary.keys())

                for derivation_not_present in dict_derivations_from_etym_dictionary.keys():
                    lexeme = lexicon.get_lexemes(lemma=derivation_not_present)
                    if len(lexeme) == 1:  # if there are not homonymous lexemes, return first (only) one
                        lexeme = lexeme[0]
                        if lexeme.parent_relation is None: # the lexeme is root, connect it directly
                            if dict_derivations_from_etym_dictionary[derivation_not_present].lemma != lexeme.lemma:
                                try:
                                    lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],lexeme)
                                except:
                                    # there can be some errors with cyclic relations. Two errors that occured:
                                    # Lexeme:játra#NNN??-----A---?, Tree root: celý#AA???----??---?, parent: jitrocel#NNI??-----A---?
                                    # Lexeme:don#NNM??-----A---?, Tree root: Quijote#NNMXX-----A----, parent: donkichot#NNM??-----A---?
                                    if verbose:
                                        print(f"EROR!\nLexeme:{lexeme}, Tree root: {tree_root}, parent: {dict_derivations_from_etym_dictionary[derivation_not_present]}")
                                counter += 1
                                print(f"{lexeme}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}",file=added_derivations_direct)
                            else:
                                pass
                                #print(f"OMITED {lexeme}, lemma {lexeme.lemma}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}, lemma {dict_derivations_from_etym_dictionary[derivation_not_present].lemma}")
                        else:
                            # the found derivation is not root of a tree, we will connect the whole tree (the root of the derivation) instead
                            root_of_derivation_lexeme = lexeme.get_tree_root()
                            
                            if root_of_derivation_lexeme != tree_root:
                                # the target lexeme already has a parent, connect the whole tree (the root of lexeme) to the tree_root
                                if dict_derivations_from_etym_dictionary[derivation_not_present].lemma != root_of_derivation_lexeme.lemma:
                                    lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],root_of_derivation_lexeme)                            
                                    counter += 1
                                    print(f"{root_of_derivation_lexeme}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}\t{lexeme}",file=added_derivations_intermediates)                                
                                else:
                                    pass
                                    # print(f"OMITED {root_of_derivation_lexeme}, lemma {root_of_derivation_lexeme.lemma}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}, lemma {dict_derivations_from_etym_dictionary[derivation_not_present].lemma}")
                                    
                            else:
                                root_derivation_same_as_tree_root_counter += 1
                                # for example for agent we have derivations found in Etym dict ['agentura', 'agenturni'] which are missing in Derinte
                                # However 'agentura' is root of tree containing 'agenturni' so when 'agentura' is added to 'agent' as derivation
                                # the root of 'agenturni' now becomes 'agent' so its already in the tree, we dont add it
                    elif len(lexeme) == 0:
                        not_found_words.add(derivation_not_present)
                        lexeme_not_found_counter += 1
                    else:
                        homonyms_counter += 1
                        # print("Lexeme with homonyms:", derivation_not_present)
        
        if verbose:
            print("Potentialy new words:", potentionaly_new_words)
            print("Added relations:", counter)
            print("Lexemes not found:", lexeme_not_found_counter)
            print("Root of Lexemes same as roots of given trees:", root_derivation_same_as_tree_root_counter)
            print("Lexemes with homonyms:", homonyms_counter)
            print("Not found words:\n", not_found_words)
            with open("not_found_words.txt", "at") as not_found:
                print("\n", file=not_found)
                for word in not_found_words:
                    print(word,file=not_found)
            print("\nFinished processing lexicon")

def invert_dictionary(original_dict: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Inverts a dictionary where keys are strings and values are lists of strings.
    The resulting dictionary will have strings from the lists as keys, and values will be lists of all keys from the original
    dictionary that had the string in their value list.

    Args:
        original_dict (dict[str, list[str]]): The original dictionary to be inverted.

    Returns:
        dict[str, list[str]]: The inverted dictionary.
    """
    inverted_dict = {}

    for key, value_list in original_dict.items():
        for value in value_list:
            if value not in inverted_dict:
                inverted_dict[value] = []
            inverted_dict[value].append(key)
    return inverted_dict

def jaccard_similarity(word1, word2, n=2):
    """
    Calculate Jaccard similarity between two words based on character n-grams.

    Args:
        word1 (str): The first word.
        word2 (str): The second word.
        n (int): The length of the n-grams.

    Returns:
        float: Jaccard similarity index.
    """
    def ngrams(word, n):
        return set(word[i:i+n] for i in range(len(word) - n + 1))

    ngrams1 = ngrams(word1, n)
    ngrams2 = ngrams(word2, n)

    intersection = ngrams1.intersection(ngrams2)
    union = ngrams1.union(ngrams2)

    return len(intersection) / len(union)

def check_derinet_inconsistencies(lexicon:dlex.Lexicon, inverted_etym_dict:dict[str, list[str]], filename_logging:str):
    """Iterates through all trees and checks if in the same trees arent 2 nodes which have different root based on Etym Dict"""
    inconsistencies = set()
    with open(filename_logging, 'wt') as log:
        for root in lexicon.iter_trees():
            for node1 in root.iter_subtree():
                parents1 = inverted_etym_dict.get(node1.lemma,[]) # for most cases this is list with one element
                for node2 in root.iter_subtree(): # we check all pairs twice, could be done in some more effective way
                    if jaccard_similarity(node1.lemma,node2.lemma) > 0.4: 
                        continue # skip words that have "high" similarity
                    parents2 = inverted_etym_dict.get(node2.lemma,[]) # for most cases this is list with one element
                    if parents2 != [] and parents1 != []:
                        have_common_parent = False
                        for parent1 in parents1:
                            for parent2 in parents2:
                                if parent1 == parent2:
                                    have_common_parent = True
                                    break
                                parent1_lexemes = lexicon.get_lexemes(parent1)
                                parent2_lexemes = lexicon.get_lexemes(parent2)
                                for lexeme1 in parent1_lexemes:
                                    for lexeme2 in parent2_lexemes:
                                        if lexeme1.get_tree_root() == lexeme2.get_tree_root():
                                            have_common_parent = True
                                            break
                            if have_common_parent: 
                                break

                        if not have_common_parent:
                            if node1 < node2:
                                inconsistencies.add(f"Node1: {node1}, parents1 Etym {parents1}\tNode2: {node2}, parents2 Etym {parents2}\tRoot: {root}")
                            else:
                                inconsistencies.add(f"Node1: {node2}, parents1 Etym {parents2}\tNode2: {node1}, parents2 Etym {parents1}\tRoot: {root}")
        for line in inconsistencies:
            print(line,file=log)

def main():

    time1 = time.time()
    build_normalized_extracted_dict = True # if build normallized dict from parsed_dictionary.tsv or if loading it directly
    slim = False # slim == True => not printing anything, not saving anything to files
    # file to stored the modified version to
    file_updated_version = "new-derinet-2-1-1.tsv"

    if build_normalized_extracted_dict:
        dict_file = 'parsed_dictionary.txt'
        dict_file_tsv = 'parsed_dictionary.tsv'
        dictionary = parse_data_tsv(dict_file_tsv)
        #dictionary = parse_data(dict_file)


        dictionary_derivatios_only = extract_field(dictionary,'derivations')
        dictionary_normalized_derivations = normalize_words(get_dict_without_multiple_word_entries_and_derivations(dictionary_derivatios_only))
        

        inverted_dictionary_derivations = invert_dictionary(dictionary_normalized_derivations)
        save_normalized_dict_derivations(inverted_dictionary_derivations,"inverted_dict.tsv")

        dictionary_srov_only = extract_field(dictionary,'srov')
        dictionary_normalized_srov = normalize_words(get_dict_without_multiple_word_entries_and_derivations(dictionary_srov_only))
        
        
       
        save_normalized_dict_derivations(dictionary_normalized_derivations,"normalized_derivations.tsv", omit_empty=True)
       
        save_normalized_dict_derivations(dictionary_normalized_srov,"normalized_srov.tsv", omit_empty=True)

    time2 = time.time()
    print("\nFirst section - Extract and Normalize dictionary - took:", time2 - time1,"s to complete")
    
    lexicon = dlex.Lexicon()  # creating empty lexical network
    lexicon.load('derinet-2-1-1.tsv',on_err='continue')  # short notation of loading data (automatically loads data in dlex.Format.DERINET_V2)


    time3 = time.time()
    print("\nSecond section - Loading DeriNet - took:", time3 - time2,"s to complete")

    check_derinet_inconsistencies(lexicon,invert_dictionary(dictionary_normalized_derivations),"inconsistences.tsv")

    """

    if slim:
        update_lexicon_slim(lexicon,'normalized_derivations.tsv')
    else:
        # from data in 'derivations'
        file_added_derivations_direct = "added_derivations_direct-2.1-1.tsv"
        file_added_derivations_with_intermediates = "added_derivations_intermediates-2.1-1.tsv"

        # from data in 'srov'
        file_added_derivations_srov_direct = "added_derivations_srov_direct-2.1-1.tsv"
        file_added_derivations_with_intermediates_srov = "added_derivations_srov_intermediates-2.1-1.tsv"

        # file to stored the modified version to
        file_updated_version = "new-derinet-2-1-1.tsv"

        # update lexicon with derivations
        update_lexicon(lexicon,file_added_derivations_direct,file_added_derivations_with_intermediates,dictionary_normalized_derivations)    

        # update lexicon with srov
        update_lexicon(lexicon,file_added_derivations_srov_direct,file_added_derivations_with_intermediates_srov,dictionary_normalized_srov)    
    """

    time4 = time.time()
    print("\nThird section - Adding derivations - took:", time4 - time3,"s to complete")
    sys.exit(0) # comment this line to save


    lexicon.save(data_sink=file_updated_version, fmt=dlex.Format.DERINET_V2)  # full notation of saving data
    del lexicon  # clean RAM

    time4 = time.time()
    print("\nFourth section - Saving - took:", time4 - time3,"s to complete")

if __name__ == "__main__":
    main()