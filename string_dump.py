#!/usr/bin/python3
'''
python3 string_dump.py <baserom> <file>
python3 dump.py <baserom> <mode> <labels> [--] <options>
    eg. python3 dump.py baserom.gba text gSpeciesNames gMoveNames gUnknown_829572B
'''

import sys
import os
import re
import json
import charmap
from mmap import ACCESS_READ, mmap
from collections import OrderedDict

#@arg file: list of lines in a file
def process_incbin(text=""):
    offset = 0x0
    size = 0x0

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        #layout_table_offsets = []
        #for i in range(0x17F):
        #    offs = 0x34EB8C + i * 4
        #    ptr = get_rom_address(baserom[offs : offs + 4])
        #    layout_table_offsets.append(ptr)

        for match in re.finditer(regex, text):

            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            yield label, offset, size

    # gSpeciesNames:: @ 8245EE0
    #'.incbin "baserom.gba", 0x245EE0, 0xD05'
    #for line in file:
    #    if ".incbin" in line:
    #        vals = line.strip().replace(",", "").split()
    #        # vals = ['.incbin', '"baserom.gba"', '0x245EE0', '0xD05']
    #        offset = int(vals[2], 0)
    #        size = int(vals[3], 0)
    #        yield offset, size



#@arg data: bytearray
def to_string(data = None):
    #
    '''r_str = ""
    for byte in data:
        r_str += charmap.firered_decode[byte]

    return r_str'''
    #print(charmap.decode(data, charmap.firered_decode))
    try:
        return charmap.decode(data, charmap.en_decode)
        #r_str = re.sub(r"\\[A-Za-z]", "", r_str)
        #return r_str
    except:
        return charmap.decode(data, charmap.jp_decode)
    #pass



def dump_strings(data = None):
    current_bytes = []
    prev_byte = 0x00

    bytes_consumed = 0

    num_bytes = len(data)
    for b in range(num_bytes):
        byte = data[b]
    #for byte in data:

        #print(byte)

        #if byte == 0x00:
        #    continue

        bytes_consumed += 1

        if (byte == 0xff and prev_byte != 0xff) or (b == num_bytes - 1):
            yield to_string(current_bytes), bytes_consumed
            bytes_consumed = 0
            current_bytes = []

        else:
            current_bytes.append(byte)

        prev_byte = byte



def dump_event_script_text():

    text = ""

    with open("data/text_in.inc", "r", encoding="utf-8") as infile:
        contents = infile.read()

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for label, offset, size in process_incbin(contents):

            #print("incbin {} at 0x{:X}".format(label, offset))

            #text += "\n{}:: @ 8{:X}".format(label, offset)

            # TODO: use sys.arg for type of incbin {string, etc}
            for string, bytes_consumed in dump_strings(baserom[offset : offset + size]):
                text += "\n{}:: @ 8{:X}\n".format(label, offset)
                #text += "\n"
                offset += bytes_consumed
                label = "Text_{:X}".format(offset)
                #print(charmap.encode(string, charmap.firered_encode))#.encode("utf-8"))
                text += "\t.string \"" + re.sub(r"(\\[Ppnl])", r'\1"\n\t.string "', str(string)) + "$\"\n"

    with open("data/text_dump.inc", "w", encoding="utf-8") as dump:
        dump.write(text)



def move_text_to_map_dirs():

    script_dirs = OrderedDict()

    with open("data/text_in.inc", "r", encoding="utf-8") as infile:
        contents = infile.readlines()

    regex = re.compile(r"(?P<label>[A-Za-z0-9_]+)::\s+@")

    for line in contents:

        break # disable this we are done

        match = regex.search(line)

        if match is not None:
            label = match.group("label")

            print(label)

            for map_dir in os.listdir("data/maps/"):
                script_file = "data/maps/{}/scripts.inc".format(map_dir)
                if not os.path.exists(script_file): continue
                with open(script_file, "r") as f:
                    text = f.read()
                if label in text:
                    if map_dir not in script_dirs:
                        script_dirs[map_dir] = [label]
                    else:
                        script_dirs[map_dir].append(label)
                    break

    #print(script_dirs)
    with open("data/text_dump.inc", 'w') as f:
        json.dump(script_dirs, f, indent=2, separators=(',', ': '))

    pass



def actually_move():

    with open("data/text_dump.inc", "r", encoding="utf-8") as f:
        dump_lines = f.readlines()

    regex = re.compile(r"(?P<label>[A-Za-z0-9_]+)")

    maps = []

    for line in dump_lines:
        if ":" in line:
            maps.append(regex.search(line).group("label"))

    #print(labels)
    with open("data/text_dump.inc", "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())#, strict=False)

    with open("data/text_in.inc", "r", encoding="utf-8") as f:
        lines = f.readlines()

    includes = ""

    for mapname in maps:

        #print("{}: {}".format(mapname, json_data[mapname]))

        stop = False

        text_filename = "data/maps/{}/text.inc".format(mapname)

        includes += "\n\t.include \"{}\"".format(text_filename)

        file_text = ""

        last_label = json_data[mapname][-1]

        #if json_data[mapname][0] not in lines[0]:
        #    continue

        i = 0

        for line in lines:

            if "::" in line and stop:
                break

            file_text += line

            i += 1

            if last_label in line:
                stop = True

        lines = lines[i:]

        print("{}: {} lines".format(text_filename, i))
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(file_text)

    with open("data/includes.inc", "w") as f:
        f.write(includes)

    pass



def main():

    #dump_event_script_text()
    #move_text_to_map_dirs()
    actually_move()

    pass



if __name__ == "__main__":
    main()
