from parse_etym_data_file import parse_data
import derinet.lexicon as dlex  # importing DeriNet API
import time
import re
import sys

def extract_derivations_only(dictionary:dict[str,dict[str,str]]) -> dict[str,list[str]]:
    """Takes in dictionary representing the Etymological dictionary (dict with entries as keys and dict containg the data as values).
        Extracts only the derivations for each entry
        Returns new dict with entries as keys and list of derivations as values.
    """
    derivations_only_dict = {}
    for key in dictionary.keys():
        derivations_only_dict[key] = dictionary[key]['derivations']
    return derivations_only_dict

def get_dict_without_multiple_word_entries_and_derivations(dictionary:dict[str,list[str]]) -> dict[str,list[str]]:
    """Creates new dict with multiple word entries like \'naučit se\' or \'fata morgana\' removed. Same in the list of derivations
        Examples: fata morgána, fifty fifty, happy end, křížem krážem, perpetuum mobile, but mostly 'učit se', 'zpívat si'
    """
    one_word_dict = {}
    shorten_entries_counter = 0
    shorten_derivations_counter = 0
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
    print("Entries shorten:", shorten_entries_counter)
    return one_word_dict

def normalize_words(dictionary: dict[str, list[str]]) -> dict[str, list[str]]:
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
                #print(modified_derivations)
                #input("press enter to continue")
                modified = True
            else:
                # Add the unmodified derivation
                modified_derivations.append(derivation)

        if modified:
            modified_entries_count += 1
            normalized_entries_dict[entry] = modified_derivations
        else:
            normalized_entries_dict[entry] = derivations

    print("Entries modified:", modified_entries_count)
    return normalized_entries_dict


def show_entries_by_one(dictionary:dict):
    for entry,value in dictionary.items():
        print(entry, value)
        input("Press enter to continue")

