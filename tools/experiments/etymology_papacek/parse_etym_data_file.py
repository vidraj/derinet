
def parse_data(file_path: str) -> dict[str, dict[str, any]]:
    """
    Parses a text file containing word definitions and information from an Etymological dictionary,
    organizing the data into a nested dictionary.
    
    Each word and its associated data is extracted and stored as key-value pairs, 
    where the key is the word itself, and the value is another dictionary containing 
    specific categories as keys (like 'description', 'derivations', etc.) and their respective details as values.
    Notably, 'derivations' is stored as a list of strings.
    
    Parameters:
    - file_path (str): The path to the text file containing the word data.
    
    Returns:
    - dict[str, dict[str, any]]: A dictionary where each key is a word and each value is another dictionary 
      with keys as categories and values as the respective details for that category. 
      The value under 'derivations' is a list of strings (the derivations, may be empty).
    """
    data_dict = {}
    current_word = ""
    info_dict = {}
    HEADER_LEN = len('word:')
    with open(file_path, 'rt', encoding='utf-8') as file:
        for line in file:
            if line.startswith('word:'):
                if current_word:  # Save the previous word data
                    data_dict[current_word] = info_dict
                current_word = line[HEADER_LEN:].strip()
                info_dict = {}
            else:
                if line.strip():  # Skip empty lines
                    key, value = line.split(':', 1)
                    key, value = key.strip(), value.strip()
                    if key == 'derivations':
                        # Convert comma-separated derivations to a list of strings
                        info_dict[key] = [item.strip() for item in value.split(',')]
                    else:
                        info_dict[key] = value

        if current_word:  # Save the last word data
            data_dict[current_word] = info_dict

    return data_dict

def main():
    file_path = 'parsed_dictionary.txt'
    dictionary = parse_data(file_path)
    print(dictionary.get("adolescence").get('derivations'))

if __name__ == "__main__":
    main()
