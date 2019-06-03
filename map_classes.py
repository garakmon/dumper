'''
classes for different map objects

'''

import os
from mmap import ACCESS_READ, mmap
from rom import *
from struct import pack, unpack

#named_pointers = {}


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
class MapLayout:
    def __init__(self, name="", offset=0x0):
        self.map = name
        self.name = name # + "_Layout"
        self.offset = offset

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:

            self.width = read_word(baserom[offset: offset + 4])
            self.height = read_word(baserom[offset + 4: offset + 8])
            self.border_ptr = get_rom_address(baserom[offset + 8: offset + 12])
            self.blockdata_ptr = get_rom_address(baserom[offset + 12: offset + 16])
            self.primary_tileset_ptr = get_rom_address(baserom[offset + 16: offset + 20])
            self.secondary_tileset_ptr = get_rom_address(baserom[offset + 20: offset + 24])
            self.border_width = read_byte(baserom[offset + 24: offset + 25])
            self.border_height = read_byte(baserom[offset + 25: offset + 26])
            self.unk_half = read_half(baserom[offset + 26: offset + 28])

            #self.unk_half = 
            self.border_bytes = self.blockdata_ptr - self.border_ptr
            self.total_bytes = self.border_bytes + (2 * self.width * self.height) + 24


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

            with open(blockdata_file, "wb") as file:
                file.write(baserom[self.blockdata_ptr: self.blockdata_ptr + (self.width * self.height * 2)])

    # get printable/writable string for layout
    def to_string(self):
        string = ""
        
        string += self.name + "_Border:: @ 8{}\n".format(hex(self.border_ptr).upper().replace("0X", ""))
        string += "\t.incbin \"data/layouts/{}/border.bin\"\n\n".format(self.map)

        string += self.name + "_Blockdata:: @ 8{}\n".format(hex(self.blockdata_ptr).upper().replace("0X", ""))
        string += "\t.incbin \"data/layouts/{}/map.bin\"\n\n".format(self.map)

        string += "\t.align 2\n"
        string += self.name + ":: @ 8{}\n".format(hex(self.offset).upper().replace("0X", ""))
        string += "\t.4byte {}\n".format(self.width)
        string += "\t.4byte {}\n".format(self.height)
        string += "\t.4byte {}_Border\n".format(self.name)
        string += "\t.4byte {}_Blockdata\n".format(self.name)
        string += "\t.4byte " + ptr_from_addr(self.primary_tileset_ptr, "gTileset") + "\n"
        string += "\t.4byte " + ptr_from_addr(self.secondary_tileset_ptr, "gTileset") + "\n"
        string += "\t.byte {}\n".format(self.border_width)
        string += "\t.byte {}\n".format(self.border_height)
        string += "\t.2byte {}\n\n".format(self.unk_half)
        #string += "\t.4byte gTileset_8" + hex(self.primary_tileset_ptr) + "\n"
        #string += "\t.4byte gTileset_8" + hex(self.secondary_tileset_ptr) + "\n\n"

        return string



'''
gTileset_General:: @ 83DF704
    .byte TRUE @ is compressed
    .byte FALSE @ is secondary tileset
    .2byte 0 @ padding
    .4byte gTilesetTiles_General
    .4byte gTilesetPalettes_General
    .4byte gMetatiles_General
    .4byte gMetatileAttributes_General
    .4byte InitTilesetAnim_General
'''
class TilesetHeader:
    def __init__(self, label="", offset=0x0, size=0x0):
        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
            data = baserom[offset : offset + size]
        self.label = label
        self.is_compressed = read_byte(data[0])
        self.is_secondary = read_byte(data[1])
        self.tiles_addr = get_rom_address(data[4:8])
        self.palettes_addr = get_rom_address(data[8:12])
        self.metatiles_addr = get_rom_address(data[12:16])
        #self.metatile_attrib_addr = get_rom_address(data[16:20])
        #self.tileset_anim_func = get_function_ptr(data[20:24])
        self.tileset_anim_func = get_function_ptr(data[16:20])
        self.metatile_attrib_addr = get_rom_address(data[20:24])
        pass

    def to_string(self):
        string = self.label + "::\n"

        string += "\t.byte {} @ is compressed\n".format("TRUE" if self.is_compressed == 1 else "FALSE")
        string += "\t.byte {} @ is secondary\n".format("TRUE" if self.is_secondary == 1 else "FALSE")
        string += "\t.2byte 0 @ padding\n"
        string += "\t.4byte {}\n".format(ptr_from_addr(self.tiles_addr, "gTilesetTiles"))
        string += "\t.4byte {}\n".format(ptr_from_addr(self.palettes_addr, "gTilesetPalettes"))
        string += "\t.4byte {}\n".format(ptr_from_addr(self.metatiles_addr, "gMetatiles"))
        string += "\t.4byte {}\n".format(self.tileset_anim_func)
        string += "\t.4byte {}".format(ptr_from_addr(self.metatile_attrib_addr, "gMetatileAttributes"))

        return string



'''
TODO: rename gMapData_MapName to MapName_Layout

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

struct MapHeader
{
    /* 0x00 */ struct MapData *mapData;
    /* 0x04 */ struct MapEvents *events;
    /* 0x08 */ u8 *mapScripts;
    /* 0x0C */ struct MapConnections *connections;
    /* 0x10 */ u16 music;
    /* 0x12 */ u16 mapDataId;
    /* 0x14 */ u8 regionMapSectionId;
    /* 0x15 */ u8 cave;
    /* 0x16 */ u8 weather;
    /* 0x17 */ u8 mapType;
    /* 0x18 */ u8 filler_18;
    /* 0x19 */ u8 escapeRope;
    /* 0x1A */ u8 flags;
    /* 0x1B */ u8 battleType;
};
'''
class MapHeader:
    #def __init__(self, layout_ptr, events_ptr, scripts_ptr, connections_ptr, music):
    def __init__(self, name="", offset=0x0):
        self.address = offset
        self.name = name

        with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
            #pass
            self.layout_ptr = get_rom_address(baserom[offset: offset + 4])
            self.events_ptr = get_rom_address(baserom[offset + 4: offset + 8])
            self.scripts_ptr = get_rom_address(baserom[offset + 8: offset + 12])
            self.connections_ptr = get_rom_address(baserom[offset + 12: offset + 16])
            self.music = 0#read_word()
            self.layout = ""
            self.location = ""
            self.cave = ""
            self.weather = ""
            self.type = ""
            self.unk = ""
            self.escape_rope = ""
            self.flags = ""
            self.battle_scene = ""

        pass

    def to_string(self):
        pass



class MapConnection:
    def __init__(self):
        pass


class Tileset:
    def __init__(self, offset):
        self.address = offset
        self.ptr = "gTileset_8" + hex(offset).replace("0x", 0)

class EventObject:
    def __init__(self, address=0x0):
        self.address = 0







