# fireredmap2json.py

import os
import sys
import glob
import re
import json
from collections import OrderedDict

from constants import pokefirered_constants



def read_map_header(mapname=""):

    header_re = re.compile(r"(?P<map_label>[A-Za-z0-9_]*)::.*\s+"
                  r".4byte\s+(?P<layout_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<events_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<scripts_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<connections_ptr>[A-Za-z0-9_]*).*\s+"
                  r".2byte\s+(?P<bgm>[A-Za-z0-9_]*)\s+"
                  r".2byte\s+(?P<layout_id>[A-Za-z0-9_]*)\s+"
                   r".byte\s+(?P<map_section>[A-Za-z0-9_]*),\s+"
                           r"(?P<flash>[A-Za-z0-9_]*),\s+"
                           r"(?P<weather>[A-Za-z0-9_]*),\s+"
                           r"(?P<map_type>[A-Za-z0-9_]*),\s+"
                           r"(?P<unknown_18>[A-Za-z0-9_]*),\s+"
                           r"(?P<unknown_19>[A-Za-z0-9_]*),\s+"
                           r"(?P<flags>[A-Za-z0-9_]*),\s+"
                           r"(?P<battle_scene>[A-Za-z0-9_]*)")

    with open("data/maps/{}/header.inc".format(mapname), "r", encoding="utf-8") as headerInFile:
        header_text = headerInFile.read()

    header_values = OrderedDict()

    match = header_re.search(header_text)

    if match is not None:

        flag_val = int(match.group("flags"), 0)

        flags = {
            'flag_1': bool(flag_val & 1),        'flag_2': bool((flag_val >> 1) & 1),
            'flag_3': bool((flag_val >> 2) & 1), 'flag_4': bool((flag_val >> 3) & 1)
        }
        
        header_values['id'] = re.sub(r"([a-z])([A-Z])", r"\1_\2", "MAP_{}".format(mapname)).upper()
        header_values['name'] = match.group("map_label")
        header_values['layout'] = pokefirered_constants["layouts"][int(match.group("layout_id"), 0)]
        header_values['music'] = match.group("bgm")
        header_values['region_map_section'] = pokefirered_constants["map_sections"][int(match.group("map_section"), 0)]
        header_values['requires_flash'] = bool(int(match.group("flash"), 0))
        header_values['weather'] = "WEATHER_{}".format(int(match.group("weather"), 0))
        header_values['map_type'] = "MAP_TYPE_{}".format(int(match.group("map_type"), 0))
        header_values['unknown_18'] = int(match.group("unknown_18"), 0)
        header_values['unknown_19'] = int(match.group("unknown_19"), 0)
        header_values['flag_1'] = flags['flag_1']
        header_values['flag_2'] = flags['flag_2']
        header_values['flag_3'] = flags['flag_3']
        header_values['flag_4'] = flags['flag_4']
        header_values['battle_scene'] = "BATTLE_SCENE_{}".format(int(match.group("battle_scene"), 0))

    return header_values



