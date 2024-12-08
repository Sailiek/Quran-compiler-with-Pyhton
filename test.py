import json
import re

# Load dictionary data
file_path = 'C:\\Users\\DELL\\Desktop\\last_skuld_dictionary.json'
with open(file_path, 'r', encoding='utf-8') as file:
    dictionary_data = json.load(file)

# Load Quran data
file_path = 'C:\\Users\\DELL\\Desktop\\new_skuld.json'
with open(file_path, 'r', encoding='utf-8') as file:
    quran_data = json.load(file)


with open("C:\\Users\\DELL\\Desktop\\test_data.txt", 'r', encoding='utf-8') as file:
    content = file.read()



with open("C:\\Users\\DELL\\Desktop\\regex_data.txt", 'r', encoding='utf-8') as file:
    regexy = file.read()



with open("C:\\Users\\DELL\\Desktop\\skuld_data.txt", 'r', encoding='utf-8') as file:
    patterns = file.read()

#plines = patterns.split('\n')

#skuld_pstring = ""

#for line in plines :
#    line = line + "\n"
#    if line not in skuld_pstring :
#        skuld_pstring += line


#output_file_path = "C:\\Users\\DELL\\Desktop\\final_skuld__operation_data.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_pstring)


with open("C:\\Users\\DELL\\Desktop\\final_skuld__operation_data.txt", 'r', encoding='utf-8') as file:
    last_move = file.read()


with open("C:\\Users\\DELL\\Desktop\\last_skuld_chance.txt", 'r', encoding='utf-8') as file:
    last_chance = file.read()

#zlines = last_chance.split('\n')

#skuld_zstring = ""

#for line in zlines :
#    if line not in skuld_zstring :
#        skuld_zstring += line + '\n'


#output_file_path = "C:\\Users\\DELL\\Desktop\\the_real_final_skuld_operation_data.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_zstring)



with open("C:\\Users\\DELL\\Desktop\\the_real_final_skuld_operation_data.txt", 'r', encoding='utf-8') as file:
    last_shot = file.read()


slines = last_shot.split('\n')

skuld_sstring =""

for line in slines :
    line = line.replace('alphabe1', 'alphabet_1')
    line = line.replace('alphabe2', 'alphabet_2')
    line = line.replace('alphabe3', 'alphabet_3')
    line = line.replace('alphabe4', 'alphabet_4')
    line = line.replace('alphabe5', 'alphabet_5')
    line = line.replace('alphabe6', 'alphabet_6')
    line = line.replace('alphabe7', 'alphabet_7')
    line = line.replace('alphabe8', 'alphabet_8')

    skuld_sstring += line + '\n'


output_file_path = "C:\\Users\\DELL\\Desktop\\the_real_final_skuld_operation_data_ever.txt"
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(skuld_sstring)







#llines = patterns.split('\n')

#skuld_lstring = ""

#for line in llines:
#    line = line.replace('t_', '')
#    skuld_lstring += line + "\n"

#output_file_path = "C:\\Users\\DELL\\Desktop\\last_skuld_chance.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_lstring)


#glines = regexy.split('\n')

#skuld_gstring = ""

#for line in glines:
#    line = line.lstrip()
    
#    line = line.replace('": "', " = r'")
#    line = line.replace('",', "'")
#    line = line.replace('"', '')
    
#    skuld_gstring += line + "\n"


with open("C:\\Users\\DELL\\Desktop\\regex.txt", 'r', encoding='utf-8') as file:
    last_regex = file.read()


#rlines = last_regex.split('\n')

#skuld_rstring = ""

#for line in rlines:
#    line = line.replace('^', '')
#    line = line.replace('$', '')

#    skuld_rstring += line + "\n"

#output_file_path = "C:\\Users\\DELL\\Desktop\\last_regex_operation.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_rstring)






#output_file_path = "C:\\Users\\DELL\\Desktop\\regex.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_gstring)


#lines = content.split('\n')

#skuld_string = ""


#for line in lines :
#    line = line.replace("|", "       |")
#    skuld_string += line+ "\n"

#output_file_path = "C:\\Users\\DELL\\Desktop\\skuld_data.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(skuld_string)








#for surah in quran_data :
#    for verse in surah['verses'] :
#        verse['translation'] = verse['translation'].replace(" -", "")


