#!usr/bin/python3

# dump_event_scripts.py

from script_commands import event_commands, map_commands
from constants import pokefirered_constants
from event_script_classes import *
from rom import *

import re
import sys
import glob
from mmap import ACCESS_READ, mmap



# 
# globals
# 

#dump_filename = ""

# 



# do all the stuff for stopping
def get_next_command(incbin=[], start=0x0, ismap=False):

    try:
        if ismap:
            command = map_commands[0x2]
        else:
            command = event_commands[incbin[start]]
            #command = map_commands[0x2]

    except:# KeyError:
        return event_commands[0]

    #print()

    return command #True if start < 10 else False, size



# needs more nuance
def command_ends_script(command):

    if command.get('terminating', False):
        return True



def try_create_new_script(start=0x0, size=0x0):

    # how do I decide whether this is movement?

    try:

        debug = True

        if debug:
            print("try_create_new_script({}, {})".format(start, size))

        if start in named_pointers.keys():

            label = named_pointers[start]
            named_pointers.pop(start)

            if "Movement" in label:
                return parse_movement_script("{}".format(label), start, size)

            elif "Items" in label:
                return parse_mart_items(label, start, size)

            else:
                return parse_event_script("EventScript_{:X}".format(start), start, size)

        else:
            return parse_event_script("EventScript_{:X}".format(start), start, size)

    except:
        return ""



def parse_mart_script(label="", addr=0x0, size=0x0):

    script = ""

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        incbin = baserom[addr : addr + size]

    script = "{}:: @ 8{:06X}\n".format(label, addr)

    for byte in range(int(size / 2)):
        item = read_half(incbin[2 * byte: 2 * byte + 2])

        print("Item number {}".format(item))

        script += "\t.2byte " + pokefirered_constants['items'][item] + "\n"

        if item == 0x0:
            byte += 2
            script += "\trelease\n\tend\n\n" + try_create_new_script(addr + byte + 1, size - byte)
            break


    return script[:-1]



def parse_movement_script(label="", addr=0x0, size=0x0):

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        incbin = baserom[addr : addr + size]

    script = "{}:: @ 8{:06X}\n".format(label, addr)

    for byte in range(size):
        #print(pokefirered_constants['movement'][incbin[byte]])
        mvmt = incbin[byte]

        script += "\t" + pokefirered_constants['movement'][mvmt] + "\n"

        if mvmt == 0xFE:
            # movement script ends, insert another one?
            #new_label = "Movement_"
            #if new_addr in named_pointers:
            #    #remove it
            script += "\n" + try_create_new_script(addr + byte + 1, size - byte)
            break


    return script[:-1] # remove trailing carriage return



def parse_map_script(label="", offset=0x0, size=0x0, filename=""):

    #print("PARSING MAP SCRIPT {}".format(label))

    with open(filename, "r", encoding="utf-8") as inFile:
        text = inFile.read()

    regex = re.compile(r"map_script\s+(?P<type>[0-9]+).\s+" + label)

    match = regex.search(text)

    if match is not None:
        map_script_type = int(match.group("type"), 0)

    else:
        map_script_type = 0xff

    #sys.exit("******** MAP SCRIPT TYPE {} ********".format(map_script_type))

    if map_script_type in [2, 4]:
        print("type 2 or 4 map script")

        #script = ""
        return parse_event_script(label, offset, size, True)

    else:
        return parse_event_script(label, offset, size)




def parse_event_script(label="", addr=0x0, size=0x0, ismap=False):

    #debug = False
    debug = True

    print("size: {}".format(size))

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        incbin = baserom[addr : addr + size]

    script = "{}:: @ 8{:06X}\n".format(label, addr)

    start = 0x0

    while (True):

        command = get_next_command(incbin, start, ismap)
        script += "\t{}".format(command.get('name', ""))

        if not ismap:
            start += 1

        if debug:
            print(command['name'])

        if start >= size or command is None: break

        #if (command)

        parameters = command.get('param_types', [])
        if not parameters:
            script += "\n"
            #continue
        else:
            script += " "

        pop_last_two = False

        for param in parameters:

            ###print(param)
            #print(param['name'])

            # pass the first byte to event_class constructor
            # even though it is ignored in all cases except TrainerBattleArgs
            # then call class.label(incbin[class.size_])
            if not isinstance(param, str):
                print("bad parameter: {}".format(param))

            #print("{}:: script command: {}".format(label, command['name']))
            event_class = get_event_class(param, incbin, start)

            #print("event_class.label(incbin[{}: {}])".format(start, start + event_class.size_))
            #print(incbin[start : start + event_class.size_])
            num = size - start 
            append = bytearray()
            while num < event_class.size_:
                print("there is probably something bad happening in {}".format(label))
                append.append(0xff)
                num += 1

            # handle special cases
            #if param == "TrainerBattleArgs":
            if isinstance(event_class, TrainerBattleArgs):
                print("TRAINERBATTLEPLSKILLME")
                script += event_class.label(incbin[start : start + event_class.size_])

            else: # default
                script += event_class.label(incbin[start : start + event_class.size_] + append) + ", "
                pop_last_two = True

            start += event_class.size_

        # remove the trailing comma from the script
        if parameters and pop_last_two:
            script = script[:-2] + "\n"

        if ismap:
            script += "\t.2byte 0\n"
            start += 2

        if command_ends_script(command):

            if debug:
                print(command['name'], "TERMINATES\n")

                print("start: {}, size: {}".format(start, size))

            if (start < size):
                #if addr + start not in named_pointers.keys():
                script += "\n" + try_create_new_script(addr + start, size - start)

            break

    return script