def get_map_events_json(events_path=""):

    events_json = OrderedDict()
    events_json['object_events'] = []
    events_json['warp_events'] = []
    events_json['coord_events'] = []
    events_json['bg_events'] = []

    if not os.path.exists(events_path):
        return events_json

    with open(events_path, "r", encoding="utf-8") as eventInFile:
        lines = eventInFile.readlines()

    for line in lines:

        line = line.strip()

        event_object = OrderedDict()

        # object_event index:9, gfx_id:95, zero_1:0, x_1:26, x_2:0, y_1:32, y_2:0, elevation:3, 
        #              movement_type:8, movement_radius_xy:17, zero_2:0, trainer_type_1:0, trainer_type_2:0, 
        #              trainer_sight_or_berry_tree_id_1:0, trainer_sight_or_berry_tree_id_2:0, 
        #              script:CeruleanCity_EventScript_1BDF13, flag:19, zero_3:0, zero_4:0
        # macro index gfx 0 x y 
        if line.startswith("object_event"):

            args = re.compile(r"[, ]+").split(line)
            event_object['graphics_id'] = args[2]
            x = int(args[4], 0) | (int(args[5], 0) << 8)
            event_object['x'] = x
            y = int(args[6], 0) | (int(args[7], 0) << 8)
            event_object['y'] = y
            event_object['elevation'] = int(args[8], 0)
            event_object['movement_type'] = args[9]
            radius = int(args[10], 0)
            radius_x = radius & 0xF
            radius_y = (radius >> 4) & 0xF
            event_object['movement_range_x'] = radius_x
            event_object['movement_range_y'] = radius_y
            event_object['trainer_type'] = int(args[12], 0) | (int(args[13], 0) << 8)
            event_object['trainer_sight_or_berry_tree_id'] = int(args[14], 0) | (int(args[15], 0) << 8)
            event_object['script'] = args[16]
            event_object['flag'] = args[17]
            events_json['object_events'].append(event_object)

        elif line.startswith("warp_def"):

            args = re.compile(r"[, ]+").split(line)
            event_object['x'] = int(args[1], 0)
            event_object['y'] = int(args[2], 0)
            event_object['elevation'] = int(args[3], 0)
            event_object['dest_map'] = pokefirered_constants['maps'][int(args[5], 0)]
            event_object['dest_warp_id'] = int(args[4], 0)
            events_json['warp_events'].append(event_object)

        elif line.startswith("coord_event"):

            args = re.compile(r"[, ]+").split(line)
            event_object['type'] = "trigger"
            event_object['x'] = int(args[1], 0)
            event_object['y'] = int(args[2], 0)
            event_object['elevation'] = int(args[3], 0)
            event_object['var'] = pokefirered_constants['vars'][int(args[5], 0)]
            event_object['var_value'] = int(args[6], 0)
            event_object['script'] = args[8]
            events_json['coord_events'].append(event_object)

        elif line.startswith("bg_event"):

            args = re.compile(r"[, ]+").split(line)

            kind = int(args[4], 0)

            if kind == 7:
                event_object['type'] = "hidden_item"
                event_object['x'] = int(args[1], 0)
                event_object['y'] = int(args[2], 0)
                event_object['elevation'] = int(args[3], 0)
                event_object['item'] = pokefirered_constants['items'][int(args[6], 0)]
                event_object['flag'] = args[7]
                event_object['unknown'] = int(args[8], 0)

            else:
                event_object['type'] = "bg_event_type_{}".format(kind)
                event_object['x'] = int(args[1], 0)
                event_object['y'] = int(args[2], 0)
                event_object['elevation'] = int(args[3], 0)
                event_object['script'] = args[6]

            events_json['bg_events'].append(event_object)

    return events_json



def get_map_connections_json(connections_path=""):

    if not os.path.exists(connections_path):
        return None

    with open(connections_path, "r", encoding="utf-8") as headerInFile:
        connections_text = headerInFile.read()

    connections_json = []

    connection_regex = re.compile(r"connection\s+(?P<direction>[a-z]*),\s+(?P<offset>[\-0-9]*),\s+(?P<map>[A-Za-z0-9_]*)")

    for match in re.finditer(connection_regex, connections_text):

        connection = OrderedDict()
        connection['direction'] = match.group("direction")
        connection['offset'] = int(match.group("offset"), 0)
        connection['map'] = match.group("map")
        connections_json.append(connection)

    return connections_json



