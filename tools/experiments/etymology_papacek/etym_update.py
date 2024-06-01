from parse_etym_data_file import parse_data,parse_data_tsv
import derinet.lexicon as dlex  # importing DeriNet API
import time
import re
import sys


#GLOBAL
verbose = True

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

def normalize_words(dictionary: dict[str, list[str]], verbose:bool = True) -> dict[str, list[str]]:
    """
    Normalize entries and list of derivations by splitting derivations containing parentheses into two derivations.
    For example, 'učitel(ka)' becomes 'učitel' and 'učitelka'.
    
    Args:
        dictionary (dict[str, list[str]]): A dictionary where each key is an entry and each value is a list of derivations.
    
    Returns:
        dict[str, list[str]]: A dictionary with the normalized entries.
    """
    normalized_entries_dict = {}
    modified_entries_count = 0

    # Pattern to find words containing parentheses, like "ucitel(ka), (z)bourat"
    pattern = re.compile(r'(\w*)\((\w*)\)(\w*)')

    for entry, derivations in dictionary.items():
        modified_derivations = []
        modified = False

        for derivation in derivations:
            # Search for the pattern in each derivation
            match = pattern.search(derivation)
            if match:
                prefix, infix, suffix = match.groups()
                # Create the two new derivations
                modified_derivations.extend([prefix + suffix, prefix + infix + suffix])
                modified = True
            elif '/' in derivation:
                # Split words separated by slash into two words
                parts = derivation.split('/')
                modified_derivations.extend(parts)
                modified = True
            elif not derivation.isalpha():
                modified_derivations.append(derivation.strip('();\'123-')) # there may be parantheses left at beginning or end or some digit after the word
                modified = True
            else:
                # Add the unmodified derivation
                modified_derivations.append(derivation)        
        if modified:
            modified_entries_count += 1
            normalized_entries_dict[entry] = modified_derivations
        else:
            normalized_entries_dict[entry] = derivations
    if verbose:
        print("Entries modified:", modified_entries_count)
    return normalized_entries_dict

def show_entries_by_one(dictionary:dict):
    for entry,value in dictionary.items():
        print(entry, value)
        input("Press enter to continue")

def process_lexicon(lexicon:dlex.Lexicon, file_to_print_trees_and_not_present_derivations:str, file_added_derivations:str, dictionary_normalized:dict[str,list[str]], verbose:bool=True):
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
    with open(file_added_derivations, "wt") as added_derivations, open(file_to_print_trees_and_not_present_derivations, "wt") as trees_and_new_derivations:
        counter = 0  # Trees printed counter
        new_words = 0
        lexeme_not_found_counter = 0
        homonyms_counter = 0
        root_derivation_same_as_tree_root_counter = 0
        not_found_words = []

        for tree_root in lexicon.iter_trees():  # iterate through trees
            if tree_root.lemma in ["agent","balanc", 'blesk','centr', 'mysl']:
                pass
            etym_dict_derivations = dictionary_normalized.get(tree_root._lemma)
            # if etym_dict_derivations == None or etym_dict_derivations == [""]: continue
            
            etym_dict_derivations_copy = set(etym_dict_derivations) if etym_dict_derivations and etym_dict_derivations != [""] else set()
            for lexeme in tree_root.iter_subtree():
                lemma = lexeme.lemma
                lemma_derivations = dictionary_normalized.get(lemma)  # get derivations from etym dict for derivations in the tree in DERINET
                if lemma_derivations:
                    lemma_derivations = set(lemma_derivations)
                    for derivation in lemma_derivations:
                        if derivation.strip() != "":
                            etym_dict_derivations_copy.add(derivation)  # set add, list append!!!
                            # Now I am adding all derivations to the same list so they will be all eventually connected to the root
                            # it would be correct to connect them to the subtree instead
            if len(etym_dict_derivations_copy) != 0:
                # print(etym_dict_derivations_copy)
                if tree_root.lemma in etym_dict_derivations_copy:
                    etym_dict_derivations_copy.remove(tree_root.lemma)
                for lexeme in tree_root.iter_subtree():
                    lemma = lexeme.lemma
                    # print(lemma, (lemma in etym_dict_derivations_copy))
                    if lemma in etym_dict_derivations_copy:
                        etym_dict_derivations_copy.remove(lemma)
            if len(etym_dict_derivations_copy) != 0:
                new_words += len(etym_dict_derivations_copy)
                print("Lemma:", tree_root._lemma, file=trees_and_new_derivations)
                print("Tree:", file=trees_and_new_derivations)
                print("\n".join(tree_root._pprint_subtree_indented("", "")), file=trees_and_new_derivations)  # pretty print to file
                print("Etym dict derivations all:", etym_dict_derivations, file=trees_and_new_derivations)
                print("Etym dict derivations NOT present in derinet:", etym_dict_derivations_copy, file=trees_and_new_derivations)
                for derivation_not_present in etym_dict_derivations_copy:
                    lexeme = lexicon.get_lexemes(lemma=derivation_not_present)
                    if len(lexeme) == 1:  # if there are not homonymous lexemes, return first (only) one
                        lexeme = lexeme[0]
                        if lexeme.get_tree_root() != lexeme:
                            # the found derivation is not root of a tree, connect the whole tree (the root) instead
                            pass
                            # print("!!Target lexeme isn't root!!\n Lexeme:", lexeme.lemma, ", Tree root:", lexeme.get_tree_root().lemma)  # lexemes that are not roots of trees
                        if lexeme.parent_relation is None: # the lexeme is root, connect it directly
                            lexicon.add_derivation(tree_root, lexeme)
                            counter += 1
                            print(f"Adding relation, source: {tree_root}, target {lexeme} which was originally root", file=added_derivations)
                        else:
                            root_of_derivation_lexeme = lexeme.get_tree_root()
                            if root_of_derivation_lexeme != tree_root:
                                # the target lexeme already has a parent, connect the whole tree (the root of lexeme) to the tree_root
                                lexicon.add_derivation(tree_root, root_of_derivation_lexeme)  # add the derivation to the lexicon
                                counter += 1
                                print(f"Adding relation, source: {tree_root}, target {root_of_derivation_lexeme} which is root of tree containing {lexeme} which is derivation of {tree_root} or some of his children", file=added_derivations)
                                # I should add the derivation edge to the node which has the lexeme as its derivation, not to the root !!!
                            else:
                                root_derivation_same_as_tree_root_counter += 1
                                # for example for agent we have derivations found in Etym dict ['agentura', 'agenturni'] which are missing in Derinte
                                # However 'agentura' is root of tree containing 'agenturni' so when 'agentura' is added to 'agent' as derivation
                                # the root of 'agenturni' now becomes 'agent' so its already in the tree, we dont add it

                    elif len(lexeme) == 0:
                        not_found_words.append(derivation_not_present)
                        lexeme_not_found_counter += 1
                        
                    else:
                        homonyms_counter += 1
                        # print("Lexeme with homonyms:", derivation_not_present)
        
        if verbose:
            print("New words:", new_words)
            print("Added relations:", counter)
            print("Lexemes not found:", lexeme_not_found_counter)
            print("Root of Lexemes same as roots of given trees:", root_derivation_same_as_tree_root_counter)
            print("Lexemes with homonyms:", homonyms_counter)
            print("Not found words:\n", not_found_words)