#output_file_path = "C:\\Users\\DELL\\Desktop\\new_skuld.json"

#with open(output_file_path, "w", encoding="utf-8") as file:
#    json.dump(quran_data, file, ensure_ascii=False, indent=4)


type_count = {}
my_list = []
tokens_list = []  # List to store token names
tokens_dict = {}  # Dictionary to store token names and regex patterns
added_regex = set()  # Set to track added regex patterns

# Count the occurrences of each word type
#for word, word_type in dictionary_data:
#    if word_type in type_count:
#        type_count[word_type] += 1
#    else:
#        type_count[word_type] = 1

# Create regex patterns for each type
#for word_type, count in type_count.items():
#    word_index = 1  # To track the index for each type
#    for word, current_type in dictionary_data:
#        if current_type == word_type:
#            regex_pattern = r'^' + ''.join(f"[{char.lower()}{char.upper()}]{{1}}" if char.isalpha() else char for char in word) + '$'

            # Check if the regex pattern already exists
#            if regex_pattern not in added_regex:
#                var_name = f"{word_type}_{word_index}"  # Create the token name
#                tokens_list.append(var_name)  # Add to tokens list
#                token_var = f"t_{var_name}"  # Add 't_' prefix for dictionary
#                tokens_dict[token_var] = regex_pattern  # Add token and regex to dictionary
#                added_regex.add(regex_pattern)
#                word_index += 1

# Convert the tokens list to a tuple
#tokens_tuple = tuple(tokens_list)


#output_file_path = "C:\\Users\\DELL\\Desktop\\tokens.json"

#with open(output_file_path, "w", encoding="utf-8") as file:
#    json.dump(tokens_tuple, file, ensure_ascii=False, indent=4)




#output_file_path = "C:\\Users\\DELL\\Desktop\\regex.json"

#with open(output_file_path, "w", encoding="utf-8") as file:
#    json.dump(tokens_dict, file, ensure_ascii=False, indent=4)

#print("regex done")

# Debug output: Check the tokens list (optional)
#print("Tokens Tuple:", tokens_tuple)

# Generate formatted string for verses
#my_string = '''aya : '''

#for surah in quran_data :
#    for verse in surah['verses']:
#        line = []  # Use a list to accumulate parts of the line
#        words = verse['translation'].split()
#        for word in words:
#            for token_var, regex_pattern in tokens_dict.items():
#                if re.match(regex_pattern, word):  # Check for regex match
#                    line.append(token_var)  # Append matched token
#                    break
        # Join the line and add the newline and indentation
#        if line:
#            line_str = ' '.join(line)  # Join list into a string with space separation
#            my_string += line_str + "\n" + "    | "

# Remove any extra newline or space at the end
#my_string = my_string.rstrip()

#output_file_path = "C:\\Users\\DELL\\Desktop\\test_data.txt"
#with open(output_file_path, "w", encoding="utf-8") as file:
#    file.write(my_string)

#print("Process completed. Output saved to test_data.txt.")



#for word_type, count in type_count.items():
#    word_index = 1  # To track the index for each type
#    for word, current_type in dictionary_data:
#        if current_type == word_type:
            # Create regex pattern for the word
#            regex_pattern = r'^' + ''.join(
#                f"[{char.lower()}{char.upper()}]" if char.isalpha() else char for char in word
#            ) + '$'

            # Check if the regex pattern already exists
#            if regex_pattern not in added_regex:
#                var_name = f"{word_type}_{word_index}"  # Create the token name
#                tokens_list.append(var_name)  # Add to tokens list
                
                # Dynamically create a function with the name `t_<var_name>`
#                def dynamic_token_function(t, pattern=regex_pattern):
#                    t.value = t.value.lower()  # Normalize the token value
#                    return t
                
#                token_var_name = f"t_{var_name}"  # Create variable name for the function
#                globals()[token_var_name] = dynamic_token_function  # Dynamically create the function
                
                # Optionally store the regex pattern for reference
#                tokens_dict[token_var_name] = regex_pattern
                
                # Add the pattern to the set of added regex patterns
#                added_regex.add(regex_pattern)
#                word_index += 1



output_file_path = "C:\\Users\\DELL\\Desktop\\regex_data.json"

with open(output_file_path, "w", encoding="utf-8") as file:
    json.dump(tokens_dict, file, ensure_ascii=False, indent=4)