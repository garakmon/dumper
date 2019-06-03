'''
a map consists of the following data:
gMapName:   MapName_Layout_Border
            MapName_Layout_Blockdata
            MapName_Layout

map header: 28 bytes

'''

import sys
import os
import re
import glob

#import charmap
from mmap import ACCESS_READ, mmap
from collections import OrderedDict

#from rom import *
from map_classes import *
from map_names import *
from map_groups import pokefirered_map_list
#from script_commands import event_commands

map_constants = {}

def read_map_constants():
    for group_string, map_name in pokefirered_map_names.items():

        group, num = group_string.split('.')
        group = int(group)
        num = int(num)
        value = (num | (group << 8))
        map_constants[value] = "MAP_" + map_name.upper()



# write include/constants/map_groups.h file
def write_map_groups_file():
    with open("map_groups.h", "w") as group_file:
        text =  "#ifndef GUARD_CONSTANTS_MAP_GROUPS_H\n"
        text += "#define GUARD_CONSTANTS_MAP_GROUPS_H\n\n"

        group_num = 0
        for map_group in pokefirered_map_list:
            text += "// Map Group {}\n".format(group_num)
            map_id_num = 0
            for map_id in map_group:
                text += "#define MAP_{} ({} | ({} << 8))\n".format(map_id.upper(), map_id_num, group_num)
                map_id_num += 1
            text += "\n"
            group_num += 1

        text += "#endif // GUARD_CONSTANTS_MAP_GROUPS_H\n"
        group_file.write(text, encoding="utf-8")



'''
DewfordTown:
    .4byte DewfordTown_Layout
    .4byte DewfordTown_MapEvents
    .4byte DewfordTown_MapScripts
    .4byte DewfordTown_MapConnections
    .2byte MUS_HIGHTOWN
    .2byte LAYOUT_DEWFORD_TOWN
    .byte MAPSEC_DEWFORD_TOWN
    .byte 0
    .byte WEATHER_SUNNY
    .byte MAP_TYPE_TOWN
    .2byte 0
    map_header_flags allow_bike=1, allow_escape_rope=0, allow_run=1, show_map_name=1
    .byte MAP_BATTLE_SCENE_NORMAL
'''
layouts = set()
events = set()
scripts = set()
connections = set()
def gen_header(mapname = "MapName", data = None):
    header = mapname + ':\n'
    header += "\t.4byte " + make_pointer(data[0:4]) + "\n" # maplayout
    header += "\t.4byte " + make_pointer(data[4:8]) + "\n" # mapevents
    header += "\t.4byte " + make_pointer(data[8:12]) + "\n" # mapscripts
    header += "\t.4byte " + make_pointer(data[12:16]) + "\n" # connections
    header += "\t.2byte " + make_half(data[16:18]) + "\n" # music
    header += "\t.2byte " + make_half(data[18:20]) + "\n" # layout
    header += "\t.byte "  + make_byte(data[20]) + "\n"
    header += "\t.byte "  + make_byte(data[21]) + "\n"
    header += "\t.byte "  + make_byte(data[22]) + "\n"
    header += "\t.byte "  + make_byte(data[23]) + "\n"
    header += "\t.2byte " + make_half(data[24:26]) + "\n"
    header += "\t.byte "  + make_byte(data[26]) + "\n"
    header += "\t.byte "  + make_byte(data[27]) + "\n"

    layouts.add(make_word(data[0:4]))
    events.add(make_word(data[4:8]))
    scripts.add(make_word(data[8:12]))
    connections.add(make_word(data[12:16]))

    return header



'''
for m in re.finditer(pattern, s):
    print m.group(2), '*', m.group(1)
'''
def preview_map_headers():
    #PalletTown:: @ 8350618
    #.incbin "baserom.gba", 0x350618, 0x1C
    # \xc0\xd4-\x08PN;\x08ZT\x16\x08l'5\x08,\x01N\x00X\x00\x02\x01\x01\x06\x00\x00
    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*)")

    groups_text = ""
    headers_text = ""

    with open("./data/maps/groups.inc", "r") as groups_file:
        groups_text = groups_file.read()

    for match in re.finditer(regex, groups_text):

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
            offset = int(match.group(2), 0)
            name = match.group(1)
            headers_text += gen_header(mapname = name, data = baserom[offset: offset + 0x1c]).replace("gUnknown_0", "NULL") + "\n"

    with open("./data/maps/headers.inc", "w", encoding = "utf-8") as header_file:
        header_file.write(headers_text)

    #layouts.sort()
    print(sorted(layouts))
    #print(groups_text)



'''
PetalburgCity_Layout_Border::
    .incbin "data/layouts/PetalburgCity/border.bin"

PetalburgCity_Layout_Blockdata::
    .incbin "data/layouts/PetalburgCity/map.bin"

    .align 2
PetalburgCity_Layout::
    .4byte 30
    .4byte 30
    .4byte PetalburgCity_Layout_Border
    .4byte PetalburgCity_Layout_Blockdata
    .4byte gTileset_General
    .4byte gTileset_Petalburg

border is always 8 bytes
blockdata is width * height * 2 bytes (or width * height half words)
'''
def preview_map_layouts():
    offset = 0x2dd4c0 #0x2df308 #0x2e8338
    size = 0xF00 #0xF24

    layout_text = ""
    
    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        data = baserom[offset : offset + size]
        layout_text += "width: " + make_word(data[0 : 4]) + "\n"
        layout_text += "height: " + make_word(data[4 : 8]) + "\n"
        layout_text += make_pointer(data[8 : 12]) + "\n"
        layout_text += make_pointer(data[12 : 16]) + "\n"
        layout_text += make_pointer(data[16 : 20]) + "\n"
        layout_text += make_pointer(data[20 : 24]) + "\n"

    print(layout_text)
    return layout_text



def split_baserom(text="", addrs=[], prefix="Unknown"):
    #
    split = text
    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        
        for addr in addrs:

            matches = []
            for match in re.finditer(regex, split):
                matches.append(match)

            #for match in matches:
            for i in range(len(matches)):
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
                if offset_current == addr:
                    break

                elif offset_current > addr:
                    
                    old_incbin = match_previous.group(0)
                    new_incbin = label_previous + ":: @ 8" + hex(offset_previous).upper().replace("0X", "") + "\n"

                    new_size = addr - offset_previous
                    new_incbin += "\t.incbin \"baserom.gba\", {}, {}\n\n".format(hex(offset_previous).upper().replace("X", "x"), hex(new_size).upper().replace("X", "x"))

                    #next_incbin = ""
                    new_incbin += "gMapData_8" + hex(addr).upper().replace("0X", "") + ":: @ 8" + hex(addr).upper().replace("0X", "") + "\n"
                    next_size = offset_current - addr
                    new_incbin += "\t.incbin \"baserom.gba\", {}, {}\n".format(hex(addr).upper().replace("X", "x"), hex(next_size).upper().replace("X", "x"))

                    split = split.replace(old_incbin, new_incbin)

                    #print(hex(addr))


                    #split += new_incbin #match_current.group(0) + "\n\n"
                    #return split
                    break

    return split