def convert_maps_to_json():

    #for filepath in glob.iglob('data/maps/*', recursive=True):
    for map_dir in os.listdir("data/maps/"):
        if not os.path.isdir("data/maps/{}".format(map_dir)): continue

        print(map_dir)

        #map_dir = "CeruleanCity"

        header_path = "data/maps/{}/header.inc".format(map_dir)
        connections_path = "data/maps/{}/connections.inc".format(map_dir)
        events_path = "data/maps/{}/events.inc".format(map_dir)

        json_data = OrderedDict()
        
        header_data = read_map_header(map_dir)
        json_data.update(header_data)

        connections_data = get_map_connections_json(connections_path)
        json_data['connections'] = connections_data

        events_data = get_map_events_json(events_path)
        json_data.update(events_data)

        with open("data/maps/{}/map.json".format(map_dir), 'w') as f:
            json.dump(json_data, f, indent=2, separators=(',', ': '))

        #break

    pass



def convert_layouts_to_json():

    regex = re.compile(r"(?P<layout_name>[A-Za-z0-9_]+)_Layout::.*\s+.4byte\s+"
                       r"(?P<width>[0-9]*)\s+.4byte\s+"
                       r"(?P<height>[0-9]*)\s+.*\s+.*\s+.4byte\s+"
                       r"(?P<primary_tileset>[A-Za-z0-9_]*)\s+.4byte\s+"
                       r"(?P<secondary_tileset>[A-Za-z0-9_]*)\s+.byte\s+"
                       r"(?P<border_width>[0-9]*)\s+.byte\s+"
                       r"(?P<border_height>[0-9]*)")

    with open("data/layouts/layouts_old.inc", "r", encoding="utf-8") as layoutsInFile:
        layouts_text = layoutsInFile.read()

    layouts = []
    layouts_table_label = "gMapLayouts"

    null_layouts = []
    i = 0

    for match in re.finditer(regex, layouts_text):

        i += 1

        if i in null_layouts:
            layouts.append({})

        print(match)

        layout = OrderedDict()
        layout['id'] = re.sub(r"([a-z])([A-Z])", r"\1_\2", "LAYOUT_{}".format(match.group("layout_name"))).upper()
        layout['name'] = match.group("layout_name") + "_Layout"
        layout['width'] = int(match.group("width"), 0)
        layout['height'] = int(match.group("height"), 0)
        layout['border_width'] = int(match.group("border_width"), 0)
        layout['border_height'] = int(match.group("border_height"), 0)
        layout['primary_tileset'] = match.group("primary_tileset")
        layout['secondary_tileset'] = match.group("secondary_tileset")
        layout['border_filepath'] = "data/layouts/{}/border.bin".format(match.group("layout_name"))
        layout['blockdata_filepath'] = "data/layouts/{}/map.bin".format(match.group("layout_name"))

        layouts.append(layout)

    layouts_data = OrderedDict([('layouts_table_label', layouts_table_label), ('layouts', layouts)])

    with open("data/layouts/layouts.json", 'w') as f:
        json.dump(layouts_data, f, indent=2, separators=(',', ': '))
    
    #return layouts_data

    pass





def write_new_layout_constants():

    layout_re = re.compile(r".4byte\s+(?P<name>[A-Za-z0-9_]+)_Layout")

    with open("data/layouts/layouts_table.inc", "r") as layoutsInFile:
        layouts_lines = layoutsInFile.readlines()

    new_layout_header = "#ifndef GUARD_CONSTANTS_LAYOUTS_H\n#define GUARD_CONSTANTS_LAYOUTS_H\n\n"

    i = 1

    for line in layouts_lines:

        match = layout_re.search(line)

        if match is not None:

            new_constant = re.sub(r"([a-z])([A-Z])", r"\1_\2", "LAYOUT_{}".format(match.group("name"))).upper()
            new_layout_header += "#define {} {}\n".format(new_constant, i)

        if "4byte" in line:
            i += 1

    new_layout_header += "\n#endif // GUARD_CONSTANTS_LAYOUTS_H\n"

    with open("include/constants/layouts.h", "w") as layoutsOutFile:
        layoutsOutFile.write(new_layout_header)

    pass


