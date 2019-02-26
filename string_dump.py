#!/usr/bin/python3
'''
python3 string_dump.py <baserom> <file>
python3 dump.py <baserom> <mode> <labels> [--] <options>
    eg. python3 dump.py baserom.gba text gSpeciesNames gMoveNames gUnknown_829572B
'''

import sys
import charmap
from mmap import ACCESS_READ, mmap

#@arg file: list of lines in a file
def process_incbin(file = []):
    offset = 0x0
    size = 0x0

    # gSpeciesNames:: @ 8245EE0
    #'.incbin "baserom.gba", 0x245EE0, 0xD05'
    for line in file:
        if ".incbin" in line:
            vals = line.strip().replace(",", "").split()
            # vals = ['.incbin', '"baserom.gba"', '0x245EE0', '0xD05']
            offset = int(vals[2], 0)
            size = int(vals[3], 0)
            yield offset, size



def to_string(data = None):
    #
    '''r_str = ""
    for byte in data:
        r_str += charmap.firered_decode[byte]

    return r_str'''
    #print(charmap.decode(data, charmap.firered_decode))
    return charmap.decode(data, charmap.firered_decode)
    #pass



def dump_strings(data = None):
    current_bytes = []
    prev_byte = 0x00

    for byte in data:

        #if byte == 0x00:
        #    continue

        if byte == 0xff and prev_byte != 0xff:
            yield to_string(current_bytes)
            current_bytes = []

        else:
            current_bytes.append(byte)

        prev_byte = byte



def main():

    contents = []

    rom = sys.argv[1]
    file = sys.argv[2]

    text = ""

    with open(file, "r") as infile:
        contents = infile.readlines()

    with open(rom, "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        #
        for o, s in process_incbin(contents):
            #data = []
            #for byte in range(size):
            #print(o, s)
            #print(baserom[o: o + s])

            # TODO: use sys.arg for type of incbin {string, etc}
            for string in dump_strings(baserom[o : o + s]):
                #print(charmap.encode(string, charmap.firered_encode))#.encode("utf-8"))
                text += "\t.string \"" + str(string).strip() + "$\"\n"

    with open("dump.txt", "w", encoding="utf-8") as dump:
        dump.write(text)



if __name__ == "__main__":
    main()