'''
does the layout dump

    groups_text = ""
    headers_text = ""

    with open("./data/maps/groups.inc", "r") as groups_file:
        groups_text = groups_file.read()

    for match in re.finditer(regex, groups_text):

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
            offset = int(match.group(2), 0)
            name = match.group(1)
            headers_text += gen_header(mapname = name, data = baserom[offset: offset + 0x1c]).replace("gUnknown_0", "NULL") + "\n"

    with open("./data/maps/headers.inc", "w", encoding = "utf-8") as header_file:
        header_file.write(headers_text)

@ gLayoutsTable ?
gUnknown_834EB8C:: @ 834EB8C
    .incbin "baserom.gba", 0x34EB8C, 0x5FC
'''
def dump_map_layouts_table():

    dump_file = "data/layouts/layouts_table.inc"
    layout_file = "data/layouts/layouts.inc"

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    layout_incbin_text = ""
    layout_file_text = ""
    layout_table_text = "\t.align 2\ngMapLayouts:: @ 834EB8C\n"

    offset_to_layout_ptr = {}

    with open("./data/layouts/layouts.inc", "r") as layouts_file:
        layout_incbin_text = layouts_file.read()

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        layout_table_offsets = []
        for i in range(0x17F):
            offs = 0x34EB8C + i * 4
            ptr = get_rom_address(baserom[offs : offs + 4])
            layout_table_offsets.append(ptr)

        for match in re.finditer(regex, layout_incbin_text):

            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            offset_to_layout_ptr[offset] = label
        
        #print(offset_to_layout_ptr)
        #print(layout_table_offsets)

            #print(label, offset, size)

        unused_layouts = []
        for layout_table_entry in layout_table_offsets:

            if layout_table_entry not in offset_to_layout_ptr:
                unused_layouts.append(layout_table_entry)
            
            #print(".4byte " + offset_to_layout_ptr.get(layout_table_entry, "gMapData_8" + str(layout_table_entry)))
            layout_table_text += "\t.4byte " + offset_to_layout_ptr.get(layout_table_entry, ptr_from_addr(address=layout_table_entry, label="MapData")) + "\n"

        #print((sorted(set(unused_layouts))))
        unused_layouts = sorted(set(unused_layouts))

        unused_layouts.pop(0)
        #print(split_baserom(text=layout_incbin_text, addrs=unused_layouts, prefix="MapData"))
        #for unused_layout in unused_layouts:
        #    print(hex(unused_layout).upper())
        #    size = 

    with open(dump_file, "w") as outfile:
        outfile.write(layout_table_text)

    with open(layout_file, "w") as layoutFile:
        layoutFile.write(split_baserom(text=layout_incbin_text, addrs=unused_layouts, prefix="MapData"))



'''
PetalburgCity_Layout_Border::
    .incbin "data/layouts/PetalburgCity/border.bin"

PetalburgCity_Layout_Blockdata::
    .incbin "data/layouts/PetalburgCity/map.bin"

    .align 2
PetalburgCity_Layout::
    .4byte 30
    .4byte 30
    .4byte PetalburgCity_Layout_Border
    .4byte PetalburgCity_Layout_Blockdata
    .4byte gTileset_General
    .4byte gTileset_Petalburg

border is always 8 bytes
blockdata is width * height * 2 bytes (or width * height half words)

data = baserom[offset : offset + size]
        layout_text += "width: " + make_word(data[0 : 4]) + "\n"
        layout_text += "height: " + make_word(data[4 : 8]) + "\n"
        layout_text += make_pointer(data[8 : 12]) + "\n"
        layout_text += make_pointer(data[12 : 16]) + "\n"
        layout_text += make_pointer(data[16 : 20]) + "\n"
        layout_text += make_pointer(data[20 : 24]) + "\n"

'''
def dump_map_layouts():

    dump_file = "data/layouts/layout_dump.inc"
    dump_text = ""

    layout_incbin_text = ""
    with open("./data/layouts/layouts.inc", "r") as layouts_file:
        layout_incbin_text = layouts_file.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    tileset_header_text = ""
    primary_tileset_addrs = []
    secondary_tileset_addrs = []

    #
    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, layout_incbin_text):

            layout_text = ""

            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            data = baserom[offset : offset + size]

            primary_tileset = get_rom_address(data[16:20])
            primary_tileset_addrs.append(primary_tileset)

            secondary_tileset = get_rom_address(data[20:24])
            secondary_tileset_addrs.append(secondary_tileset)

            border = get_rom_address(data[8:12])
            blockdata = get_rom_address(data[12:16])

            #layout_text += label + "_Border::\n"
            #layout_text += "\tincbin\"baserom.gba\", {}, {}\n\n".format(border, 1)

            # FOR ME IN THE AM:::::
            # *****  use MapLayout class  ****

            # first replace duped layout names with resolved ~ add to bottom of list
            # before making the layout folders

            #layout_text += label + ":: @ 8{}\n".format(hex(offset).upper().replace("0X", ""))
            #layout_text += "\t.4byte " + str(int(make_word(data[0 : 4]), 0)) + "\n"
            #layout_text += "\t.4byte " + str(int(make_word(data[4 : 8]), 0)) + "\n"
            #layout_text += "\t.4byte " + make_pointer(data[8  : 12]) + "\n" # border
            #layout_text += "\t.4byte " + make_pointer(data[12 : 16]) + "\n" # blockdata
            #layout_text += "\t.4byte " + make_pointer(data[16 : 20], label="gTileset") + "\n" # primary tileset
            #layout_text += "\t.4byte " + make_pointer(data[20 : 24], label="gTileset") + "\n" # secondary tileset

            #dump_text += layout_text + "\n"

            layout = MapLayout(name=label, offset=offset)

            #if layout.total_bytes != size:
            #    message = "{} size is {}, but expected {}".format(label, layout.total_bytes, size)
            #    print(message)

            #if layout.border_ptr + 8 != layout.blockdata_ptr:
            #    message = "{} border is not 8 bytes ({})".format(label, layout.blockdata_ptr - layout.border_ptr)
            #    print(message)

            layout.write_data_files()
            dump_text += layout.to_string()

    all_tileset_addrs = primary_tileset_addrs + secondary_tileset_addrs
    all_tileset_addrs.remove(0)

    #for tileset in sorted(set(all_tileset_addrs)):
    #
    #    label = ptr_from_addr(tileset, label="gTileset")
    #    offset = hex(tileset).upper().replace("X", "x")
    #    size = hex(6 * 4).upper().replace("X", "x")
    #
    #    tileset_header_text += "\t.align 2\n" + label + "::\n"
    #    tileset_header_text += "\t.incbin \"baserom.gba\", {}, {}\n\n".format(offset, size)
    #    print(label, offset, size)

    #for secondary in sorted(set(secondary_tileset_addrs.remove(0))):
    #    print(secondary)

    with open(dump_file, "w") as dumpFile:
        dumpFile.write(dump_text)

    #with open("data/tilesets/headers.inc", "w") as tilesetFile:
    #    tilesetFile.write(tileset_header_text)



# writes the file data/maps.s
def write_maps_data_file():
    pass



def read_message():
    pass
    
# return text for an event (does dump text strings too?)
def read_event(event):
    evtaddr = event[0]
    mapname = event[1]

    text = "EventScript"

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        text += ""

    return text



class MapScript:
    def __init__(addr):
        self.addr = addr
        self.labels = []
        self.text = ""



