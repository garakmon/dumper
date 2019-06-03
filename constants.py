# constants.py

import re

'''

'''



def strip_comments(text=""):
    return re.sub(r"//.*?(\r\n?|\n)|/\*.*?\*/", "", text, flags=re.DOTALL)



def evaluate_expression(expression="", known_constants=None):
    return int(eval(expression, known_constants))



def read_specials(filepath=""):

    specials = {}

    with open(filepath, "r", encoding="utf-8") as in_file:
        specials_text = in_file.read()

    g_specials = re.compile(r"gSpecials::.*gSpecialsEnd::", re.DOTALL)
    specials_text = re.search(g_specials, specials_text).group(0)
    lines = specials_text.splitlines()

    val = 0
    for line in lines:

        if "def_special" in line:
            specials[val] = line.split()[1]
            val += 1

    return specials



def read_c_constants(filepath=""):

    constants = {}

    with open(filepath, "r", encoding="utf-8") as in_file:
        constants_text = in_file.read()

    constants_text = strip_comments(constants_text)

    define_regex = re.compile(r"#define\s+(?P<define_name>[A-z0-9_]*)\s+(?P<value_expression>[A-z0-9_()+&-|<> ]*)")

    for match in re.finditer(define_regex, constants_text):

        label = match.group("define_name")
        expr  = match.group("value_expression")

        if expr and label not in constants:
            constants[label] = evaluate_expression(expr.strip(), constants)
        

    # why is this key being inserted????
    constants.pop("__builtins__")
    return constants



def reverse_dict(original_dict={}):
    return {value: key for key, value in original_dict.items()}



def read_movement_constants(filepath=""):

    with open(filepath, "r", encoding="utf-8") as in_file:
        lines = in_file.readlines()

    constants = {}

    i = 0
    for line in lines:

        if "enum_start" in line and "0x":
            i = int(line.strip().split(" ")[1], 0)

        elif "create_movement" in line:
            #print(i)
            name = line.strip().split(" ")[1]
            constants[i] = name
            i += 1

    return constants



pokefirered_constants = {}

pokefirered_constants['species'] = reverse_dict(read_c_constants("include/constants/species.h"))
pokefirered_constants['moves'] = reverse_dict(read_c_constants("include/constants/moves.h"))
pokefirered_constants['flags'] = reverse_dict(read_c_constants("include/constants/flags.h"))
pokefirered_constants['vars'] = reverse_dict(read_c_constants("include/constants/vars.h"))
pokefirered_constants['songs'] = reverse_dict(read_c_constants("include/constants/songs.h"))
pokefirered_constants['items'] = reverse_dict(read_c_constants("include/constants/items.h"))
pokefirered_constants['decor'] = reverse_dict(read_c_constants("include/constants/decorations.h"))
pokefirered_constants['maps'] = reverse_dict(read_c_constants("include/constants/map_groups.h"))
pokefirered_constants['layouts'] = reverse_dict(read_c_constants("include/constants/layouts.h"))
pokefirered_constants['specials'] = read_specials("data/specials.inc")
pokefirered_constants['movement'] = read_movement_constants("asm/macros/movement.inc")
pokefirered_constants['map_sections'] = reverse_dict(read_c_constants("include/constants/region_map.h"))

def main():

    #print(pokefirered_constants)

    pass



if __name__ == "__main__":
    main()





















