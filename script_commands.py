#

import sys

from rom import *
from event_script_classes import *

from mmap import ACCESS_READ, mmap



'''
an event script gets passes in the data (all data from baserom incbin)
'''
class EventScript():

    def __init__(self, label="", data=[], addr=0x0):
        self.starting_address = addr
        self.data = data
        self.pos_ = 0
        self.commands = []

        pass


    def get_next_command(self):
        try:
            self.cmd_ = self.data[self.pos_]
            self.pos_ += 1
        except IndexError:
            print("Error retrieving command at 0x{:X}".format(self.pos_))
            self.cmd_ = 0x0
            self.pos_ += 1
        return self.cmd_


    def incbin_remaining():
        pass


    def get_command_text(self, command):

        text = ""

        print(command)

        text += "\t" + command['name']

        parameters = command.get('param_types', [])

        if parameters is None:
            text += "\n"
            return text

        else:
            text += " "

        for param in parameters:

            ###print(param)

            # pass the first byte to event_class constructor
            # even though it is ignored in all cases except TrainerBattleArgs
            # then call class.label(data[class.size_])
            event_class = getattr(sys.modules[__name__], param)(self.data[self.pos_ + 1])

            #print(event_class.label(self.data[self.pos_ : self.pos_ + event_class.size_]))

            # TODO: no print extra comma
            text += event_class.label(self.data[self.pos_ : self.pos_ + event_class.size_]) + ", "


            self.pos_ += event_class.size_

        text += "\n"

        return text



    def parse(self):

        text = ""

        # get next command, 
        # if terminating is true, there is much work to be done to find the end of the script.
        # 
        while not event_commands[self.get_next_command()].get('terminating', False):

            command = event_commands[self.cmd_]
            #print(command['name'])

            text += self.get_command_text(command)

        # we ran into a terminating command, so resolve the end of the script
        terminating_command = event_commands[self.cmd_]#['name']
        text += self.get_command_text(terminating_command)


        print("text: ", text)

        pass


    def to_string(self):
        pass


    def print_remaining_incbin(self):
        pass