def main():

    time1 = time.time()

    dict_file = 'parsed_dictionary.txt'
    dictionary = parse_data(dict_file)
    dictionary_derivatios_only = extract_derivations_only(dictionary)
    dictionary_one_word_derivations_only = get_dict_without_multiple_word_entries_and_derivations(dictionary_derivatios_only)
    dictionary_normalized = normalize_words(dictionary_one_word_derivations_only)


    time2 = time.time()
    print("First section took:", time2 - time1,"s to complete")

    lexicon = dlex.Lexicon()  # creating empty lexical network
    lexicon.load('derinet-2-1.tsv',on_err='continue')  # short notation of loading data (automatically loads data in dlex.Format.DERINET_V2)
    #lexicon.load('derinet-2-0.tsv',on_err='continue')  # version 2-0


    time3 = time.time()
    print("Second section took:", time3 - time2,"s to complete")


    file_trees_and_not_present_derivations = "trees_with_some_new_derivations.txt"
    file_added_derivations = "added_derivations.txt"
    file_trees_and_not_present_derivations = "trees_with_some_new_derivations-2.1.txt"
    file_added_derivations = "added_derivations-2.1.txt"
    file_updated_version = "new-derinet-2-1.tsv"
    with open(file_added_derivations, "wt") as added_derivations:
        with open(file_trees_and_not_present_derivations, "wt") as trees_and_new_derivations:
            counter = 0 # trees printed counter
            new_words = 0
            modulo = 10
            lexeme_not_found_counter = 0
            hononyms_counter = 0
            i = 0 #iteration counter
            not_found_words = []
            for tree_root in lexicon.iter_trees():  # iterate through trees
                i+=1
                etym_dict_derivations = dictionary_normalized.get(tree_root._lemma)
                #if etym_dict_derivations == None or etym_dict_derivations == [""]: continue
                #if counter > 1_000: break
                
                etym_dict_derivations_copy = set(etym_dict_derivations) if etym_dict_derivations and etym_dict_derivations != [""] else set()
                for lexeme in tree_root.iter_subtree():
                    lemma = lexeme.lemma
                    lemma_derivations = dictionary_normalized.get(lemma) # get derivations from etym dict for derivations in the tree in DERINET
                    if lemma_derivations != None and lemma_derivations != [""] and lemma_derivations != []:
                        lemma_derivations = set(lemma_derivations)
                        for derivation in lemma_derivations:
                            if derivation.strip() != "":
                                etym_dict_derivations_copy.add(derivation) # set add, list append!!!
                                # Now I am adding all derivations to the same list so they will be all eventualy connected to the root
                                # it would be correct to conect them to the subtree instead
                        #print(f"Derivations for {tree_root.lemma} found in subtree under {lemma}, all derivations:", etym_dict_derivations_copy)
                        #input()
                if(len(etym_dict_derivations_copy) != 0):
                    #REMOVE ALREADY PRESENT LEMMAS - NOT WORKING RIGHT NOW - Maybe it is now
                    #print(etym_dict_derivations_copy)
                    if tree_root.lemma in etym_dict_derivations_copy:
                        etym_dict_derivations_copy.remove(tree_root.lemma)
                    for lexeme in tree_root.iter_subtree():
                        lemma = lexeme.lemma
                        #print(lemma, (lemma in etym_dict_derivations_copy))
                        if lemma in etym_dict_derivations_copy:

                            etym_dict_derivations_copy.remove(lemma)
                    if(len(etym_dict_derivations_copy) != 0):
                        pass
                        #print(etym_dict_derivations_copy)
                        #input("Press enter to continue")
                if(len(etym_dict_derivations_copy) != 0):
                    #print("TREE:", tree_root.lemma)
                    new_words += len(etym_dict_derivations_copy)
                    print("Lemma:",tree_root._lemma,file=trees_and_new_derivations)
                    print("Tree:",file=trees_and_new_derivations)
                    print("\n".join(tree_root._pprint_subtree_indented("","")),file=trees_and_new_derivations) #prety print to file
                    print("Etym dict derivations all:", etym_dict_derivations,file=trees_and_new_derivations)
                    print("Etym dict derivations NOT present in derinet:",etym_dict_derivations_copy, file=trees_and_new_derivations)
                    for derivation_not_present in etym_dict_derivations_copy:
                        lexeme = lexicon.get_lexemes(lemma=derivation_not_present)
                        if len(lexeme) == 1:  # if there are not homonymous lexemes, return first (only) one
                            counter+=1
                            lexeme = lexeme[0]
                            if lexeme.get_tree_root() != lexeme:
                                pass
                                #print("!!Target lexeme isnt root!!\n Lexeme:", lexeme.lemma, ", Tree root:", lexeme.get_tree_root().lemma) # lexmes that are not roots of trees
                            #print(f"Adding derivation, source={tree_root.lemma}, target={lexeme.lemma}" )
                            #input("Press enter to continue")
                            if tree_root != lexeme:
                                if (lexeme.parent_relation is None):
                                    lexicon.add_derivation(tree_root, lexeme)
                                    print(f"Adding relation source: {tree_root}, target {lexeme} which was originaly root", file=added_derivations)
                                else:
                                    root_of_derivation_lexeme = lexeme.get_tree_root()
                                    if root_of_derivation_lexeme != tree_root:
                                        # the target lexeme already has a parent, connect the whole tree (the root of lexeme) to the tree_root
                                        # maybe connect the smaller tree to the bigger one? Or some better heuristic on how to do it? or manualy?
                                        lexicon.add_derivation(tree_root,root_of_derivation_lexeme) # add the derivation to the lexicon
                                        print(f"Adding relation source: {tree_root}, target {root_of_derivation_lexeme} which is root of tree containing {lexeme} which is derivation of {tree_root} or some of his children", file=added_derivations)
                                        # I should add the derivation edge to the node which has the lexeme as its derivation, not to the root !!!

                        elif(len(lexeme) == 0):
                            not_found_words.append(derivation_not_present)
                            lexeme_not_found_counter += 1
                            
                        else:
                            hononyms_counter += 1
                            #print("Lexeme with hononyms:",derivation_not_present)
            
        print("New words:",new_words)
        print("Added relations:", counter)
        print("Lexemes not found:", lexeme_not_found_counter)
        print("Lexemes hononyms:", hononyms_counter)
        print("Not found words", not_found_words)
                        
            

    time4 = time.time()
    print("Third section took:", time4 - time3,"s to complete")
    #sys.exit(0) # uncomment to save
    """
    Traceback (most recent call last):
    File "/Users/ampapacek/derinet/tools/data-api/derinet2/etym_update.py", line 161, in <module>
        lexicon.save(data_sink='new-derinet-2-0.tsv', fmt=dlex.Format.DERINET_V2)  # full notation of saving data
    File "/Users/ampapacek/derinet/tools/data-api/derinet2/derinet/lexicon.py", line 531, in save
        switch[fmt](data_sink)
    File "/Users/ampapacek/derinet/tools/data-api/derinet2/derinet/lexicon.py", line 610, in _save_derinet_v2
        raise Exception("An error occurred while saving data: Lexeme {} processed twice".format(lexeme))
    Exception: An error occurred while saving data: Lexeme slovanství#NNN??-----A---? processed twice

    """

    lexicon.save(data_sink=file_updated_version, fmt=dlex.Format.DERINET_V2)  # full notation of saving data
    del lexicon  # clean RAM

    time4 = time.time()
    print("Fourth section took:", time4 - time3,"s to complete")

if __name__ == "__main__":
    main()