'''
    rename the constants in include/constants/map_groups.h
                            include/constants/layouts.h
'''
def fix_map_and_layout_constants():
    
    with open("include/constants/layouts.h", "r", encoding="utf-8") as layoutsInFile:
        layouts_text = layoutsInFile.read()

    for layout_folder in os.listdir("data/layouts/"):

        print(layout_folder)

        old_layout_constant = "LAYOUT_{}".format(layout_folder.replace("_Layout","").upper())
        new_layout_constant = re.sub(r"([a-z])([A-Z])", r"\1_\2", "LAYOUT_{}".format(layout_folder.replace("_Layout",""))).upper()

        if layouts_text.find(old_layout_constant) == -1 and old_layout_constant != new_layout_constant:
            print("layout constant not found: {}".format(old_layout_constant))
        layouts_text = layouts_text.replace(old_layout_constant, new_layout_constant)

        # for status updates
        #print("{} -> {}".format(old_layout_constant, new_layout_constant))

        #for script_file in glob.iglob('data/**/script*', recursive=True):

        #    with open(script_file, "r", encoding="utf-8") as file:
        #        text = file.read()

        #    text = text.replace(old_layout_constant, new_layout_constant)

        #    with open(script_file, "w", encoding="utf-8") as file:
        #        file.write(text)

    with open("include/constants/layouts.h", "w", encoding="utf-8") as layoutsOutFile:
        layoutsOutFile.write(layouts_text)

    #with open("include/constants/map_groups.h", "r", encoding="utf-8") as mapGroupsInFile:
    #    map_groups_text = mapGroupsInFile.read()

    for map_folder in os.listdir("data/maps/"):
    #for map_folder in ["MtEmber_RubyPath_1F", "FourIsland_IcefallCave_B1F", "FourIsland_IcefallCave_Back", 
    #                   "FiveIsland_RocketWarehouse", "SixIsland_DottedHole_1F", "SixIsland_DottedHole_B4F",
    #                   "SixIsland_PatternBush", "SixIsland_AlteringCave"]:

        old_map_constant = "{}".format(map_folder.upper())
        new_map_constant = re.sub(r"([a-z])([A-Z])", r"\1_\2", "{}".format(map_folder)).upper()

        #if old_map_constant == new_map_constant:
        #    continue

        #map_groups_text = map_groups_text.replace(old_map_constant, new_map_constant)

        # for status updates
        print("{} -> {}".format(old_map_constant, new_map_constant))

        new_map_constant_regex_string = ""

        for word in new_map_constant.split("_"):
            new_map_constant_regex_string += word
            if word != new_map_constant.split("_")[-1]:
                new_map_constant_regex_string += r"[_]{0,1}"

        print(new_map_constant_regex_string)

        for script_file in glob.iglob('data/**/script*', recursive=True):

            break

            with open(script_file, "r", encoding="utf-8") as file:
                text = file.read()

            text = re.sub(new_map_constant_regex_string, new_map_constant, text)

            #text = text.replace(old_map_constant, new_map_constant)

            with open(script_file, "w", encoding="utf-8") as file:
                file.write(text)

        for source_file in glob.iglob('src/**/*.*', recursive=True):

            break

            print(source_file)

            with open(source_file, "r", encoding="utf-8") as file:
                text = file.read()

            text = text.replace(old_map_constant, new_map_constant)

            with open(source_file, "w", encoding="utf-8") as file:
                file.write(text)

        for connection_file in glob.iglob('data/maps/**/connections.inc', recursive=True):

            break

            print(connection_file)

            with open(connection_file, "r", encoding="utf-8") as file:
                text = file.read()

            text = text.replace(old_map_constant, new_map_constant)

            with open(connection_file, "w", encoding="utf-8") as file:
                file.write(text)

        for json_file in glob.iglob('data/maps/**/map.json', recursive=True):

            break

            print(json_file)

            with open(json_file, "r", encoding="utf-8") as file:
                text = file.read()

            #text = text.replace(old_map_constant, new_map_constant)
            text = re.sub(new_map_constant_regex_string, new_map_constant, text)

            with open(json_file, "w", encoding="utf-8") as file:
                file.write(text)

    #with open("include/constants/map_groups.h", "w", encoding="utf-8") as mapgroupsOutFile:
    #    mapgroupsOutFile.write(map_groups_text)

    pass