#all_event_scripts_list = {}
# do a dry run of the event dump? or full run and then 
def event_dump():

    map_events_s = ""
    with open("data/map_events.s", "r") as mapEventsFile:
        map_events_s = mapEventsFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    event_dump = "\t.include \"asm/macros.inc\"\n\n"

    object_event_n_bytes = 24
    warp_def_n_bytes     = 8
    coord_event_n_bytes  = 16
    bg_event_n_bytes     = 12

    obj_event_script_list = {}
    coord_event_script_list = {}
    bg_event_script_list = {}

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, map_events_s):

            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            #print(label)

            map_name = label.replace("gMapEvents_", "") # also the map / folder name

            npc_events  = get_rom_address(baserom[offset + 4 : offset + 8])
            warp_events = get_rom_address(baserom[offset + 8 : offset + 12])
            trap_events = get_rom_address(baserom[offset + 12: offset + 16])
            sign_events = get_rom_address(baserom[offset + 16: offset + 20])

            npcs  = map_name + "_EventObjects" #ptr_from_addr(npc_events,  label=map_name, suffix="_EventObjects")
            warps = map_name + "_MapWarps" #ptr_from_addr(warp_events, label=map_name, suffix="_MapWarps")
            traps = map_name + "_MapCoordEvents" #ptr_from_addr(trap_events, label=map_name, suffix="_MapCoordEvents")
            signs = map_name + "_MapBGEvents" #ptr_from_addr(sign_events, label=map_name, suffix="_MapBGEvents")

            npc_events_count  = read_byte(baserom[offset + 0 : offset + 1])
            warp_events_count = read_byte(baserom[offset + 1 : offset + 2])
            trap_events_count = read_byte(baserom[offset + 2 : offset + 3])
            sign_events_count = read_byte(baserom[offset + 3 : offset + 4])

            #print("{} event counts: {} {} {} {}".format(label, npc_events_count, warp_events_count, trap_events_count, sign_events_count))

            if npc_events_count != 0:
                event_dump += npcs + ":\n"

            for event in range(npc_events_count):
                event_offset = npc_events + event * object_event_n_bytes
                event_script = get_rom_address(baserom[event_offset + 16: event_offset + 20])
                if event_script != 0:
                    event_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                else:
                    event_script_label = "NULL"
                if event_script not in obj_event_script_list:
                    obj_event_script_list[event_script] = [event_script_label]
                else:
                    obj_event_script_list[event_script].append(event_script_label)
                event_dump_entry = "\tobject_event {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                    read_byte(baserom[event_offset + 0 : event_offset + 1]),
                    read_half(baserom[event_offset + 1 : event_offset + 3]),
                    read_byte(baserom[event_offset + 3 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    read_byte(baserom[event_offset + 6 : event_offset + 7]),
                    read_byte(baserom[event_offset + 7 : event_offset + 8]),
                    read_byte(baserom[event_offset + 8 : event_offset + 9]),
                    read_byte(baserom[event_offset + 9 : event_offset + 10]),
                    read_byte(baserom[event_offset + 10: event_offset + 11]),
                    read_byte(baserom[event_offset + 11: event_offset + 12]),
                    read_byte(baserom[event_offset + 12: event_offset + 13]),
                    read_byte(baserom[event_offset + 13: event_offset + 14]),
                    read_byte(baserom[event_offset + 14: event_offset + 15]),
                    read_byte(baserom[event_offset + 15: event_offset + 16]),
                    event_script_label,
                    read_half(baserom[event_offset + 20: event_offset + 22]),
                    read_byte(baserom[event_offset + 22: event_offset + 23]),
                    read_byte(baserom[event_offset + 23: event_offset + 24]),
                )
                event_dump += event_dump_entry

            if warp_events_count != 0:
                event_dump += "\n" + warps + ":\n"

            for event in range(warp_events_count):
                event_offset = warp_events + event * warp_def_n_bytes
                warp_map_num = read_byte(baserom[event_offset + 6 : event_offset + 7])
                warp_map_grp = read_byte(baserom[event_offset + 7 : event_offset + 8])
                warp_map = (warp_map_num | (warp_map_grp << 8))
                event_dump += "\twarp_def {}, {}, {}, {}, {}\n".format(
                    read_half(baserom[event_offset + 0 : event_offset + 2]),
                    read_half(baserom[event_offset + 2 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    warp_map
                )

            if trap_events_count != 0:
                event_dump += "\n" + traps + ":\n"

            for event in range(trap_events_count):
                event_offset = trap_events + event * coord_event_n_bytes
                event_script = get_rom_address(baserom[event_offset + 12: event_offset + 16])
                if event_script != 0:
                    coord_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                else:
                    coord_script_label = "NULL"
                if event_script not in coord_event_script_list:
                    coord_event_script_list[event_script] = [coord_script_label]
                else:
                    coord_event_script_list[event_script].append(coord_script_label)
                event_dump += "\tcoord_event {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                    read_half(baserom[event_offset + 0 : event_offset + 2]),
                    read_half(baserom[event_offset + 2 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    read_half(baserom[event_offset + 6 : event_offset + 8]),
                    read_half(baserom[event_offset + 8 : event_offset + 10]),
                    read_half(baserom[event_offset + 10: event_offset + 12]),
                    coord_script_label
                )

            if sign_events_count != 0:
                event_dump += "\n" + signs + ":\n"

            for event in range(sign_events_count):
                event_offset = sign_events + event * bg_event_n_bytes
                kind = read_byte(baserom[event_offset + 5 : event_offset + 6])
                if kind < 5:
                    event_script = get_rom_address(baserom[event_offset + 8: event_offset + 12])
                    if event_script != 0:
                        bg_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                    else:
                        bg_script_label = "NULL"
                    if event_script not in bg_event_script_list:
                        bg_event_script_list[event_script] = [bg_script_label]
                    else:
                        bg_event_script_list[event_script].append(bg_script_label)
                    event_dump += "\tbg_event {}, {}, {}, {}, {}, {}\n".format(
                        read_half(baserom[event_offset + 0 : event_offset + 2]),
                        read_half(baserom[event_offset + 2 : event_offset + 4]),
                        read_byte(baserom[event_offset + 4 : event_offset + 5]),
                        kind,
                        read_half(baserom[event_offset + 6 : event_offset + 8]),
                        bg_script_label,
                    )
                else:
                    event_dump += "\tbg_event {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                        read_half(baserom[event_offset + 0 : event_offset + 2]),
                        read_half(baserom[event_offset + 2 : event_offset + 4]),
                        read_byte(baserom[event_offset + 4 : event_offset + 5]),
                        kind,
                        read_half(baserom[event_offset + 6 : event_offset + 8]),
                        read_half(baserom[event_offset + 8 : event_offset + 10]),
                        read_byte(baserom[event_offset + 10: event_offset + 11]),
                        read_byte(baserom[event_offset + 11: event_offset + 12]),
                    )

            event_dump += "\n{}::\n".format(label)
            event_dump += "\tmap_events {}, {}, {}, {}\n\n".format(npcs, warps, traps, signs)
    
    #with open("data/map_events_dump.s", "w") as eventOutFile:
    #    eventOutFile.write(event_dump)

    new_event_script_text = ""
    all_event_scripts_list = {**obj_event_script_list, **coord_event_script_list, **bg_event_script_list}

    for addr in sorted(all_event_scripts_list):
        for label_ in sorted(set(all_event_scripts_list[addr])):
            new_event_script_text += "{}:: @ 8{}\n".format(label_, hex(addr).upper().replace("0X",""))
        new_event_script_text += "\n"

    return all_event_scripts_list

    #with open("data/map_event_scripts_dump.inc", "w") as eventScriptFile:
    #    eventScriptFile.write(new_event_script_text)
    #print(obj_event_script_list)
    #print(coord_event_script_list)
    #print(bg_event_script_list)



def split_map_script_baseroms(write=True):
    
    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    event_scripts_text = ""
    with open("data/map_event_scripts.inc", "r") as eventScriptsFile:
        event_scripts_text = eventScriptsFile.read()
    event_scripts_text_out = "" #event_scripts_text

    map_scripts_list = event_dump()
    #map_scripts_list = {}

    # 
    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, event_scripts_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            if offset not in map_scripts_list:
                map_scripts_list[offset] = [label]
            else:
                map_scripts_list.append(label)

            trim_label = label.replace("gMapScripts_", "")

            new_incbin = "{}:: @ 8{}\n".format(label, hex(offset).upper().replace("0X", ""))
            i = 0
            while read_byte(baserom[offset + i * 5 : offset + i * 5 + 1]) != 0:
                map_script_offset = get_rom_address(baserom[offset + i * 5 + 1: offset + i * 5 + 5])
                map_script_label = "{}_MapScript{}_{}".format(trim_label, i + 1, hex(map_script_offset).upper().replace("0X", ""))
                if map_script_offset not in map_scripts_list:
                    map_scripts_list[map_script_offset] = [map_script_label]
                else:
                    map_scripts_list[map_script_offset].append(map_script_label)
                new_incbin += "\tmap_script {}, {}\n".format(
                    read_byte(baserom[offset + i * 5 : offset + i * 5 + 1]),
                    map_script_label
                )
                i += 1
                # calculate size of new incbin

            new_incbin += "\t.byte 0\n\n"

            if "gUnknown" in label:
                new_incbin = old_incbin + "\n\n"

            event_scripts_text_out += new_incbin

            # ******* TODO *******
            # make this instead a dict of {address : new_incbin string}
            # so can insert other incbins from all_scripts_list into here
            # or make a dict of like {address : (size, text)}

            #old_text = match.group(0)
            #print(label, old_text, "\n\n\n")
            # combine this with the last functions all_events_list

        if write:
            with open("data/map_event_scripts_out.inc", "w") as eventScriptsFileDump:
                eventScriptsFileDump.write(event_scripts_text_out)

    all_scripts_list = map_scripts_list#{**all_event_scripts_list, **map_scripts_list}

    new_event_script_text = ""
    for addr in sorted(all_scripts_list):
        for label_ in sorted(set(all_scripts_list[addr])):
            #print(label_)
            if "gUnknown" not in label_:
                new_event_script_text += "{}:: @ 8{}\n".format(label_, hex(addr).upper().replace("0X",""))

        if new_event_script_text != "":
            incbin_size = 4
            new_event_script_text += "\t.incbin \"baserom.gba\", {}, {}\n\n".format(
                hex(addr).upper().replace("X","x"),
                hex(incbin_size).upper().replace("X", "x")
            )

    if write:
        with open("data/map_event_scripts_dump.inc", "w") as eventScriptFile:
            eventScriptFile.write(new_event_script_text)



def calc_event_baserom_sizes():

    output_text = ""

    map_event_scripts_dump_text = ""
    with open("data/map_event_scripts_dump.inc", "r") as mapEventScriptsDumpFile:
        map_event_scripts_dump_text = mapEventScriptsDumpFile.read()

    regex = re.compile(r"([A-Za-z0-9_:\n @]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        matches = []
        for match in re.finditer(regex, map_event_scripts_dump_text):

            matches.append(match)

            #for match in matches:
        for i in range(len(matches)):
            match_current = matches[i]
            match_previous = matches[i - 1]
            match_next = matches[(i + 1) % len(matches)]

            label_current = match_current.group(1)
            offset_current = int(match_current.group(2), 0)
            size_current = int(match_current.group(3), 0)

            label_previous = match_previous.group(1)
            offset_previous = int(match_previous.group(2), 0)
            size_previous = int(match_previous.group(3), 0)

            label_next = match_next.group(1)
            offset_next = int(match_next.group(2), 0)
            size_next = int(match_next.group(3), 0)

            new_size = offset_next - offset_current

            #print(size_current)

            new_incbin = "{}:: @ 8{}\n\t.incbin \"baserom.gba\", {}, {}".format(
                label_current,
                hex(offset_current).upper().replace("0X",""),
                hex(offset_current).upper().replace("X","x"),
                hex(new_size).upper().replace("X", "x")
            )

            output_text += new_incbin

    with open("data/map_event_scripts_dump_split.inc", "w") as outFile:
        outFile.write(output_text)



def dump_map_script_pointers():

    map_event_scripts_text = ""
    with open("data/map_event_scripts.inc", "r", encoding="utf-8") as inFile:
        map_event_scripts_text = inFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+.*(0x[0-9A-Fa-f]*)")

    new_text = map_event_scripts_text #""

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, map_event_scripts_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            if "gMapScripts" in label:

                trim_label = label.replace("gMapScripts_", "")

                new_incbin = "{}:: @ 8{}\n".format(label, hex(offset).upper().replace("0X", ""))
                i = 0
                while read_byte(baserom[offset + i * 5 : offset + i * 5 + 1]) != 0:
                    map_script_offset = get_rom_address(baserom[offset + i * 5 + 1: offset + i * 5 + 5])
                    map_script_label = "{}_MapScript{}_{}".format(trim_label, i + 1, hex(map_script_offset).upper().replace("0X", ""))
                    new_incbin += "\tmap_script {}, {}\n".format(
                        read_byte(baserom[offset + i * 5 : offset + i * 5 + 1]),
                        map_script_label
                    )
                    i += 1

                new_incbin += "\t.byte 0"

                bytes_in_map_script = i * 5 + 1
                if size < bytes_in_map_script:
                    print("ERROR -- REALLY BAD!!!! @ {}: {} < {}".format(label, size, bytes_in_map_script))
                elif size > bytes_in_map_script:
                    print("Need another incbin after {}: {} > {}".format(label, size, bytes_in_map_script))
                    new_offset = offset + bytes_in_map_script
                    new_size = size - bytes_in_map_script
                    new_label = "{}_EventScript_{}".format(trim_label, hex(new_offset).upper().replace("0X", ""))
                    new_incbin += "\n\n{}:: @ 8{}\n\t.incbin \"baserom.gba\", {}, {}".format(
                        new_label,
                        hex(new_offset).upper().replace("0X",""),
                        hex(new_offset).upper().replace("X","x"),
                        hex(new_size).upper().replace("X", "x")
                    )

                if old_incbin not in new_text:
                    print("wtf", label)
                new_text = new_text.replace(old_incbin, new_incbin) #new_text += new_incbin
                #print(label, offset)

            #else:
            #    new_text += old_incbin + "\n\n"



    with open("data/map_event_scripts_dump.inc", "w", encoding="utf-8") as outFile:
        outFile.write(new_text)
    
    pass



def dump_map_event_tables():

    map_events_s = ""
    with open("data/map_events.s", "r") as mapEventsFile:
        map_events_s = mapEventsFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+(0x[0-9A-Fa-f]*)")

    event_dump = "\t.include \"asm/macros.inc\"\n\n\t.section .rodata\n\t.align 2\n\n"

    object_event_n_bytes = 24
    warp_def_n_bytes     = 8
    coord_event_n_bytes  = 16
    bg_event_n_bytes     = 12

    # 24 + 8 * 2 + 16 * 2

    obj_event_script_list = {}
    coord_event_script_list = {}
    bg_event_script_list = {}

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        for match in re.finditer(regex, map_events_s):

            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            print(label)

            map_name = label.replace("gMapEvents_", "") # also the map / folder name

            npc_events  = get_rom_address(baserom[offset + 4 : offset + 8])
            warp_events = get_rom_address(baserom[offset + 8 : offset + 12])
            trap_events = get_rom_address(baserom[offset + 12: offset + 16])
            sign_events = get_rom_address(baserom[offset + 16: offset + 20])

            npcs  = map_name + "_EventObjects" #ptr_from_addr(npc_events,  label=map_name, suffix="_EventObjects")
            warps = map_name + "_MapWarps" #ptr_from_addr(warp_events, label=map_name, suffix="_MapWarps")
            traps = map_name + "_MapCoordEvents" #ptr_from_addr(trap_events, label=map_name, suffix="_MapCoordEvents")
            signs = map_name + "_MapBGEvents" #ptr_from_addr(sign_events, label=map_name, suffix="_MapBGEvents")

            npc_events_count  = read_byte(baserom[offset + 0 : offset + 1])
            warp_events_count = read_byte(baserom[offset + 1 : offset + 2])
            trap_events_count = read_byte(baserom[offset + 2 : offset + 3])
            sign_events_count = read_byte(baserom[offset + 3 : offset + 4])

            #print("{} event counts: {} {} {} {}".format(label, npc_events_count, warp_events_count, trap_events_count, sign_events_count))

            if npc_events_count != 0:
                event_dump += npcs + ":\n"

            for event in range(npc_events_count):
                event_offset = npc_events + event * object_event_n_bytes
                event_script = get_rom_address(baserom[event_offset + 16: event_offset + 20])
                if event_script != 0:
                    event_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                else:
                    event_script_label = "0x0"
                if event_script not in obj_event_script_list:
                    obj_event_script_list[event_script] = [event_script_label]
                else:
                    obj_event_script_list[event_script].append(event_script_label)
                event_dump_entry = "\tobject_event {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                    read_byte(baserom[event_offset + 0 : event_offset + 1]),
                    read_half(baserom[event_offset + 1 : event_offset + 3]),
                    read_byte(baserom[event_offset + 3 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    read_byte(baserom[event_offset + 6 : event_offset + 7]),
                    read_byte(baserom[event_offset + 7 : event_offset + 8]),
                    read_byte(baserom[event_offset + 8 : event_offset + 9]),
                    read_byte(baserom[event_offset + 9 : event_offset + 10]),
                    read_byte(baserom[event_offset + 10: event_offset + 11]),
                    read_byte(baserom[event_offset + 11: event_offset + 12]),
                    read_byte(baserom[event_offset + 12: event_offset + 13]),
                    read_byte(baserom[event_offset + 13: event_offset + 14]),
                    read_byte(baserom[event_offset + 14: event_offset + 15]),
                    read_byte(baserom[event_offset + 15: event_offset + 16]),
                    event_script_label,
                    read_half(baserom[event_offset + 20: event_offset + 22]),
                    read_byte(baserom[event_offset + 22: event_offset + 23]),
                    read_byte(baserom[event_offset + 23: event_offset + 24]),
                )
                event_dump += event_dump_entry

            if warp_events_count != 0:
                event_dump += "\n" + warps + ":\n"

            for event in range(warp_events_count):
                event_offset = warp_events + event * warp_def_n_bytes
                warp_map_num = read_byte(baserom[event_offset + 6 : event_offset + 7])
                warp_map_grp = read_byte(baserom[event_offset + 7 : event_offset + 8])
                warp_map = (warp_map_num | (warp_map_grp << 8))
                event_dump += "\twarp_def {}, {}, {}, {}, {}\n".format(
                    read_half(baserom[event_offset + 0 : event_offset + 2]),
                    read_half(baserom[event_offset + 2 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    warp_map
                )

            if trap_events_count != 0:
                event_dump += "\n" + traps + ":\n"

            for event in range(trap_events_count):
                event_offset = trap_events + event * coord_event_n_bytes
                event_script = get_rom_address(baserom[event_offset + 12: event_offset + 16])
                if event_script != 0:
                    coord_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                else:
                    coord_script_label = "0x0"
                if event_script not in coord_event_script_list:
                    coord_event_script_list[event_script] = [coord_script_label]
                else:
                    coord_event_script_list[event_script].append(coord_script_label)
                event_dump += "\tcoord_event {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                    read_half(baserom[event_offset + 0 : event_offset + 2]),
                    read_half(baserom[event_offset + 2 : event_offset + 4]),
                    read_byte(baserom[event_offset + 4 : event_offset + 5]),
                    read_byte(baserom[event_offset + 5 : event_offset + 6]),
                    read_half(baserom[event_offset + 6 : event_offset + 8]),
                    read_half(baserom[event_offset + 8 : event_offset + 10]),
                    read_half(baserom[event_offset + 10: event_offset + 12]),
                    coord_script_label
                )

            if sign_events_count != 0:
                event_dump += "\n" + signs + ":\n"

            for event in range(sign_events_count):
                event_offset = sign_events + event * bg_event_n_bytes
                kind = read_byte(baserom[event_offset + 5 : event_offset + 6])
                if kind < 5:
                    event_script = get_rom_address(baserom[event_offset + 8: event_offset + 12])
                    if event_script != 0:
                        bg_script_label = "{}_EventScript_{}".format(map_name, hex(event_script).upper().replace("0X", ""))
                    else:
                        bg_script_label = "0x0"
                    if event_script not in bg_event_script_list:
                        bg_event_script_list[event_script] = [bg_script_label]
                    else:
                        bg_event_script_list[event_script].append(bg_script_label)
                    event_dump += "\tbg_event {}, {}, {}, {}, {}, {}\n".format(
                        read_half(baserom[event_offset + 0 : event_offset + 2]),
                        read_half(baserom[event_offset + 2 : event_offset + 4]),
                        read_byte(baserom[event_offset + 4 : event_offset + 5]),
                        kind,
                        read_half(baserom[event_offset + 6 : event_offset + 8]),
                        bg_script_label,
                    )
                else:
                    event_dump += "\tbg_event {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                        read_half(baserom[event_offset + 0 : event_offset + 2]),
                        read_half(baserom[event_offset + 2 : event_offset + 4]),
                        read_byte(baserom[event_offset + 4 : event_offset + 5]),
                        kind,
                        read_half(baserom[event_offset + 6 : event_offset + 8]),
                        read_half(baserom[event_offset + 8 : event_offset + 10]),
                        read_byte(baserom[event_offset + 10: event_offset + 11]),
                        read_byte(baserom[event_offset + 11: event_offset + 12]),
                    )

            if npc_events_count == 0:
                npcs = "0x0"
            if warp_events_count == 0:
                warps = "0x0"
            if trap_events_count == 0:
                traps = "0x0"
            if sign_events_count == 0:
                signs = "0x0"

            event_dump += "\n{}::\n".format(label)
            event_dump += "\tmap_events {}, {}, {}, {}\n\n".format(npcs, warps, traps, signs)
    
    with open("data/map_events_dump.s", "w") as eventOutFile:
        eventOutFile.write(event_dump)

    pass



def insert_pointer(text="", address=0x0, label=""):

    new_text = text

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+(0x[0-9A-Fa-f]*)")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        matches = []
        for match in re.finditer(regex, new_text):

            matches.append(match)

            #for match in matches:
        for i in range(len(matches)):
            match_current = matches[i]
            match_previous = matches[i - 1]
            match_next = matches[(i + 1) % len(matches)]

            old_incbin = match_current.group(0)

            label_current = match_current.group(1)
            offset_current = int(match_current.group(2), 0)
            size_current = int(match_current.group(3), 0)

            label_previous = match_previous.group(1)
            offset_previous = int(match_previous.group(2), 0)
            size_previous = int(match_previous.group(3), 0)

            label_next = match_next.group(1)
            offset_next = int(match_next.group(2), 0)
            size_next = int(match_next.group(3), 0)

            #new_size = offset_next - offset_current

            if offset_next > address:
                print("Insert {} after {}".format(label, label_current))
                #print(old_incbin)
                new_size = 0
                new_incbin = "{}:: @ 8{}\n\t.incbin \"baserom.gba\", {}, {}\n\n".format(
                    label_current,
                    hex(offset_current).upper().replace("0X", ""),
                    match_current.group(2),
                    hex(address - offset_current).upper().replace("X", "x")
                )
                new_incbin += "{}:: @ 8{}\n\t.incbin \"baserom.gba\", {}, {}".format(
                    label,
                    hex(address).upper().replace("0X", ""),
                    hex(address).upper().replace("X", "x"),
                    hex(offset_next - address).upper().replace("X", "x")
                )
                new_text = new_text.replace(old_incbin, new_incbin)
                break

    return new_text



def fix_undefined_references():

    undef_ref_text = ""
    with open("data/undefined_references.inc", "r", encoding="utf-8") as inFile:
        undef_ref_text = inFile.read()

    map_events_text = ""
    with open("data/map_event_scripts_fixed.inc", "r", encoding="utf-8") as inFile:
        map_events_text = inFile.read()

    regex = re.compile(r"undefined reference to `([A-Za-z_0-9]*_([A-Za-z0-9]*))'")

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        undefined_references = {}

        for match in re.finditer(regex, undef_ref_text):

            label = match.group(1)
            address = int("0x" + match.group(2), 0)

            undefined_references[address] = label

            #print("{} : {}".format(address, label))

        for addr_ in sorted(undefined_references):
            map_events_text = insert_pointer(map_events_text, addr_, undefined_references[addr_])
            #print(undefined_references[addr_])

    #print(len(undefined_references))

    with open("data/map_event_scripts_fixed.inc", "w", encoding="utf-8") as outFile:
        outFile.write(map_events_text)


    pass



def fix_map_scripts_incbin_sizes():

    # gMapScripts

    bad_text = ""
    with open("data/map_event_scripts_fixed.inc", "r", encoding="utf-8") as inFile:
        bad_text = inFile.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*).*\s+(0x[0-9A-Fa-f]*)")

    map_scripts_regex = re.compile(r"(gMapScripts_[A-Za-z0-9_]*):: @ 8([0-9A-Fa-f]*)", re.DOTALL)

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        map_scripts_dict = {}
        for match in re.finditer(map_scripts_regex, bad_text):
            label = match.group(1)
            offset = int("0x" + match.group(2), 0)
            i = 0
            while read_byte(baserom[offset + i * 5 : offset + i * 5 + 1]) != 0:
                i += 1
            bytes_in_map_script = i * 5 + 1
            map_scripts_dict[offset] = bytes_in_map_script

        #print(map_scripts_dict)

        matches = []
        for match in re.finditer(regex, bad_text):
            matches.append(match)

            #for match in matches:
        for i in range(len(matches)):

            match_current = matches[i]
            match_previous = matches[i - 1]
            match_next = matches[(i + 1) % len(matches)]

            old_incbin = match_current.group(0)

            label_current = match_current.group(1)
            offset_current = int(match_current.group(2), 0)
            size_current = int(match_current.group(3), 0)

            label_previous = match_previous.group(1)
            offset_previous = int(match_previous.group(2), 0)
            size_previous = int(match_previous.group(3), 0)

            label_next = match_next.group(1)
            offset_next = int(match_next.group(2), 0)
            size_next = int(match_next.group(3), 0)  

            offset = sorted(map_scripts_dict)[0]
            if offset_next > offset:
                map_scripts_dict.pop(offset)
                print(offset_next)

    # match current
    # match_next.group(0) contains gMapScripts

    # if match_before offset - match_next offset == match_before offset size,
    # subtract current gMapScripts nbytes from match_before

    pass



def make_map_header_dirs():

    headers_in = ""
    with open("data/maps/headers.inc", "r") as headerFileIn:
        headers_in = headerFileIn.read()

    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*\s+.*\s+.*\s+.*\s+.*\s+.*\s+.*")

    new_headers_includes = ""

    for match in re.finditer(regex, headers_in):

        text = match.group(0)
        name = match.group(1)

        header_file = "data/maps/{}/header.inc".format(name)
        os.makedirs(os.path.dirname(header_file), exist_ok=True)

        print("creating directory " + header_file.replace(".inc", ""))

        with open(header_file, "w") as headerFileOut:
            headerFileOut.write(text + "\n")

        new_headers_includes += "\t.include \"{}\"\n".format(header_file)

    with open("data/maps/headers.inc", "w") as headerFileNew:
        headerFileNew.write(new_headers_includes)



def make_map_connection_files():

    connections_in = ""
    with open("data/maps/connections.inc", "r") as connectionInFile:
        connections_in = connectionInFile.read()

    label_regex = re.compile(r"([A-z0-9_]*)::.*\s+\.4byte\s+([0-9]*)\s+\.4byte\s+([A-z0-9_]*)")
    connection_regex = re.compile(r"connection\s+([A-z]*),\s+([0-9]*),\s+([A-z0-9_]*)")

    new_connections_inc = ""

    for match in re.finditer(label_regex, connections_in):

        connection_list_label = match.group(3)

        map_dir = connection_list_label.replace("_MapConnectionsList", "")

        connection_file = "data/maps/{}/connections.inc".format(map_dir)
        os.makedirs(os.path.dirname(connection_file), exist_ok=True)

        new_connections_inc += "\t.include \"{}\"\n".format(connection_file)

        connection_text = ""

        connection_list_regex = re.compile("{}.*{}".format(connection_list_label, connection_list_label), re.DOTALL)

        for match in re.finditer(connection_list_regex, connections_in):
            connection_text += match.group(0)
            connection_text += "\n"

        with open(connection_file, "w") as connectionOutFile:
            connectionOutFile.write(connection_text)

    with open("data/maps/connections.inc", "w") as newConnectionsInc:
        newConnectionsInc.write(new_connections_inc)

    pass



def make_map_events_files():

    map_events_full = ""
    with open("data/map_events.s", "r") as mapEventsIn:
        map_events_full = mapEventsIn.read()
    
    label_regex = re.compile("([A-z0-9_]*)_MapEvents")

    new_events_inc = ""

    for match in re.finditer(label_regex, map_events_full):

        map_name = match.group(1)

        events_file = "data/maps/{}/events.inc".format(map_name)
        os.makedirs(os.path.dirname(events_file), exist_ok=True)

        map_events_text = ""

        new_file_regex = re.compile("{}*.*{}_MapEvents::\\s+[A-z0-9_ ,]*".format(map_name, map_name), re.DOTALL)

        for match_ in re.finditer(new_file_regex, map_events_full):

            map_events_text += match_.group(0) + "\n"

            map_events_full = map_events_full.replace(match_.group(0), "")

        if map_events_text:
            new_events_inc += "\t.include \"{}\"\n".format(events_file)
            with open(events_file, "w") as eventsOutFile:
                eventsOutFile.write(map_events_text)

    with open("data/maps/events.inc", "w") as newEventsInc:
        newEventsInc.write(new_events_inc)

    pass













'''
steps:

1 - read data/maps/groups.inc -> headers.inc
    A -- layout addr
        --- dump layouts
    -- map events addr
    -- map scripts addr
    -- map connections addr
2 - keep track of 



'''
def full_map_dump():
    regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.incbin\s+\"baserom.gba\", (0x[0-9A-Fa-f]*)")

    groups_text = ""
    layouts_text = ""

    layout_addrs = []
    layout_names = dict()
    map_events_addrs = []
    map_scripts_addrs = []
    map_connections_addrs = []
    tileset_addrs = []

    with open("./data/maps/groups.inc", "r") as groups_file:
        groups_text = groups_file.read()

    for match in re.finditer(regex, groups_text):

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
            offset = int(match.group(2), 0)
            name = match.group(1)

            header = MapHeader(name, offset)
            layout_addr = header.layout_ptr
            layout_addrs.append(layout_addr)
            layout_names[layout_addr] = name # TODO: generic names for reused layouts

            #layout = MapLayout(name, header.layout_ptr)
            connection_ptr = ptr_from_addr(header.connections_ptr)

            # events
            events_addr = header.scripts_ptr
            map_events_addrs.append((events_addr, name))

            #print("{} connection: {}".format(name, connection_ptr))
            #layouts_text += layout.to_string()

            #print("{} layout: {} x {}".format(name, layout.width, layout.height))


    ### -=-=-=-=-=-=-=-=-=-=-=-=-=- OUTPUT DATA -=-=-=-=-=-=-=-=-=-=-=-=-=- ###
    # TODO: make individual functions?

    ''' write to:
            data/layouts/layouts.inc
            data/layouts/layouts_table.inc
            data/MapLayoutName/layout.inc
    '''
    layout_addrs = sorted(set(layout_addrs))

    for addr in layout_addrs:
        layout = MapLayout(layout_names[addr], addr)
        #layout.write_data_files() # TODO: uncomment this
        layouts_text += layout.to_string()

        # for other things
        tileset_addrs.append(layout.primary_tileset_ptr)
        tileset_addrs.append(layout.secondary_tileset_ptr)

    with open("data/layouts/layouts.inc", "w") as layouts_file:
        layouts_file.write(layouts_text)

    layout_table_addr = layout_addrs[-1] + 28

    layout_table_text = "gMapLayouts::\n"
    num_layouts = len(layout_addrs)

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        for index in range(num_layouts + 43 + 18): # 43 unknown layouts(???), 18 NULL pointers
            start = layout_table_addr + 4 * index
            end = start + 4
            address = get_rom_address(baserom[start: end])
            layout_table_text += "\t.4byte " + layout_names.get(address, ptr_from_addr(address, "Layout")) + "_Layout\n"

    with open("data/layouts/layouts_table.inc", "w") as layouts_table_file:
        layouts_table_file.write(layout_table_text.replace("NULL_Layout", "NULL"))


    ''' write to:
            data/maps/headers.inc
    '''


    ''' write to:
            data/maps/groups.inc
    '''
    # careful not to overwrite existing -- maybe use a temp for now(or do git reset --hard; git clean -fd)


    ''' write to:
            data/event_scripts.s
    '''
    events_text = ""
    for event in map_events_addrs:
        events_text += read_event(event)

    with open("data/event_scripts.s", "w") as events_file:
        events_file.write(events_text)


    ''' write to:
            data/tilesets.s
            data/tilesets/graphics.inc
            data/tilesets/metatiles.inc
            data/tilesets/headers.inc
    '''
    tileset_addrs = sorted(set(tileset_addrs))

    #print(layout_addrs)
    #print(map_events_addrs)
    #print(map_scripts_addrs)
    #print(map_connections_addrs)

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



def dump_tileset_headers():

    with open("data/tilesets/headers.inc", "r") as headersInFile:
        headers_text = headersInFile.read()

    dump_text = ""

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\",\s+(0x[0-9A-Fa-f]*),\s+(0x[0-9A-Fa-f]*)")

        for match in re.finditer(regex, headers_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            if "Tileset" not in label: continue

            headers_text = headers_text.replace(old_incbin, TilesetHeader(label, offset, size).to_string())

            #dump_text += "incbin \"{}\" found at 0x{:X}\n".format(label, offset)
            #dump_text += TilesetHeader(label, offset, size).to_string()

    #print("************* named pointers *************", named_pointers)

    insert_incbins("data/tilesets/headers.inc", named_pointers)

    with open("data/tileset_headers_dump.inc", "w") as headersOutFile:
        headersOutFile.write(headers_text)

    pass



'''
    # write _Border and _Blockdata files
    def write_data_files(self):

        border_file = "data/layouts/{}/border.bin".format(self.map)
        os.makedirs(os.path.dirname(border_file), exist_ok=True)
        blockdata_file = "data/layouts/{}/map.bin".format(self.map)
        os.makedirs(os.path.dirname(blockdata_file), exist_ok=True)

        print("writing layout data for " + self.map)

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

            with open(border_file, "wb") as file:
                file.write(baserom[self.border_ptr: self.border_ptr + self.border_bytes])
'''
def dump_metatiles():

    with open("data/tilesets/metatiles.inc", "r") as metatilesInFile:
        metatiles_text = metatilesInFile.read()

    dump_text = ""

    tileset_data = {}
    with open("data/tilesets/headers.inc", "r") as headersInFile:
        headers_text = headersInFile.read()

    regex = re.compile(r"gTileset_(?P<name>[A-Za-z0-9]*)::\s+.*\s+.byte\s+"
                       r"(?P<secondary>[A-Z]*).*\s+.*\s+.4byte\s+"
                       r"(?P<tiles>[A-Za-z0-9_]*)\s+.4byte\s+"
                       r"(?P<palettes>[A-Za-z0-9_]*)\s+.4byte\s+"
                       r"(?P<metatiles>[A-Za-z0-9_]*)\s+.*\s+.4byte\s+"
                       r"(?P<attributes>[A-Za-z0-9_]*)")

    for match in re.finditer(regex, headers_text):

        print(match)

        ts_secondary = "secondary" if match.group("secondary") == "TRUE" else "primary"
        ts_name = match.group("name")

        ts_metatiles = match.group("metatiles")
        tileset_data[ts_metatiles] = {'name': ts_name, 'secondary': ts_secondary}

        ts_attributes = match.group("attributes")
        tileset_data[ts_attributes] = {'name': ts_name, 'secondary': ts_secondary}

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\",\s+(0x[0-9A-Fa-f]*),\s+(0x[0-9A-Fa-f]*)")

        for match in re.finditer(regex, metatiles_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            filename = "metatile_attributes" if "Attributes" in label else "metatiles"
            tileset_name = tileset_data[label]['name']
            secondary = tileset_data[label]['secondary']

            #print("")

            metatile_file = "data/tilesets/{}/{}/{}.bin".format(secondary, tileset_name, filename)
            os.makedirs(os.path.dirname(metatile_file), exist_ok=True)

            with open(metatile_file, "wb") as outFile:
                outFile.write(baserom[offset : offset + size])
            #print(metatile_file)

            new_include = "{}:: @ 8{:X}\n\t.include \"{}\"".format(label, offset, metatile_file)

            metatiles_text = metatiles_text.replace(old_incbin, new_include)

    with open("data/tileset_metatiles_dump.inc", "w") as metatilesOutFile:
        metatilesOutFile.write(metatiles_text)



def dump_tilesets():
    
    with open("data/tilesets/graphics.inc", "r") as metatilesInFile:
        tileset_gfx_text = metatilesInFile.read()

    dump_text = ""

    tileset_data = {}
    with open("data/tilesets/headers.inc", "r") as headersInFile:
        headers_text = headersInFile.read()

    regex = re.compile(r"gTileset_(?P<name>[A-Za-z0-9]*)::\s+.byte\s+"
                       r"(?P<compressed>[A-Za-z0-9_]*).*\s+.byte\s+"
                       r"(?P<secondary>[A-Z]*).*\s+.*\s+.4byte\s+"
                       r"(?P<tiles>[A-Za-z0-9_]*)\s+.4byte\s+"
                       r"(?P<palettes>[A-Za-z0-9_]*)\s+.4byte\s+"
                       r"(?P<metatiles>[A-Za-z0-9_]*)\s+.*\s+.4byte\s+"
                       r"(?P<attributes>[A-Za-z0-9_]*)")

    for match in re.finditer(regex, headers_text):

        #print(match)

        ts_secondary = "secondary" if match.group("secondary") == "TRUE" else "primary"
        ts_name = match.group("name")
        ts_compressed = ".lz" if match.group("compressed") == "TRUE" else ""

        ts_tiles = match.group("tiles")
        tileset_data[ts_tiles] = {'name': ts_name, 'secondary': ts_secondary, 'compressed': ts_compressed}

        ts_palettes = match.group("palettes")
        tileset_data[ts_palettes] = {'name': ts_name, 'secondary': ts_secondary}

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        regex = re.compile(r"([A-Za-z0-9_]*)::.*\s+.*incbin\s+\"baserom.gba\",\s+(0x[0-9A-Fa-f]*),\s+(0x[0-9A-Fa-f]*)")

        for match in re.finditer(regex, tileset_gfx_text):

            old_incbin = match.group(0)
            label = match.group(1)
            offset = int(match.group(2), 0)
            size = int(match.group(3), 0)

            if "Palette" in label:

                tileset_name = tileset_data[label]['name']
                secondary = tileset_data[label]['secondary']

                new_incbin = "{}:: @ 8{:X}\n".format(label, offset)

                for pal_num in range(16):
                    pal_offs = int(offset + 32 * pal_num)
                    pals_file = "data/tilesets/{}/{}/palettes/{}.gbapal".format(secondary, tileset_name, pal_num)
                    os.makedirs(os.path.dirname(pals_file), exist_ok=True)

                    new_incbin += "\t.incbin \"{}\"\n".format(pals_file)

                    print(pals_file)
                    with open(pals_file, "wb") as outFile:
                        outFile.write(baserom[pal_offs : pal_offs + 32])

                new_incbin = new_incbin[:-1] # remove last carriage return

            else:
                lz = tileset_data[label]['compressed']
                tileset_name = tileset_data[label]['name']
                secondary = tileset_data[label]['secondary']
                tiles_file = "data/tilesets/{}/{}/tiles.4bpp{}".format(secondary, tileset_name, lz)
                os.makedirs(os.path.dirname(tiles_file), exist_ok=True)

                print(tiles_file)
                with open(tiles_file, "wb") as outFile:
                    outFile.write(baserom[offset : offset + size])

                new_incbin = "{}:: @ 8{:X}\n\t.incbin \"{}\"".format(label, offset, tiles_file)

            tileset_gfx_text = tileset_gfx_text.replace(old_incbin, new_incbin)

    with open("data/tileset_tiles_dump.inc", "w") as tilesOutFile:
        tilesOutFile.write(tileset_gfx_text)



'''
#define GET_GBA_PAL_RED(x)   (((x) >>  0) & 0x1F)
#define GET_GBA_PAL_GREEN(x) (((x) >>  5) & 0x1F)
#define GET_GBA_PAL_BLUE(x)  (((x) >> 10) & 0x1F)

#define SET_GBA_PAL(r, g, b) (((b) << 10) | ((g) << 5) | (r))

#define UPCONVERT_BIT_DEPTH(x) (((x) * 255) / 31)

#define DOWNCONVERT_BIT_DEPTH(x) ((x) / 8)

palette->numColors = fileSize / 2;

    for (int i = 0; i < palette->numColors; i++) {
        uint16_t paletteEntry = (data[i * 2 + 1] << 8) | data[i * 2];
        palette->colors[i].red = UPCONVERT_BIT_DEPTH(GET_GBA_PAL_RED(paletteEntry));
        palette->colors[i].green = UPCONVERT_BIT_DEPTH(GET_GBA_PAL_GREEN(paletteEntry));
        palette->colors[i].blue = UPCONVERT_BIT_DEPTH(GET_GBA_PAL_BLUE(paletteEntry));
}
'''
def gbapal_to_jasc(data=[]):

    data_size = len(data)

    n_colors = int(data_size / 2)

    jasc_text = "JASC-PAL\r\n" + "0100\r\n" + "{}\r\n".format(n_colors)

    for i in range(n_colors):

        color = read_half(data[i * 2 : i * 2 + 2])

        red   = int(((color >> 0)  & 0x1f) * 255 / 31)
        green = int(((color >> 5)  & 0x1f) * 255 / 31)
        blue  = int(((color >> 10) & 0x1f) * 255 / 31)

        jasc_text += "{} {} {}\r\n".format(red, green, blue)

    return jasc_text



def dump_gbapals():

    for filepath in glob.iglob('data/tilesets/**/*.gbapal', recursive=True):

        print(filepath)

        with open(filepath, "rb") as file:
            data = file.read()

        os.remove(filepath)

        with open(filepath.replace("gbapal", "pal"), "w") as file:
            file.write(gbapal_to_jasc(data))

    pass



'''
new_incbin = "{}:: @ 8{:X}\n".format(label, offset)

                for pal_num in range(16):
                    pal_offs = int(offset + 32 * pal_num)
                    pals_file = "data/tilesets/{}/{}/palettes/{}.gbapal".format(secondary, tileset_name, pal_num)
                    os.makedirs(os.path.dirname(pals_file), exist_ok=True)

                    new_incbin += "\t.incbin \"{}\"\n".format(pals_file)

                    print(pals_file)
                    with open(pals_file, "wb") as outFile:
                        outFile.write(baserom[pal_offs : pal_offs + 32])

82D4A94 gTilesetTiles_8EA1D68 gTilesetPalettes_8EA1B68
82D4C74 gTilesetTiles_8EA99F4 gTilesetPalettes_8EA97F4
82D4E6C gTilesetTiles_8EA9F88 gTilesetPalettes_8EA9D88
82D4ECC gTilesetTiles_828FBD8 gTilesetPalettes_8290DD0
'''
def dump_weirdo_tilesets_that_are_in_the_wrong_place():

    tileset_data = {
        '82D4A94' : {
            'tiles': 'gTilesetTiles_8EA1D68',
            'palette': 'gTilesetPalettes_8EA1B68',
        },
        '82D4C74' : {
            'tiles': 'gTilesetTiles_8EA99F4',
            'palette': 'gTilesetPalettes_8EA97F4',
        },
        '82D4E6C' : {
            'tiles': 'gTilesetTiles_8EA9F88',
            'palette': 'gTilesetPalettes_8EA9D88',
        },
        #'82D4ECC' : {
        #    'tiles': 'gTilesetTiles_828FBD8',
        #    'palette': 'gTilesetPalettes_8290DD0',
        #}# this one is shared
    }

    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

        tileset_name = "82D4A94"
        tiles_label = "gTilesetTiles_8EA1D68"
        secondary = "primary"
        offset = 0x0
        size = 0x0

'''
        tileset_name = '82D4E6C'
        secondary = "secondary"
        offset = 0xEA9D88
        size = 0x200
        label = "gTilesetPalettes_8EA9D88"

        new_incbin = "\t.align 2\n{}:: @ 8{:X}\n".format(label, offset)

        for pal_num in range(16):

            pal_offs = int(offset + 32 * pal_num)
            pals_file = "data/tilesets/{}/{}/palettes/{}.gbapal".format(secondary, tileset_name, pal_num)
            os.makedirs(os.path.dirname(pals_file), exist_ok=True)

            new_incbin += "\t.incbin \"{}\"\n".format(pals_file)

            print(pals_file)
            with open(pals_file, "wb") as outFile:
                outFile.write(baserom[pal_offs : pal_offs + 32])

        with open("data/tileset_tiles_dump.inc", "w") as dumpFile:
            dumpFile.write(new_incbin)

        for filepath in glob.iglob('data/tilesets/{}/{}/palettes/*.gbapal'.format(secondary, tileset_name), recursive=True):

            print(filepath)
            with open(filepath, "rb") as file:
                data = file.read()

            os.remove(filepath)

            with open(filepath.replace("gbapal", "pal"), "w") as file:
                file.write(gbapal_to_jasc(data))
'''
    pass



'''
make the following data in order of address:
    data/tilesets.s
        .include "data/tilesets/graphics.inc"
        .include "data/tilesets/metatiles.inc"
        .include "data/tilesets/headers.inc"

    data/maps.s
        .include "data/layouts/layouts.inc"
        .include "data/layouts/layouts_table.inc"
        .include "data/maps/headers.inc"
        .include "data/maps/groups.inc"
        .include "data/maps/connections.inc"

data/maps.s (remove include groups.inc at bottom of data/data.s and add this file to linker)
@#include "constants/layouts.h"
@#include "constants/map_types.h"
#include "constants/maps.h"
@#include "constants/weather.h"
@#include "constants/region_map_sections.h"
@#include "constants/songs.h"
@#include "constants/weather.h"
    .include "asm/macros.inc"
    .include "constants/constants.inc"

    .section .rodata

@   .include "data/layouts/layouts.inc"
@   .include "data/layouts/layouts_table.inc"
@   .include "data/maps/headers.inc"
    .include "data/maps/groups.inc"
@   .include "data/maps/connections.inc"


'''
def main():
    #full_map_dump()
    #preview_map_layouts()
    #preview_map_headers()
    #dump_map_layouts()
    #event_dump()
    #split_map_script_baseroms()
    #calc_event_baserom_sizes()
    #dump_map_script_pointers()
    #dump_map_event_tables()
    #fix_undefined_references()
    #fix_map_scripts_incbin_sizes()
    #make_map_header_dirs()
    #make_map_connection_files()
    #make_map_events_files()
    #dump_tileset_headers()
    #dump_metatiles()
    #dump_tilesets()
    #dump_gbapals()
    #dump_weirdo_tilesets_that_are_in_the_wrong_place()

    pass

'''
dumping tile images

../../../../tools/gbagfx/gbagfx tiles.4bpp.lz tiles.4bpp
../../../../tools/gbagfx/gbagfx tiles.4bpp tiles.png -width 16 -palette ../../../../../Tools/dumper/ref_pal.gbapal


tilesets with tile images and/or palettes that are in data/graphics.s
82D4A94 gTilesetTiles_8EA1D68 gTilesetPalettes_8EA1B68
82D4C74 gTilesetTiles_8EA99F4 gTilesetPalettes_8EA97F4
82D4E6C gTilesetTiles_8EA9F88 gTilesetPalettes_8EA9D88
82D4ECC gTilesetTiles_828FBD8 gTilesetPalettes_8290DD0


undumped:
               
                
               
               

'''




if __name__ == '__main__':
    main()