def main():

    time1 = time.time()

    dict_file = 'parsed_dictionary.txt'
    dict_file_tsv = 'parsed_dictionary.tsv'
    dictionary = parse_data_tsv(dict_file_tsv)
    #dictionary = parse_data(dict_file)

    dictionary_derivatios_only = extract_field(dictionary,'derivations')
    dictionary_srov_only = extract_field(dictionary,'srov')

    dictionary_one_word_derivations_only = get_dict_without_multiple_word_entries_and_derivations(dictionary_derivatios_only)
    dictionary_normalized_derivations = normalize_words(dictionary_one_word_derivations_only)
    dictionary_normalized_srov = normalize_words(get_dict_without_multiple_word_entries_and_derivations(dictionary_srov_only))
    #dictionary_normalized_derivations = dictionary_normalized_srov # JUST TESTING DELETE THIS LINE 
    time2 = time.time()
    print("First section - Extract and Normalize dictionary - took:", time2 - time1,"s to complete")

    lexicon = dlex.Lexicon()  # creating empty lexical network
    lexicon.load('derinet-2-1-1.tsv',on_err='continue')  # short notation of loading data (automatically loads data in dlex.Format.DERINET_V2)


    time3 = time.time()
    print("Second section - Loading DeriNet - took:", time3 - time2,"s to complete")


    file_trees_and_not_present_derivations = "trees_with_some_new_derivations-2.1-1.txt"
    file_added_derivations = "added_derivations-2.1-1.txt"
    file_added_derivations_from_srov = "added_derivations_srov-2.1-1.txt"
    file_updated_version = "new-derinet-2-1-1.tsv"

    process_lexicon(lexicon,file_trees_and_not_present_derivations,file_added_derivations,dictionary_normalized_derivations)    

    time4 = time.time()
    print("Third section - Adding derivations - took:", time4 - time3,"s to complete")
    sys.exit(0) # uncomment to save


    lexicon.save(data_sink=file_updated_version, fmt=dlex.Format.DERINET_V2)  # full notation of saving data
    del lexicon  # clean RAM

    time4 = time.time()
    print("Fourth section - Saving - took:", time4 - time3,"s to complete")

if __name__ == "__main__":
    main()