'''
    fix map layout constants

    just do this when the map.json files are completed
'''
def fix_map_headers():

    print("fix_map_headers")

    for value, constant in pokefirered_constants['maps'].items():
        print("{}: {}".format(constant, value))

    #for filepath in glob.iglob('data/maps/*/headers.inc', recursive=True):
    #    print(filepath)

        #filename = "{}{}".format(filepath, script_file)
        #with open(filename, "w", encoding = "utf-8") as scriptFile:
        #    scriptFile.write("@\t.include \"{}\"\n".format(filename))

    pass



import shutil
def fix_map_layout_paths():

    for filepath in glob.iglob('data/layouts/*/', recursive=True):

        new_filepath = filepath.replace("_Layout", "")
        shutil.move(filepath, new_filepath)
        print("{} -> {}".format(filepath, new_filepath))

    pass



def print_empty_layouts():

    with open("data/layouts/layouts_table.inc", "r") as layoutsFile:
        layouts_text = layoutsFile.read()

    regex = re.compile(r"4byte\s+([A-Za-z0-9_]+)")

    i = 1
    for match in re.finditer(regex, layouts_text):

        if match.group(1) == "NULL":
            print(i)

        i += 1

    pass



def find_shared_events_maps():

    for map_dir in os.listdir("data/maps/"):
        if not os.path.exists("data/maps/{}/header.inc".format(map_dir)): continue

        with open("data/maps/{}/header.inc".format(map_dir), "r") as headerFile:
            headers_text = headerFile.read()

        events_label_regex = re.compile(r"([A-Za-z0-9_]+)_MapEvents")
        events_label = events_label_regex.search(headers_text).group(1)

        if events_label != map_dir:
            print("{} shares map events with {}".format(map_dir, events_label))

        scripts_label_regex = re.compile(r"([A-Za-z0-9_]+)_MapScripts")
        scripts_label = scripts_label_regex.search(headers_text).group(1)

        if scripts_label != map_dir:
            print("{} shares map scripts with {}".format(map_dir, scripts_label))

        #print(events_label)

    pass



def create_map_groups_json():

    with open("data/maps/groups.inc", "r") as groupsInFile:
        groups_asm = groupsInFile.readlines()

    groups_data = OrderedDict()

    map_groups = OrderedDict()

    group_label_regex = re.compile(r"([A-Za-z0-9_]+)::")
    map_name_regex = re.compile(r"4byte\s+([A-Za-z0-9_]+)")

    group_name = ""

    for line in groups_asm:

        if re.compile(r"gMapGroup[0-9]+::").search(line) is not None:

            group_name = group_label_regex.search(line).group(1)

            map_groups[group_name] = []

        elif "4byte" in line and "gMapGroup" not in line:

            map_groups[group_name].append(map_name_regex.search(line).group(1))

    with open("data/maps/connections.inc", "r") as connectionsInFile:
        connections_lines = connectionsInFile.readlines()

    connections = []
    for line in connections_lines:

        match = re.compile(r"data/maps/([A-Za-z0-9_]+)/connections\.inc").search(line)
        if match is not None:
            connections.append(match.group(1))

    map_groups_data = OrderedDict()

    map_groups_data["group_order"] = list(map_groups.keys())
    map_groups_data.update(map_groups)
    map_groups_data["connections_include_order"] = connections

    with open("data/maps/map_groups.json", 'w') as f:
        json.dump(map_groups_data, f, indent=2, separators=(',', ': '))

            #print(group_name)

            #map_groups()
    pass



