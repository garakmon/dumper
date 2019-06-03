# rom.py

import re

named_pointers = {}

def get_rom_address(data = None):
    ptr = (data[0] << 0) | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)
    return ptr & 0x1ffffff



def make_pointer(data = None, label="gUnknown"):
    # 0x1ffffff
    #ptr = (data[0] << 0) | (data[1] << 8) | (data[2] << 16) | (data[4] << 24)
    ptr = (data[0] << 0) | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)
    return label + "_8" + hex(ptr & 0x1ffffff).replace("0x", "").upper()



def get_function_ptr(data=None):
    addr = read_word(data)
    if addr == 0:
        return "0x0"
    else:
        addr -= 1
    with open("pokefirered.map", "r") as map_file:
        map_text = map_file.read()

    addr_label = "0x0{:x}".format(addr)

    regex = re.compile("\\s+{}\\s+(?P<func>[A-Za-z0-9_]*)".format(addr_label))

    match = regex.search(map_text)

    if match is not None:
        func = match.group("func")
        print("found function pointer {} in map file at 0x0{:X}".format(func, addr))

    else:
        func = "sub_{:X}".format(addr)

    return func



def make_word(data = None):
    word = (data[0] << 0) | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)
    return hex(word).upper().replace("X", "x")



def make_half(data=None):
    half = (data[0] << 0) | (data[1] << 8)
    return hex(half).replace("X", "x")



def make_byte(data=None):
    return hex(data).replace("X", "x")



def read_word(data = None):
    word = (data[0] << 0) | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)
    return word



def read_half(data=None):
    half = (data[0] << 0) | (data[1] << 8)
    return half



def read_byte(data=None):
    try: return int(data[0])
    except: return int(data)



def ptr_from_addr(address=0x0, label="gUnknown", suffix=""):
    if address == 0:
        return "NULL"

    label = label + "_8" + hex(address).replace("0x", "").upper() + suffix 
    named_pointers[address] = label

    return label

