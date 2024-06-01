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
                #modified_derivations.append(derivation.strip('();\'123-')) # there may be parantheses left at beginning or end or some digit after the word
                modified_derivations.append(re.sub(r'[^a-zA-ZřščžáéíóúýčďěňřšťůžŘŠČŽÁÉÍÓÚÝČĎĚŇŘŠŤŮŽ]', '', derivation))
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
        header_not_root = "derivation\tparent\tintermediate_node"
        print(header_not_root,file=added_derivations_intermediates)
        header_root = "derivation\tparent"
        print(header_root,file=added_derivations_direct)
        counter = 0  # Trees printed counter
        potentionaly_new_words = 0
        lexeme_not_found_counter = 0
        homonyms_counter = 0
        root_derivation_same_as_tree_root_counter = 0
        not_found_words = []

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
                            try:
                                lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],lexeme)
                            except:
                                # there can be some errors with cyclic relations. Two errors that occured:
                                # Lexeme:játra#NNN??-----A---?, Tree root: celý#AA???----??---?, parent: jitrocel#NNI??-----A---?
                                # Lexeme:don#NNM??-----A---?, Tree root: Quijote#NNMXX-----A----, parent: donkichot#NNM??-----A---?
                                if verbose:
                                    print(f"Lexeme:{lexeme}, Tree root: {tree_root}, parent: {dict_derivations_from_etym_dictionary[derivation_not_present]}")
                            counter += 1
                            print(f"{lexeme}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}",file=added_derivations_direct)
                        else:
                            # the found derivation is not root of a tree, we will connect the whole tree (the root) instead
                            root_of_derivation_lexeme = lexeme.get_tree_root()
                            if root_of_derivation_lexeme != tree_root:
                                # the target lexeme already has a parent, connect the whole tree (the root of lexeme) to the tree_root
                                #lexicon.add_derivation(tree_root, root_of_derivation_lexeme)  # add the derivation to the lexicon
                                lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],root_of_derivation_lexeme)                            
                                counter += 1
                                print(f"{root_of_derivation_lexeme}\t{dict_derivations_from_etym_dictionary[derivation_not_present]}\t{lexeme}",file=added_derivations_intermediates)                                
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
            print("Potentialy new words:", potentionaly_new_words)
            print("Added relations:", counter)
            print("Lexemes not found:", lexeme_not_found_counter)
            print("Root of Lexemes same as roots of given trees:", root_derivation_same_as_tree_root_counter)
            print("Lexemes with homonyms:", homonyms_counter)
            print("Not found words:\n", not_found_words)
            print("\nFinished processing lexicon")

def main():

    time1 = time.time()

    dict_file = 'parsed_dictionary.txt'
    dict_file_tsv = 'parsed_dictionary.tsv'
    dictionary = parse_data_tsv(dict_file_tsv)
    #dictionary = parse_data(dict_file)

    dictionary_derivatios_only = extract_field(dictionary,'derivations')
    dictionary_normalized_derivations = normalize_words(get_dict_without_multiple_word_entries_and_derivations(dictionary_derivatios_only))

    dictionary_srov_only = extract_field(dictionary,'srov')
    dictionary_normalized_srov = normalize_words(get_dict_without_multiple_word_entries_and_derivations(dictionary_srov_only))

    time2 = time.time()
    print("\nFirst section - Extract and Normalize dictionary - took:", time2 - time1,"s to complete")

    lexicon = dlex.Lexicon()  # creating empty lexical network
    lexicon.load('derinet-2-1-1.tsv',on_err='continue')  # short notation of loading data (automatically loads data in dlex.Format.DERINET_V2)


    time3 = time.time()
    print("\nSecond section - Loading DeriNet - took:", time3 - time2,"s to complete")

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

    time4 = time.time()
    print("\nThird section - Adding derivations - took:", time4 - time3,"s to complete")
    #sys.exit(0) # comment this line to save


    lexicon.save(data_sink=file_updated_version, fmt=dlex.Format.DERINET_V2)  # full notation of saving data
    del lexicon  # clean RAM

    time4 = time.time()
    print("Fourth section - Saving - took:", time4 - time3,"s to complete")

if __name__ == "__main__":
    main()