def fix_map_header_flags_field():

    header_re = re.compile(r"(?P<map_label>[A-Za-z0-9_]*)::.*\s+"
                  r".4byte\s+(?P<layout_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<events_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<scripts_ptr>[A-Za-z0-9_]*).*\s+"
                  r".4byte\s+(?P<connections_ptr>[A-Za-z0-9_]*).*\s+"
                  r".2byte\s+(?P<bgm>[A-Za-z0-9_]*)\s+"
                  r".2byte\s+(?P<layout_id>[A-Za-z0-9_]*)\s+"
                   r".byte\s+(?P<map_section>[A-Za-z0-9_]*),\s+"
                           r"(?P<flash>[A-Za-z0-9_]*),\s+"
                           r"(?P<weather>[A-Za-z0-9_]*),\s+"
                           r"(?P<map_type>[A-Za-z0-9_]*),\s+"
                           r"(?P<unknown_18>[A-Za-z0-9_]*),\s+"
                           r"(?P<unknown_19>[A-Za-z0-9_]*),\s+"
                           r"(?P<flags>[A-Za-z0-9_]*),\s+"
                           r"(?P<battle_scene>[A-Za-z0-9_]*)")

    with open("../Tools/dumper/map_headers.txt", "r") as headersInFile:
        headers_text = headersInFile.read()

    flag_vals = {
        255: -1,
        254: -2,
        253: -3,
        252: -4,
        1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 127:127
    }

    better_flags = {}

    for match in re.finditer(header_re, headers_text):

        map_name = match.group("map_label")
        map_flags = int(match.group("flags"), 0)

        if map_flags != 0:
            #print("{} flags value is {:08b}".format(map_name, map_flags))
            better_flags[map_name] = flag_vals[map_flags]

    for json_file in glob.iglob('data/maps/**/map.json', recursive=True):

        print(json_file)

        new_json_object = OrderedDict()

        with open(json_file, "r", encoding="utf-8") as file:
            text = file.read()

        old_json_object = json.loads(text)

        #if old_json_object['name'] in better_flags.keys():
        #    new_flag = better_flags[old_json_object['name']]
        #else:
        #    new_flag = 0

        new_flag = better_flags.get(old_json_object['name'], 0)

        new_json_object['id'] = old_json_object['id']
        new_json_object['name'] = old_json_object['name']
        new_json_object['layout'] = old_json_object['layout']
        new_json_object['music'] = old_json_object['music']
        new_json_object['region_map_section'] = old_json_object['region_map_section']
        new_json_object['requires_flash'] = old_json_object['requires_flash']
        new_json_object['weather'] = old_json_object['weather']
        new_json_object['map_type'] = old_json_object['map_type']
        new_json_object['unknown_18'] = old_json_object['unknown_18']
        new_json_object['unknown_19'] = old_json_object['unknown_19']
        new_json_object['elevator_flag'] = new_flag
        new_json_object['battle_scene'] = old_json_object['battle_scene']

        #new_json_object['connections'] = connections_data.get(, None)

        new_json_object['object_events'] = old_json_object['object_events']
        new_json_object['warp_events'] = old_json_object['warp_events']
        new_json_object['coord_events'] = old_json_object['coord_events']
        new_json_object['bg_events'] = old_json_object['bg_events']

        #new_json_object[]

        #text = text.replace(old_map_constant, new_map_constant)
        #text = re.sub(new_map_constant_regex_string, new_map_constant, text)

        with open(json_file, 'w') as f:
            json.dump(new_json_object, f, indent=2, separators=(',', ': '))

        #with open(json_file, "w", encoding="utf-8") as file:
            #old_json_object = json.loads(text)
            #file.write(text)

        # json.loads(string, object_pairs_hook=OrderedDict)

        break



    pass



def reorder_keys(objects_list, key_order):

    new_json_object = []#OrderedDict()

    for obj in objects_list:
        new_object = OrderedDict()
        for key in key_order:
            if obj.get(key) is not None:
                new_object[key] = obj[key]
        new_json_object.append(new_object)

    return new_json_object
    #pass