def get_final_stop():
    pass



def insert_incbins(infile="", incbins=[]):

    with open(infile, "r", encoding="utf-8") as eventScripts:
        split = eventScripts.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]+).*\s+.*(0x[0-9A-Fa-f]+)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for addr, label in incbins.items():

            if split.find(label + "::") != -1:
                continue

            matches = []
            for match in re.finditer(regex, split):
                matches.append(match)

            #for match in matches:
            for i in range(len(matches)):

                if i == len(matches) - 1: break

                match_current = matches[i]
                match_previous = matches[i - 1]
                match_next = matches[i + 1]

                label_current = match_current.group(1)
                offset_current = int(match_current.group(2), 0)
                size_current = int(match_current.group(3), 0)

                label_previous = match_previous.group(1)
                offset_previous = int(match_previous.group(2), 0)
                size_previous = int(match_previous.group(3), 0)

                label_next = match_next.group(1)
                offset_next = int(match_next.group(2), 0)
                size_next = int(match_next.group(3), 0)

                # text = re.sub(r'\"var_value\": +(\d+)', r'"var_value": "\1"', text)

                # already exists as incbin?
                if offset_current == addr: break

                elif offset_current > addr:
                    
                    old_incbin = match_previous.group(0)
                    new_incbin = label_previous + ":: @ 8{:06X}\n".format(offset_previous) # + hex(offset_previous).upper().replace("0X", "") + "\n"

                    new_size = addr - offset_previous
                    if new_size < 1: break
                    new_incbin += "\t.incbin \"baserom.gba\", 0x{:X}, 0x{:X}\n\n".format(offset_previous, new_size) #(hex(offset_previous).upper().replace("X", "x"), hex(new_size).upper().replace("X", "x"))

                    #next_incbin = ""
                    new_incbin += label + ":: @ 8{:06X}\n".format(addr) # + hex(addr).upper().replace("0X", "") + "\n"
                    next_size = offset_current - addr
                    new_incbin += "\t.incbin \"baserom.gba\", 0x{:X}, 0x{:X}".format(addr, next_size) #(hex(addr).upper().replace("X", "x"), hex(next_size).upper().replace("X", "x"))

                    split = split.replace(old_incbin, new_incbin)

                    #named_pointers.pop(addr)

                    break
    
    with open(infile, "w", encoding="utf-8") as eventScripts:
        eventScripts.write(split)



def test():

    with open("data/test_map_script.inc", "r") as eventsFile:
        events_incbin_text = eventsFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        #offset = 0x1662D1 #0x1655ED
        #size = 0x1A0 #0xC

        for match in re.finditer(regex, events_incbin_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            script = parse_event_script(label, offset, size)
            print(script)
        #script = EventScript(data=baserom[offset : offset + size])

    #script.parse()



def dump_scripts_in_file(filename=""):

    with open(filename, "r") as eventsFile:
        events_text = eventsFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, events_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            if "MapScript" in label:
                #script = parse_event_script(label, offset, size, True)
                script = parse_map_script(label, offset, size, filename)
            elif "Items" in label:
                script = parse_mart_script(label, offset, size)
            else:
                script = parse_event_script(label, offset, size)

            events_text = events_text.replace(old_incbin, script)
            print(script)

    with open("data/script_dump.inc", "w") as outFile:
        outFile.write(events_text)

    print("\n\n************ named pointers ************\n", named_pointers)
    insert_incbins("data/map_event_scripts.inc", named_pointers)

    ###for address, ptr_name in named_pointers.items():
    ###insert_incbins("data/script_dump.inc", named_pointers)

    pass



def create_script_files():

    script_file = "scripts.inc"

    for filepath in glob.iglob('data/maps/*/', recursive=True):
        print(filepath)

        filename = "{}{}".format(filepath, script_file)
        with open(filename, "w", encoding = "utf-8") as scriptFile:
            scriptFile.write("@\t.include \"{}\"\n".format(filename))

    pass



def main():

    #map_name = "SixIsland_Mart"
    dump_filename = "data/script_dump.inc" #"data/maps/{}/scripts.inc".format(map_name)
    dump_scripts_in_file(dump_filename)
    #test()
    #create_script_files()



if __name__ == "__main__":
    main()
