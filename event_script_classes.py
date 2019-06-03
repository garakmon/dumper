# event_script_classes.py

from rom import *
from constants import pokefirered_constants

import sys

#from script_commands import event_commands

#
# dict.get(key, key)

#debug = True
debug = False


movement_scripts = []
event_scripts = []
mart_scripts = []

named_pointers = {}

def get_param_class(param=""):

    return getattr(sys.modules[__name__], param)




def get_event_class(param="", incbin=[], start=0x0):

    if debug:
        print("get_event_class({}, {}, {})".format(param, incbin, start))

    if start > len(incbin) - 1:
        print("IndexError in get_event_class({}, {}, {})".format(param, incbin, start))
        start = 0

    return get_param_class(param)(incbin[start])


'''
make sure this lets the thing know to look out for a pointer and perhaps split it out
'''
class Pointer:
    def __init__(self, data=0x0):
        self.size_ = 4
        self.value_ = 0x0

    def value(self, data):
        #return get_rom_address(data)
        self.value_ = get_rom_address(data)
        return self.value_

    def label(self, data):
        label_ = "gUnknown_8{:X}".format(self.value(data))
        named_pointers[get_rom_address(data)] = label_
        return label_
    
    pass



'''
TODO: try to find a label with this address
'''
class EventScriptPointer:
    def __init__(self, data=0x0):
        self.size_ = 4
        self.value_ = 0x0
        #super().__init__()
        pass

    def label(self, data):
        label_ = "EventScript_{:X}".format(get_rom_address(data))
        named_pointers[get_rom_address(data)] = label_
        return label_



'''
'''
class TextPointer:
    def __init__(self, data=0x0):
        self.size_ = 4
        self.value_ = 0x0
        pass

    def label(self, data):
        label_ = "Text_{:X}".format(get_rom_address(data))
        named_pointers[get_rom_address(data)] = label_
        return label_



'''
'''
class MovementPointer:
    def __init__(self, data=0x0):
        self.size_ = 4
        self.value_ = 0x0

        pass

    def label(self, data):
        label_ = "Movement_{:X}".format(get_rom_address(data))
        named_pointers[get_rom_address(data)] = label_
        return label_



'''
'''
class MartPointer:
    def __init__(self, data=0x0):
        self.size_ = 4
        self.value_ = 0x0
        pass

    def label(self, data):
        label_ = "Items_{:X}".format(get_rom_address(data))
        named_pointers[get_rom_address(data)] = label_
        return label_



'''
    .macro trainerbattle type, trainer, word, pointer1, pointer2, pointer3, pointer4
        .byte 0x5c
        .byte type
        .2byte trainer
        .2byte word
        .if type == 0
            .4byte pointer1 @ text
            .4byte pointer2 @ text
        .elseif type == 1
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ event script
        .elseif type == 2
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ event script
        .elseif type == 3
            .4byte pointer1 @ text
        .elseif type == 4
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ text
        .elseif type == 5
            .4byte pointer1 @ text
            .4byte pointer2 @ text
        .elseif type == 6
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ text
            .4byte pointer4 @ event script
        .elseif type == 7
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ text
        .elseif type == 8
            .4byte pointer1 @ text
            .4byte pointer2 @ text
            .4byte pointer3 @ text
            .4byte pointer4 @ event script
        .endif
    .endm
'''
class TrainerBattleArgs:
    def __init__(self, data=0x0):
        type_sizes = {
            0: 13,
            1: 17,
            2: 17,
            3: 9,
            4: 17,
            5: 13,
            6: 21,
            7: 17,
            8: 21,
            9: 13,
        }
        self.type_ = data
        self.size_ = type_sizes.get(self.type_, 0)

    def label(self, data):
        text = ""
        tb_type = self.type_
        tb_trainer = read_half(data[1:3])
        tb_word = read_half(data[3:5])
        if self.type_ == 0:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            text += "{}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2)
            ...

        elif self.type_ == 1:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_script_1 = EventScriptPointer().label(data[13:17])
            text += "{}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_script_1)
            ...

        elif self.type_ == 2:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_script_1 = EventScriptPointer().label(data[13:17])
            text += "{}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_script_1)
            ...

        elif self.type_ == 3:
            tb_text_1 = TextPointer().label(data[5:9])
            text += "{}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1)
            ...

        elif self.type_ == 4:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_text_3 = TextPointer().label(data[13:17])
            text += "{}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_text_3)
            ...

        elif self.type_ == 5:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            text += "{}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2)
            ...

        elif self.type_ == 6:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_text_3 = TextPointer().label(data[13:17])
            tb_script_1 = EventScriptPointer().label(data[17:21])
            text += "{}, {}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_text_3, tb_script_1)
            ...

        elif self.type_ == 7:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_text_3 = TextPointer().label(data[13:17])
            text += "{}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_text_3)
            ...

        elif self.type_ == 8:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            tb_text_3 = TextPointer().label(data[13:17])
            tb_script_1 = EventScriptPointer().label(data[17:21])
            text += "{}, {}, {}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2, tb_text_3, tb_script_1)
            ...

        elif self.type_ == 9:
            tb_text_1 = TextPointer().label(data[5:9])
            tb_text_2 = TextPointer().label(data[9:13])
            text += "{}, {}, {}, {}, {}\n".format(tb_type, tb_trainer, tb_word, tb_text_1, tb_text_2)
            ...

        return text #"{}".format(self.value(data))



'''
'''
class Variable:
    '''
    '''
    def __init__(self, data=0x0):
        self.size_ = 2 # TODO: go through and verify size on all of these params

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['vars'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Special:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['specials'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Flag:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['flags'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Species:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['species'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Move:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['moves'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Item:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        if self.val_ > 16383:
            return pokefirered_constants['vars'].get(self.val_, self.val_)
        else:
            return pokefirered_constants['items'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Layout:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['layouts'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Song:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['songs'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class MapID:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        #self.val_ = (read_byte(data[0]) >> 8 | read_byte(data[1]))
        map_group = read_byte(data[0])
        map_num = read_byte(data[1])
        self.val_ = (map_num | map_group << 8)
        return pokefirered_constants['maps'].get(self.val_, self.val_)

    def label(self, data):
        # TODO: fix this stupit
        return "{}".format(self.value(data))



'''
'''
class Decoration:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return pokefirered_constants['decor'].get(self.val_, self.val_)

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Word:
    def __init__(self, data=0x0):
        self.size_ = 4

    def value(self, data):
        self.val_ = read_word(data)
        return self.val_

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Half:
    def __init__(self, data=0x0):
        self.size_ = 2

    def value(self, data):
        self.val_ = read_half(data)
        return self.val_

    def label(self, data):
        return "{}".format(self.value(data))



'''
'''
class Byte:
    def __init__(self, data=0x0):
        self.size_ = 1

    def value(self, data):
        self.val_ = read_byte(data)
        return self.val_

    def label(self, data):
        return "{}".format(self.value(data))