def fix_map_connections_field():

    object_event_key_order = [
        'graphics_id', 'x', 'y', 'elevation', 'movement_range_x', 'movement_range_y', 'trainer_type',
        'trainer_sight_or_berry_tree_id', 'script', 'flag'
    ]

    warp_event_key_order = [
        'x', 'y', 'elevation', 'dest_map', 'dest_warp_id'
    ]

    coord_event_key_order = [
        'type', 'x', 'y', 'elevation', 'var', 'var_value', 'script'
    ]

    bg_event_include_order = [
        'type', 'x', 'y', 'elevation', 'item', 'flag', 'unknown', 'script'
    ]

    #bg_event_include_order = [
    #    'type', 'x', 'y', 'elevation', 'script'
    #]

    for json_file in glob.iglob('data/maps/**/map.json', recursive=True):

        print(json_file)

        new_json_object = OrderedDict()

        with open(json_file, "r", encoding="utf-8") as file:
            text = file.read()

        old_json_object = json.loads(text)

        map_name = old_json_object['name']

        dumper_connections_path = "../Tools/dumper/maps/{}/connections.inc".format(map_name)
        connection_json = get_map_connections_json(dumper_connections_path)

        if connection_json is not None:
            #for connection in connection_json.items():
            print(connection_json)
        else:
            print("no connections found")

        new_json_object['id'] = old_json_object['id']
        new_json_object['name'] = map_name
        new_json_object['layout'] = old_json_object['layout']
        new_json_object['music'] = old_json_object['music']
        new_json_object['region_map_section'] = old_json_object['region_map_section']
        new_json_object['requires_flash'] = old_json_object['requires_flash']
        new_json_object['weather'] = old_json_object['weather']
        new_json_object['map_type'] = old_json_object['map_type']
        new_json_object['unknown_18'] = old_json_object['unknown_18']
        new_json_object['unknown_19'] = old_json_object['unknown_19']
        new_json_object['elevator_flag'] = old_json_object['elevator_flag']
        new_json_object['battle_scene'] = old_json_object['battle_scene']

        new_json_object['connections'] = connection_json#connections_data.get(map_name, None)

        new_json_object['object_events'] = reorder_keys(old_json_object['object_events'], object_event_key_order)
        new_json_object['warp_events'] = reorder_keys(old_json_object['warp_events'], warp_event_key_order)
        new_json_object['coord_events'] = reorder_keys(old_json_object['coord_events'], coord_event_key_order)

        new_json_object['bg_events'] = reorder_keys(old_json_object['bg_events'], bg_event_include_order)

        # don't dump it yet
        with open(json_file, 'w') as f:
            json.dump(new_json_object, f, indent=2, separators=(',', ': '))

        #break

    pass



def new_object_event(events_path=""):

    events_json = []

    if not os.path.exists(events_path):
        return events_json

    with open(events_path, "r", encoding="utf-8") as eventInFile:
        lines = eventInFile.readlines()

    for line in lines:

        line = line.strip()

        event_object = OrderedDict()

        # object_event index:9, gfx_id:95, zero_1:0, x_1:26, x_2:0, y_1:32, y_2:0, elevation:3, 
        #              movement_type:8, movement_radius_xy:17, zero_2:0, trainer_type_1:0, trainer_type_2:0, 
        #              trainer_sight_or_berry_tree_id_1:0, trainer_sight_or_berry_tree_id_2:0, 
        #              script:CeruleanCity_EventScript_1BDF13, flag:19, zero_3:0, zero_4:0
        # macro index gfx 0 x y 
        if line.startswith("object_event"):

            args = re.compile(r"[, ]+").split(line)
            event_object['graphics_id'] = args[2]
            x = int(args[4], 0) | (int(args[5], 0) << 8)
            event_object['x'] = x
            y = int(args[6], 0) | (int(args[7], 0) << 8)
            event_object['y'] = y
            event_object['elevation'] = int(args[8], 0)
            event_object['movement_type'] = args[9]
            radius = int(args[10], 0)
            radius_x = radius & 0xF
            radius_y = (radius >> 4) & 0xF
            event_object['movement_range_x'] = radius_x
            event_object['movement_range_y'] = radius_y
            event_object['trainer_type'] = int(args[12], 0) | (int(args[13], 0) << 8)
            event_object['trainer_sight_or_berry_tree_id'] = int(args[14], 0) | (int(args[15], 0) << 8)
            event_object['script'] = args[16]
            event_object['flag'] = args[17]
            events_json.append(event_object)

    return events_json