event_commands = {
    0x00: {
        'name': 'nop',
        'param_names': [],
        'param_types': [],
    },
    0x01: {
        'name': 'nop1',
        'param_names': [],
        'param_types': [],
    },
    0x02: {
        'name': 'end',
        'param_names': [],
        'param_types': [],
        'terminating': True,
    },
    0x03: {
        'name': 'return',
        'param_names': [],
        'param_types': [],
        'terminating': True,
    },
    0x04: {
        'name': 'call',
        'param_names': ['destination'],
        'param_types': ['EventScriptPointer'],
    },
    0x05: {
        'name': 'goto',
        'param_names': ['destination'],
        'param_types': ['EventScriptPointer'],
        'terminating': True,
    },
    0x06: {
        'name': 'goto_if',
        'param_names': ['condition', 'destination'],
        'param_types': ['Byte', 'EventScriptPointer'],
    },
    0x07: {
        'name': 'call_if',
        'param_names': ['condition', 'destination'],
        'param_types': ['Byte', 'EventScriptPointer'],
    },
    0x08: {
        'name': 'gotostd',
        'param_names': ['function'],
        'param_types': ['Byte'],
        'terminating': True,
    },
    0x09: {
        'name': 'callstd',
        'param_names': ['function'],
        'param_types': ['Byte'],
    },
    0x0a: {
        'name': 'gotostd_if',
        'param_names': ['condition', 'function'],
        'param_types': ['Byte', 'Byte'],
    },
    0x0b: {
        'name': 'callstd_if',
        'param_names': ['condition', 'function'],
        'param_types': ['Byte', 'Byte'],
    },
    0x0c: {
        'name': 'gotoram',
        'param_names': [],
        'param_types': [],
        'terminating': True,
    },
    0x0d: {
        'name': 'killscript',
        'param_names': [],
        'param_types': [],
        'terminating': True,
    },
    0x0e: {
        'name': 'setmysteryeventstatus',
        'param_names': ['value'],
        'param_types': ['Byte'],
    },
    0x0f: {
        'name': 'loadword',
        'param_names': ['destination', 'value'],
        'param_types': ['Byte', 'Pointer'],
    },
    0x10: {
        'name': 'loadbyte',
        'param_names': ['destination', 'value'],
        'param_types': ['Byte', 'Byte'],
    },
    0x11: {
        'name': 'writebytetoaddr',
        'param_names': ['value', 'offset'],
        'param_types': ['Byte', 'Pointer'],
    },
    0x12: {
        'name': 'loadbytefromaddr',
        'param_names': ['destination', 'source'],
        'param_types': ['Byte', 'Pointer'],
    },
    0x13: {
        'name': 'setptrbyte',
        'param_names': ['source', 'destination'],
        'param_types': ['Byte', 'Pointer'],
    },
    0x14: {
        'name': 'copylocal',
        'param_names': ['destination', 'source'],
        'param_types': ['Byte', 'Byte'],
    },
    0x15: {
        'name': 'copybyte',
        'param_names': ['destination', 'source'],
        'param_types': ['Pointer', 'Pointer'],
    },
    0x16: {
        'name': 'setvar',
        'param_names': ['destination', 'value'],
        'param_types': ['Variable', 'Half'],
    },
    0x17: {
        'name': 'addvar',
        'param_names': ['destination', 'value'],
        'param_types': ['Variable', 'Half'],
    },
    0x18: {
        'name': 'subvar',
        'param_names': ['destination', 'value'],
        'param_types': ['Variable', 'Half'],
    },
    0x19: {
        'name': 'copyvar',
        'param_names': ['destination', 'source'],
        'param_types': ['Variable', 'Variable'],
    },
    0x1a: {
        'name': 'setorcopyvar',
        'param_names': ['destination', 'source'],
        'param_types': ['Variable', 'Variable'],
    },
    0x1b: {
        'name': 'compare_local_to_local',
        'param_names': ['byte1', 'byte2'],
        'param_types': ['Byte', 'Byte'],
    },
    0x1c: {
        'name': 'compare_local_to_value',
        'param_names': ['a', 'b'],
        'param_types': ['Byte', 'Byte'],
    },
    0x1d: {
        'name': 'compare_local_to_addr',
        'param_names': ['a', 'b'],
        'param_types': ['Byte', 'Pointer'],
    },
    0x1e: {
        'name': 'compare_addr_to_local',
        'param_names': ['a', 'b'],
        'param_types': ['Pointer', 'Byte'],
    },
    0x1f: {
        'name': 'compare_addr_to_value',
        'param_names': ['a', 'b'],
        'param_types': ['Pointer', 'Byte'],
    },
    0x20: {
        'name': 'compare_addr_to_addr',
        'param_names': ['a', 'b'],
        'param_types': ['Pointer', 'Pointer'],
    },
    0x21: {
        'name': 'compare_var_to_value',
        'param_names': ['var', 'value'],
        'param_types': ['Variable', 'Half'],
    },
    0x22: {
        'name': 'compare_var_to_var',
        'param_names': ['var1', 'var2'],
        'param_types': ['Variable', 'Variable'],
    },
    0x23: {
        'name': 'callnative',
        'param_names': ['func'],
        'param_types': ['Pointer'],
    },
    0x24: {
        'name': 'gotonative',
        'param_names': ['func'],
        'param_types': ['Pointer'],
        'terminating': True,
    },
    0x25: {
        'name': 'special',
        'param_names': ['function'],
        'param_types': ['Special'],
    },
    0x26: {
        'name': 'specialvar',
        'param_names': ['output', 'function'],
        'param_types': ['Variable', 'Special'],
    },
    0x27: {
        'name': 'waitstate',
        'param_names': [],
        'param_types': [],
    },
    0x28: {
        'name': 'delay',
        'param_names': ['time'],
        'param_types': ['Half'],
    },
    0x29: {
        'name': 'setflag',
        'param_names': ['a'],
        'param_types': ['Flag'],
    },
    0x2a: {
        'name': 'clearflag',
        'param_names': ['a'],
        'param_types': ['Flag'],
    },
    0x2b: {
        'name': 'checkflag',
        'param_names': ['a'],
        'param_types': ['Flag'],
    },
    0x2c: {
        'name': 'initclock',
        'param_names': [],
        'param_types': [],
    },
    0x2d: {
        'name': 'dodailyevents',
        'param_names': [],
        'param_types': [],
    },
    0x2e: {
        'name': 'gettime',
        'param_names': [],
        'param_types': [],
    },
    0x2f: {
        'name': 'playse',
        'param_names': ['sound_number'],
        'param_types': ['Song'],
    },
    0x30: {
        'name': 'waitse',
        'param_names': [],
        'param_types': [],
    },
    0x31: {
        'name': 'playfanfare',
        'param_names': ['fanfare_number'],
        'param_types': ['Song'],
    },
    0x32: {
        'name': 'waitfanfare',
        'param_names': [],
        'param_types': [],
    },
    0x33: {
        'name': 'playbgm',
        'param_names': ['song_number', 'unknown'],
        'param_types': ['Song', 'Byte'],
    },
    0x34: {
        'name': 'savebgm',
        'param_names': ['song_number'],
        'param_types': ['Song'],
    },
    0x35: {
        'name': 'fadedefaultbgm',
        'param_names': [],
        'param_types': [],
    },
    0x36: {
        'name': 'fadenewbgm',
        'param_names': ['song_number'],
        'param_types': ['Song'],
    },
    0x37: {
        'name': 'fadeoutbgm',
        'param_names': ['speed'],
        'param_types': ['Byte'],
    },
    0x38: {
        'name': 'fadeinbgm',
        'param_names': ['speed'],
        'param_types': ['Byte'],
    },
    0x39: {
        'name': 'warp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x3a: {
        'name': 'warpsilent',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x3b: {
        'name': 'warpdoor',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x3c: {
        'name': 'warphole',
        'param_names': ['map'],
        'param_types': ['MapID'],
    },
    0x3d: {
        'name': 'warpteleport',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'word', 'word'],
    },
    0x3e: {
        'name': 'setwarp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x3f: {
        'name': 'setdynamicwarp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x40: {
        'name': 'setdivewarp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x41: {
        'name': 'setholewarp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': ['MapID', 'Byte', 'Half', 'Half'],
    },
    0x42: {
        'name': 'getplayerxy',
        'param_names': ['X', 'Y'],
        'param_types': ['Variable', 'Variable'],
    },
    0x43: {
        'name': 'countpokemon',
        'param_names': [],
        'param_types': [],
    },
    0x44: {
        'name': 'additem',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x45: {
        'name': 'removeitem',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x46: {
        'name': 'checkitemspace',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x47: {
        'name': 'checkitem',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x48: {
        'name': 'checkitemtype',
        'param_names': ['index'],
        'param_types': ['Item'],
    },
    0x49: {
        'name': 'givepcitem',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x4a: {
        'name': 'checkpcitem',
        'param_names': ['index', 'quantity'],
        'param_types': ['Item', 'Half'],
    },
    0x4b: {
        'name': 'adddecor',
        'param_names': ['decoration'],
        'param_types': ['Decoration'],
    },
    0x4c: {
        'name': 'removedecor',
        'param_names': ['decoration'],
        'param_types': ['Decoration'],
    },
    0x4d: {
        'name': 'hasdecor',
        'param_names': ['decoration'],
        'param_types': ['Decoration'],
    },
    0x4e: {
        'name': 'checkdecor',
        'param_names': ['decoration'],
        'param_types': ['Decoration'],
    },
    0x4f: {
        'name': 'applymovement',
        'param_names': ['index', 'movements'],
        'param_types': ['Variable', 'MovementPointer'],
    },
    0x50: {
        'name': 'applymovement',
        'param_names': ['index', 'movements', 'mapGroup', 'mapNum'],
        'param_types': ['Variable', 'MovementPointer', 'Byte', 'Byte'],
    },
    0x51: {
        'name': 'waitmovement',
        'param_names': ['index'],
        'param_types': ['Variable'],
    },
    0x52: {
        'name': 'waitmovement',
        'param_names': ['index', 'mapBank', 'mapNum'],
        'param_types': ['Variable', 'Byte', 'Byte'],
    },
    0x53: {
        'name': 'removeobject',
        'param_names': ['localId', 'mapGroup', 'mapNum'],
        'param_types': ['Variable'],
    },
    0x54: {
        'name': 'removeobject',
        'param_names': ['localId', 'mapGroup', 'mapNum'],
        'param_types': ['Variable', 'Byte', 'Byte'],
    },
    0x55: {
        'name': 'addobject',
        'param_names': ['localId'],
        'param_types': ['Variable'],
    },
    0x56: {
        'name': 'addobject',
        'param_names': ['localId', 'mapGroup', 'mapNum'],
        'param_types': ['Variable', 'Byte', 'Byte'],
    },
    0x57: {
        'name': 'setobjectxy',
        'param_names': ['index', 'x', 'y'],
        'param_types': ['Variable', 'Variable', 'Variable'],
    },
    0x58: {
        'name': 'showobject',
        'param_names': ['index', 'map'],
        'param_types': ['Variable', 'MapID'],
    },
    0x59: {
        'name': 'hideobject',
        'param_names': ['index', 'map'],
        'param_types': ['Variable', 'MapID'],
    },
    0x5a: {
        'name': 'faceplayer',
        'param_names': [],
        'param_types': [],
    },
    0x5b: {
        'name': 'turnobject',
        'param_names': ['index', 'direction'],
        'param_types': ['Variable', 'Byte'],
    },
    # Params vary depending on the value of `type`.
    # See TrainerbattleArgs.
    0x5c: {
        'name': 'trainerbattle',
        'param_names': ['type', 'trainer', 'word', 'pointer1', 'pointer2', 'pointer3', 'pointer4'],
        'param_types': ['TrainerBattleArgs'],
    },
    0x5d: {
        'name': 'battlebegin',
        'param_names': [],
        'param_types': [],
    },
    0x5e: {
        'name': 'ontrainerbattleend',
        'param_names': [],
        'param_types': [],
    },
    0x5f: {
        'name': 'ontrainerbattleendgoto',
        'param_names': [],
        'param_types': [],
    },
    0x60: {
        'name': 'checktrainerflag',
        'param_names': ['trainer'],
        'param_types': ['Half'],
    },
    0x61: {
        'name': 'settrainerflag',
        'param_names': ['trainer'],
        'param_types': ['Half'],
    },
    0x62: {
        'name': 'cleartrainerflag',
        'param_names': ['trainer'],
        'param_types': ['Half'],
    },
    0x63: {
        'name': 'setobjectxyperm',
        'param_names': ['index', 'x', 'y'],
        'param_types': ['Variable', 'Variable', 'Variable'],
    },
    0x64: {
        'name': 'moveobjectoffscreen',
        'param_names': ['index'],
        'param_types': ['Variable'],
    },
    0x65: {
        'name': 'setobjectmovementtype',
        'param_names': ['word', 'byte'],
        'param_types': ['Variable', 'Byte'],
    },
    0x66: {
        'name': 'waitmessage',
        'param_names': [],
        'param_types': [],
    },
    0x67: {
        'name': 'message',
        'param_names': ['text'],
        'param_types': ['TextPointer'],
    },
    0x68: {
        'name': 'closemessage',
        'param_names': [],
        'param_types': [],
    },
    0x69: {
        'name': 'lockall',
        'param_names': [],
        'param_types': [],
    },
    0x6a: {
        'name': 'lock',
        'param_names': [],
        'param_types': [],
    },
    0x6b: {
        'name': 'releaseall',
        'param_names': [],
        'param_types': [],
    },
    0x6c: {
        'name': 'release',
        'param_names': [],
        'param_types': [],
    },
    0x6d: {
        'name': 'waitbuttonpress',
        'param_names': [],
        'param_types': [],
    },
    0x6e: {
        'name': 'yesnobox',
        'param_names': ['x', 'y'],
        'param_types': ['Byte', 'Byte'],
    },
    0x6f: {
        'name': 'multichoice',
        'param_names': ['x', 'y', 'list', 'b'],
        'param_types': ['Byte', 'Byte', 'Byte', 'Byte'],
    },
    0x70: {
        'name': 'multichoicedefault',
        'param_names': ['x', 'y', 'list', 'default', 'b'],
        'param_types': ['Byte', 'Byte', 'Byte', 'Byte', 'Byte'],
    },
    0x71: {
        'name': 'multichoicegrid',
        'param_names': ['x', 'y', 'list', 'per_row', 'B'],
        'param_types': ['Byte', 'Byte', 'Byte', 'Byte', 'Byte'],
    },
    0x72: {
        'name': 'drawbox',
        'param_names': [],
        'param_types': [],
    },
    0x73: {
        'name': 'erasebox',
        'param_names': ['byte1', 'byte2', 'byte3', 'byte4'],
        'param_types': ['Byte', 'Byte', 'Byte', 'Byte'],
    },
    0x74: {
        'name': 'drawboxtext',
        'param_names': ['byte1', 'byte2', 'byte3', 'byte4'],
        'param_types': ['Byte', 'Byte', 'Byte', 'Byte'],
    },
    0x75: {
        'name': 'drawmonpic',
        'param_names': ['species', 'x', 'y'],
        'param_types': ['Species', 'Byte', 'Byte'],
    },
    0x76: {
        'name': 'erasemonpic',
        'param_names': [],
        'param_types': [],
    },
    0x77: {
        'name': 'drawcontestwinner',
        'param_names': ['a'],
        'param_types': ['Byte'],
    },
    0x78: {
        'name': 'braillemessage',
        'param_names': ['text'],
        'param_types': ['Pointer'],
    },
    0x79: {
        'name': 'givemon',
        'param_names': ['species', 'level', 'item', 'unknown1', 'unknown2', 'unknown3'],
        'param_types': ['Species', 'Byte', 'Item', 'Word', 'Word', 'Byte'],
    },
    0x7a: {
        'name': 'giveegg',
        'param_names': ['species'],
        'param_types': ['Species'],
    },
    0x7b: {
        'name': 'setmonmove',
        'param_names': ['index', 'slot', 'move'],
        'param_types': ['Byte', 'Byte', 'Move'],
    },
    0x7c: {
        'name': 'checkpartymove',
        'param_names': ['index'],
        'param_types': ['Move'],
    },
    0x7d: {
        'name': 'getspeciesname',
        'param_names': ['out', 'species'],
        'param_types': ['Byte', 'Species'],
    },
    0x7e: {
        'name': 'getfirstpartymonname',
        'param_names': ['out'],
        'param_types': ['Byte'],
    },
    0x7f: {
        'name': 'getpartymonname',
        'param_names': ['out', 'slot'],
        'param_types': ['Byte', 'Variable'],
    },
    0x80: {
        'name': 'getitemname',
        'param_names': ['out', 'item'],
        'param_types': ['Byte', 'Item'],
    },
    0x81: {
        'name': 'getdecorname',
        'param_names': ['out', 'decoration'],
        'param_types': ['Byte', 'Decoration'],
    },
    0x82: {
        'name': 'getmovename',
        'param_names': ['out', 'move'],
        'param_types': ['Byte', 'Move'],
    },
    0x83: {
        'name': 'getnumberstring',
        'param_names': ['out', 'input'],
        'param_types': ['Byte', 'Variable'],
    },
    0x84: {
        'name': 'getstdstring',
        'param_names': ['out', 'index'],
        'param_types': ['Byte', 'Variable'],
    },
    0x85: {
        'name': 'getstring',
        'param_names': ['out', 'offset'],
        'param_types': ['Byte', 'TextPointer'],
    },
    0x86: {
        'name': 'pokemart',
        'param_names': ['products'],
        'param_types': ['MartPointer'],
    },
    0x87: {
        'name': 'pokemartdecor',
        'param_names': ['products'],
        'param_types': ['MartPointer'],
    },
    0x88: {
        'name': 'pokemartbp',
        'param_names': ['products'],
        'param_types': ['MartPointer'],
    },
    0x89: {
        'name': 'playslotmachine',
        'param_names': ['word'],
        'param_types': ['Variable'],
    },
    0x8a: {
        'name': 'plantberrytree',
        'param_names': [],
        'param_types': [],
    },
    0x8b: {
        'name': 'choosecontestpkmn',
        'param_names': [],
        'param_types': [],
    },
    0x8c: {
        'name': 'startcontest',
        'param_names': [],
        'param_types': [],
    },
    0x8d: {
        'name': 'showcontestresults',
        'param_names': [],
        'param_types': [],
    },
    0x8e: {
        'name': 'contestlinktransfer',
        'param_names': [],
        'param_types': [],
    },
    0x8f: {
        'name': 'random',
        'param_names': ['limit'],
        'param_types': ['Variable'],
    },
    0x90: {
        'name': 'givemoney',
        'param_names': ['value', 'check'],
        'param_types': ['Word', 'Byte'],
    },
    0x91: {
        'name': 'takemoney',
        'param_names': ['value', 'check'],
        'param_types': ['Word', 'Byte'],
    },
    0x92: {
        'name': 'checkmoney',
        'param_names': ['value', 'check'],
        'param_types': ['Word', 'Byte'],
    },
    0x93: {
        'name': 'showmoneybox',
        'param_names': ['x', 'y', 'check'],
        'param_types': ['Byte', 'Byte', 'Byte'],
    },
    0x94: {
        'name': 'hidemoneybox',
        'param_names': [],
        'param_types': [],
    },
    0x95: {
        'name': 'updatemoneybox',
        'param_names': ['x', 'y', 'check'],
        'param_types': ['Byte', 'Byte', 'Byte'],
    },
    0x96: {
        'name': 'getpricereduction',
        'param_names': [],
        'param_types': [],
    },
    0x97: {
        'name': 'fadescreen',
        'param_names': ['effect'],
        'param_types': ['Byte'],
    },
    0x98: {
        'name': 'fadescreenspeed',
        'param_names': ['effect', 'speed'],
        'param_types': ['Byte', 'Byte'],
    },
    0x99: {
        'name': 'setflashradius',
        'param_names': ['word'],
        'param_types': ['Variable'],
    },
    0x9a: {
        'name': 'animateflash',
        'param_names': ['Byte'],
        'param_types': ['Byte'],
    },
    0x9b: {
        'name': 'messageautoscroll',
        'param_names': ['Pointer'],
        'param_types': ['TextPointer'],
    },
    0x9c: {
        'name': 'dofieldeffect',
        'param_names': ['animation'],
        'param_types': ['Variable'],
    },
    0x9d: {
        'name': 'setfieldeffectarg',
        'param_names': ['argument', 'param'],
        'param_types': ['Byte', 'Variable'],
    },
    0x9e: {
        'name': 'waitfieldeffect',
        'param_names': ['animation'],
        'param_types': ['Half'],
    },
    0x9f: {
        'name': 'setrespawn',
        'param_names': ['flightspot'],
        'param_types': ['Variable'],
    },
    0xa0: {
        'name': 'checkplayergender',
        'param_names': [],
        'param_types': [],
    },
    0xa1: {
        'name': 'playmoncry',
        'param_names': ['species', 'effect'],
        'param_types': ['Species', 'Variable'],
    },
    0xa2: {
        'name': 'setmetatile',
        'param_names': ['x', 'y', 'metatile_number', 'tile_attrib'],
        'param_types': ['Variable', 'Variable', 'Variable', 'Variable'],
    },
    0xa3: {
        'name': 'resetweather',
        'param_names': [],
        'param_types': [],
    },
    0xa4: {
        'name': 'setweather',
        'param_names': ['type'],
        'param_types': ['Variable'],
    },
    0xa5: {
        'name': 'doweather',
        'param_names': [],
        'param_types': [],
    },
    0xa6: {
        'name': 'setstepcallback',
        'param_names': ['subroutine'],
        'param_types': ['Byte'],
    },
    0xa7: {
        'name': 'setmaplayoutindex',
        'param_names': ['index'],
        'param_types': ['Layout'],
    },
    0xa8: {
        'name': 'setobjectpriority',
        'param_names': ['index', 'map', 'priority'],
        'param_types': ['Variable', 'MapID', 'Byte'],
    },
    0xa9: {
        'name': 'resetobjectpriority',
        'param_names': ['index', 'map'],
        'param_types': ['Variable', 'MapID'],
    },
    0xaa: {
        'name': 'createvobject',
        'param_names': ['sprite', 'byte2', 'x', 'y', 'elevation', 'direction'],
        'param_types': ['Byte', 'Byte', 'Variable', 'Variable', 'Byte', 'Byte'],
    },
    0xab: {
        'name': 'turnvobject',
        'param_names': ['index', 'direction'],
        'param_types': ['Byte', 'Byte'],
    },
    0xac: {
        'name': 'opendoor',
        'param_names': ['x', 'y'],
        'param_types': ['Variable', 'Variable'],
    },
    0xad: {
        'name': 'closedoor',
        'param_names': ['x', 'y'],
        'param_types': ['Variable', 'Variable'],
    },
    0xae: {
        'name': 'waitdooranim',
        'param_names': [],
        'param_types': [],
    },
    0xaf: {
        'name': 'setdooropen',
        'param_names': ['x', 'y'],
        'param_types': ['Variable', 'Variable'],
    },
    0xb0: {
        'name': 'setdoorclosed2',
        'param_names': ['x', 'y'],
        'param_types': ['Variable', 'Variable'],
    },
    0xb1: {
        'name': 'addelevmenuitem',
        'param_names': [],
        'param_types': [],
        #'param_names': ['a', 'b', 'c', 'd'],
        #'param_types': ['Byte', 'Variable', 'Variable', 'Variable'],
    },
    0xb2: {
        'name': 'showelevmenu',
        'param_names': [],
        'param_types': [],
    },
    0xb3: {
        'name': 'checkcoins',
        'param_names': ['out'],
        'param_types': ['Variable'],
    },
    0xb4: {
        'name': 'givecoins',
        'param_names': ['count'],
        'param_types': ['Variable'],
    },
    0xb5: {
        'name': 'takecoins',
        'param_names': ['word'],
        'param_types': ['Variable'],
    },
    0xb6: {
        'name': 'setwildbattle',
        'param_names': ['species', 'level', 'item'],
        'param_types': ['Species', 'Byte', 'Item'],
    },
    0xb7: {
        'name': 'dowildbattle',
        'param_names': [],
        'param_types': [],
    },
    0xb8: {
        'name': 'setvaddress',
        'param_names': ['long', 'word'],
        'param_types': ['Pointer', 'Half'],
    },
    0xb9: {
        'name': 'vgoto',
        'param_names': ['Pointer'],
        'param_types': ['EventScriptPointer'],
        'terminating': True,
    },
    0xba: {
        'name': 'vcall',
        'param_names': ['Pointer'],
        'param_types': ['EventScriptPointer'],
    },
    0xbb: {
        'name': 'vgoto_if',
        'param_names': ['byte', 'pointer'],
        'param_types': ['Byte', 'EventScriptPointer'],
    },
    0xbc: {
        'name': 'vcall_if',
        'param_names': ['byte', 'pointer'],
        'param_types': ['Byte', 'EventScriptPointer'],
    },
    0xbd: {
        'name': 'vmessage',
        'param_names': ['pointer'],
        'param_types': ['Pointer'],
    },
    0xbe: {
        'name': 'vloadptr',
        'param_names': ['pointer'],
        'param_types': ['Pointer'],
    },
    0xbf: {
        'name': 'vbufferstring',
        'param_names': ['byte', 'pointer'],
        'param_types': ['Byte', 'Pointer'],
    },
    0xc0: {
        'name': 'showcoinsbox',
        'param_names': ['x', 'y'],
        'param_types': ['Byte', 'Byte'],
    },
    0xc1: {
        'name': 'hidecoinsbox',
        'param_names': ['x', 'y'],
        'param_types': ['Byte', 'Byte'],
    },
    0xc2: {
        'name': 'updatecoinsbox',
        'param_names': ['x', 'y'],
        'param_types': ['Byte', 'Byte'],
    },
    0xc3: {
        'name': 'incrementgamestat',
        'param_names': ['stat'],
        'param_types': ['Byte'],
    },
    0xc4: {
        'name': 'setescapewarp',
        'param_names': ['map', 'warp', 'x', 'y'],
        'param_types': ['MapID', 'Byte', 'Variable', 'Variable'],
    },
    0xc5: {
        'name': 'waitmoncry',
        'param_names': [],
        'param_types': [],
    },
    0xc6: {
        'name': 'bufferboxname',
        'param_names': ['out', 'box'],
        'param_types': ['Byte', 'Half'],
    },
    0xc7: {
        'name': 'textcolor',
        'param_names': ['color'],
        'param_types': ['Byte'],
    },
    0xc8: {
        'name': 'loadhelp',
        'param_names': ['pointer'],
        'param_types': ['Pointer'],
    },
    0xc9: {
        'name': 'unloadhelp',
        'param_names': [],
        'param_types': [],
    },
    0xca: {
        'name': 'signmsg',
        'param_names': [],
        'param_types': [],
    },
    0xcb: {
        'name': 'normalmsg',
        'param_names': [],
        'param_types': [],
    },
    0xcc: {
        'name': 'comparehiddenvar',
        'param_names': ['a', 'value'],
        'param_types': ['Byte', 'Word'],
    },
    0xcd: {
        'name': 'setmonobedient',
        'param_names': ['slot'],
        'param_types': ['Variable'],
    },
    0xce: {
        'name': 'checkmonobedience',
        'param_names': ['slot'],
        'param_types': ['Variable'],
    },
    0xcf: {
        'name': 'execram',
        'param_names': [],
        'param_types': [],
        'terminating': True,
    },
    0xd0: {
        'name': 'setworldmapflag',
        'param_names': ['worldmapflag'],
        'param_types': ['Half'],
    },
    0xd1: {
        'name': 'warpteleport2',
        'param_names': ['map', 'warp', 'x', 'y'],
        'param_types': ['MapID', 'Byte', 'Variable', 'Variable'],
    },
    0xd2: {
        'name': 'setmonmetlocation',
        'param_names': ['slot', 'location'],
        'param_types': ['Variable', 'Byte'],
    },
    0xd3: {
        'name': 'getbraillestringwidth',
        'param_names': ['pointer'],
        'param_types': ['Pointer'],
    },
    0xd4: {
        'name': 'bufferitemnameplural',
        'param_names': ['out', 'item', 'quantity'],
        'param_types': ['Byte', 'Variable', 'Variable'],
    },
}

map_commands = {
    0x2: {
        'name': 'map_script_2',
        'param_types': ['Variable', 'Half', 'EventScriptPointer'],
        'terminating': True,
    },
    0x4: {
        'name': 'map_script_2',
        'param_types': ['Variable', 'Half', 'EventScriptPointer'],
        'terminating': True,
    }
}



def main():

    # 0x1655ED, 0xC
    with open("baserom.gba", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as baserom:
        offset = 0x1655ED
        size = 0xC
        script = EventScript(data=baserom[offset : offset + size])

    script.parse()



if __name__ == "__main__":
    main()