# new_object_event
def fix_object_events():

    object_event_key_order = [
        'graphics_id', 'x', 'y', 'elevation', 'movement_range_x', 'movement_range_y', 'trainer_type',
        'trainer_sight_or_berry_tree_id', 'script', 'flag'
    ]

    warp_event_key_order = [
        'x', 'y', 'elevation', 'dest_map', 'dest_warp_id'
    ]

    coord_event_key_order = [
        'type', 'x', 'y', 'elevation', 'var', 'var_value', 'script'
    ]

    bg_event_include_order = [
        'type', 'x', 'y', 'elevation', 'item', 'flag', 'unknown', 'script'
    ]

    #bg_event_include_order = [
    #    'type', 'x', 'y', 'elevation', 'script'
    #]

    for json_file in glob.iglob('data/maps/**/map.json', recursive=True):

        print(json_file)

        new_json_object = OrderedDict()

        with open(json_file, "r", encoding="utf-8") as file:
            text = file.read()

        old_json_object = json.loads(text)

        map_name = old_json_object['name']

        dumper_events_path = "../Tools/dumper/maps/{}/events.inc".format(map_name)

        new_json_object['id'] = old_json_object['id']
        new_json_object['name'] = map_name
        new_json_object['layout'] = old_json_object['layout']
        new_json_object['music'] = old_json_object['music']
        new_json_object['region_map_section'] = old_json_object['region_map_section']
        new_json_object['requires_flash'] = old_json_object['requires_flash']
        new_json_object['weather'] = old_json_object['weather']
        new_json_object['map_type'] = old_json_object['map_type']
        new_json_object['unknown_18'] = old_json_object['unknown_18']
        new_json_object['unknown_19'] = old_json_object['unknown_19']
        new_json_object['elevator_flag'] = old_json_object['elevator_flag']
        new_json_object['battle_scene'] = old_json_object['battle_scene']

        new_json_object['connections'] = old_json_object['connections']

        new_json_object['object_events'] = new_object_event(dumper_events_path)

        new_json_object['warp_events'] = reorder_keys(old_json_object['warp_events'], warp_event_key_order)
        new_json_object['coord_events'] = reorder_keys(old_json_object['coord_events'], coord_event_key_order)
        new_json_object['bg_events'] = reorder_keys(old_json_object['bg_events'], bg_event_include_order)

        # don't dump it yet
        with open(json_file, 'w') as f:
            json.dump(new_json_object, f, indent=2, separators=(',', ': '))

        #break

    pass



'''
"null_layouts": [
    22, 23, 29, 38, 39, 40, 41, 42, 43, 44, 45, 56, 58, 59, 60, 61, 76, 175
  ]

name weather constants
'''
def main():

    #write_new_layout_constants()
    #fix_map_and_layout_constants()
    #fix_map_headers()
    #convert_layouts_to_json()
    #fix_map_layout_paths()
    #print_empty_layouts()
    #find_shared_events_maps()
    #create_map_groups_json()

    #fix_map_and_layout_constants()
    #fix_map_header_flags_field()
    #fix_map_connections_field()

    #fix_object_events()

    #convert_maps_to_json()

    pass



if __name__ == "__main__":
    main()
