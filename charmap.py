# coding: utf-8

"""Charmap for Pokémon Firered.
"""

from constants import pokefirered_constants
from rom import *

def decode(input, decode_charmap):
    old = bytearray(input)
    new = u''
    i = 0
    len_old = len(old)
    while i < len_old:
        start = i
        item = decode_charmap
        while hasattr(item, 'get'):
            char = old[i]
            item_ = item.get(char)
            if item_ is None:
                #print("invalid byte for charmap: {:X}".format(item_))
                raise KeyError
            item = item_
            #print(item)
            i += 1
        if item in ['{COLOR}', '{HIGHLIGHT}', '{SHADOW}']:
            color = colors.get(old[i])
            if color:
                item += '{{{}}}'.format(color)
                i += 1
        elif item in ['{COLOR_HIGHLIGHT_SHADOW}']:
            for _ in xrange(3):
                color = colors.get(old[i])
                if color:
                    item += '{{{}}}'.format(color)
                    i += 1
        elif item in ['{CLEAR_TO}', '{PAUSE}']:
            item = item[:-1] + ' 0x' + "{0:0{1}X}".format(old[i],2) + '}'
            i += 1
        elif item in ['{UNK_CTRL_F9}']:
            item = item[:-1] + ' 0x' + "{0:0{1}X}".format(old[i],2) + '}'
            i += 1
        elif item in ['{PLAY_BGM}']:
            mus = pokefirered_constants['songs'][read_half(old[i: i+2])]
            item += "{}".format(r"{" + mus + r"}")
            i += 2
        chars = item
        if chars is None:
            chars = ''.join('{' + "{0:#0{1}x}".format(old[start],4) + '}' for byte in old[start:i])
        new += chars
    return new

def encode(input, encode_charmap):
    old = input
    new = ''
    i = 0
    len_old = len(old)
    while i < len_old:
        char = old[i]
        if char == '{':
            j = i + old.find('}', i) + 1
            char = old[i:j]
            i = j
        else:
            i += 1
        chars = encode_charmap.get(char)
        if chars is None:
            # assume hex i.e. '{FF}'
            chars = chr(int(char[1:-1], 16))
        new += chars
    return new


colors = [
    'TRANSPARENT',
    'WHITE',
    'DARK_GREY',
    'LIGHT_GREY',
    'RED',
    'LIGHT_RED',
    'GREEN',
    'LIGHT_GREEN',
    'BLUE',
    'LIGHT_BLUE',
    'DYNAMIC_COLOR1',
    'DYNAMIC_COLOR2',
    'DYNAMIC_COLOR3',
    'DYNAMIC_COLOR4',
    'DYNAMIC_COLOR5',
    'DYNAMIC_COLOR6',
]
colors = dict(enumerate(colors))

en_decode = {
    0x00: u' ',
    0x01: u'À',
    0x02: u'Á',
    0x03: u'Â',
    0x04: u'Ç',
    0x05: u'È',
    0x06: u'É',
    0x07: u'Ê',
    0x08: u'Ë',
    0x09: u'Ì',
    0x0B: u'Î',
    0x0C: u'Ï',
    0x0D: u'Ò',
    0x0E: u'Ó',
    0x0F: u'Ô',
    0x10: u'Œ',
    0x11: u'Ù',
    0x12: u'Ú',
    0x13: u'Û',
    0x14: u'Ñ',
    0x15: u'ß',
    0x16: u'à',
    0x17: u'á',
    0x19: u'ç',
    0x1A: u'è',
    0x1B: u'é',
    0x1C: u'ê',
    0x1D: u'ë',
    0x1E: u'ì',
    0x20: u'î',
    0x21: u'ï',
    0x22: u'ò',
    0x23: u'ó',
    0x24: u'ô',
    0x25: u'œ',
    0x26: u'ù',
    0x27: u'ú',
    0x28: u'û',
    0x29: u'ñ',
    0x2A: u'º',
    0x2B: u'ª',
    0x2C: u'¹',
    0x2D: u'&',
    0x2E: u'+',
    0x34: u'{0x34}', # None # '[Lv]'
    0x35: u'=',
    0x36: u';',
    0x51: u'¿',
    0x52: u'¡',
    0x53: {
	None: u'{PK}',
	0x54: u'{PKMN}',
    },
    0x54: u'{MN}',
    0x55: {
	None: u'{PO}',
	0x56:{0x57:{0x58:{0x59: u'{POKEBLOCK}'}}},
    },
    0x56: u'{KE}',
    0x57: u'{BL}',
    0x58: u'{OC}',
    0x59: u'{K}',
    0x5A: u'Í',
    0x5B: u'%',
    0x5C: u'(',
    0x5D: u')',
    0x68: u'â',
    0x6F: u'í',
    0x7F: u'{0x7F}',
    0xA1: u'0',
    0xA2: u'1',
    0xA3: u'2',
    0xA4: u'3',
    0xA5: u'4',
    0xA6: u'5',
    0xA7: u'6',
    0xA8: u'7',
    0xA9: u'8',
    0xAA: u'9',
    0xAB: u'!',
    0xAC: u'?',
    0xAD: u'.',
    0xAE: u'-',
    0xAF: u'·',
    0xB0: u'…',
    0xB1: u'“',
    0xB2: u'”',
    0xB3: u'‘',
    0xB4: u'\'', #u'\'',
    0xB5: u'♂',
    0xB6: u'♀',
    0xB7: u'¥',
    0xB8: u',',
    0xB9: u'×',
    0xBA: u'/',
    0xBB: u'A',
    0xBC: u'B',
    0xBD: u'C',
    0xBE: u'D',
    0xBF: u'E',
    0xC0: u'F',
    0xC1: u'G',
    0xC2: u'H',
    0xC3: u'I',
    0xC4: u'J',
    0xC5: u'K',
    0xC6: u'L',
    0xC7: u'M',
    0xC8: u'N',
    0xC9: u'O',
    0xCA: u'P',
    0xCB: u'Q',
    0xCC: u'R',
    0xCD: u'S',
    0xCE: u'T',
    0xCF: u'U',
    0xD0: u'V',
    0xD1: u'W',
    0xD2: u'X',
    0xD3: u'Y',
    0xD4: u'Z',
    0xD5: u'a',
    0xD6: u'b',
    0xD7: u'c',
    0xD8: u'd',
    0xD9: u'e',
    0xDA: u'f',
    0xDB: u'g',
    0xDC: u'h',
    0xDD: u'i',
    0xDE: u'j',
    0xDF: u'k',
    0xE0: u'l',
    0xE1: u'm',
    0xE2: u'n',
    0xE3: u'o',
    0xE4: u'p',
    0xE5: u'q',
    0xE6: u'r',
    0xE7: u's',
    0xE8: u't',
    0xE9: u'u',
    0xEA: u'v',
    0xEB: u'w',
    0xEC: u'x',
    0xED: u'y',
    0xEE: u'z',
    0xF0: u':',
    0xF1: u'Ä',
    0xF2: u'Ö',
    0xF3: u'Ü',
    0xF4: u'ä',
    0xF5: u'ö',
    0xF6: u'ü',
    0xF7: u'{0xF7}', # None
    0xF8: u'{0xF8}', # None
    0xF9: u'{UNK_CTRL_F9}',
    0xFA: u'\\l', # None
    0xFB: u'\\p',
    0xFC: {
	0: '{NAME_END}',
	1: '{COLOR}',
	2: '{HIGHLIGHT}',
	3: '{SHADOW}',
	4: '{COLOR_HIGHLIGHT_SHADOW}',
	5: '{PALETTE}',
	6: '{SIZE}',
	7: '{UNKNOWN_7}',
	8: '{PAUSE}',
	9: '{PAUSE_UNTIL_PRESS}',
	10: '{UNKNOWN_A}',
	11: '{PLAY_BGM}',
	12: '{ESCAPE}',
	13: '{SHIFT_TEXT}',
	14: '{UNKNOWN_E}',
	15: '{UNKNOWN_F}',
	16: '{PLAY_SE}',
	17: '{CLEAR}',
	18: '{SKIP}',
	19: '{CLEAR_TO}',
	20: '{UNKNOWN_14}',
	21: '{JPN}',
	22: '{ENG}',
	23: '{PAUSE_MUSIC}',
	24: '{RESUME_MUSIC}',
    },
    0xFD: {
	1: u'{PLAYER}',
	2: u'{STR_VAR_1}',
	3: u'{STR_VAR_2}',
	4: u'{STR_VAR_3}',
	5: u'{KUN}',
	6: u'{RIVAL}',
	7: u'{VERSION}',
	8: u'{EVIL_TEAM}',
	9: u'{GOOD_TEAM}',
	10: u'{EVIL_LEADER}',
	11: u'{GOOD_LEADER}',
	12: u'{EVIL_LEGENDARY}',
	13: u'{GOOD_LEGENDARY}',
    },
    0xFE: u'\\n',
    0xFF: u'$',
}

jp_decode = {

# Hiragana
    0x01: u'あ',
    0x02: u'い',
    0x03: u'う',
    0x04: u'え',
    0x05: u'お',
    0x06: u'か',
    0x07: u'き',
    0x08: u'く',
    0x09: u'け',
    0x0A: u'こ',
    0x0B: u'さ',
    0x0C: u'し',
    0x0D: u'す',
    0x0E: u'せ',
    0x0F: u'そ',
    0x10: u'た',
    0x11: u'ち',
    0x12: u'つ',
    0x13: u'て',
    0x14: u'と',
    0x15: u'な',
    0x16: u'に',
    0x17: u'ぬ',
    0x18: u'ね',
    0x19: u'の',
    0x1A: u'は',
    0x1B: u'ひ',
    0x1C: u'ふ',
    0x1D: u'へ',
    0x1E: u'ほ',
    0x1F: u'ま',
    0x20: u'み',
    0x21: u'む',
    0x22: u'め',
    0x23: u'も',
    0x24: u'や',
    0x25: u'ゆ',
    0x26: u'よ',
    0x27: u'ら',
    0x28: u'り',
    0x29: u'る',
    0x2A: u'れ',
    0x2B: u'ろ',
    0x2C: u'わ',
    0x2D: u'を',
    0x2E: u'ん',
    0x2F: u'ぁ',
    0x30: u'ぃ',
    0x31: u'ぅ',
    0x32: u'ぇ',
    0x33: u'ぉ',
    0x34: u'ゃ',
    0x35: u'ゅ',
    0x36: u'ょ',
    0x37: u'が',
    0x38: u'ぎ',
    0x39: u'ぐ',
    0x3A: u'げ',
    0x3B: u'ご',
    0x3C: u'ざ',
    0x3D: u'じ',
    0x3E: u'ず',
    0x3F: u'ぜ',
    0x40: u'ぞ',
    0x41: u'だ',
    0x42: u'ぢ',
    0x43: u'づ',
    0x44: u'で',
    0x45: u'ど',
    0x46: u'ば',
    0x47: u'び',
    0x48: u'ぶ',
    0x49: u'べ',
    0x4A: u'ぼ',
    0x4B: u'ぱ',
    0x4C: u'ぴ',
    0x4D: u'ぷ',
    0x4E: u'ぺ',
    0x4F: u'ぽ',
    0x50: u'っ',

# Katakana
    0x51: u'ア',
    0x52: u'イ',
    0x53: u'ウ',
    0x54: u'エ',
    0x55: u'オ',
    0x56: u'カ',
    0x57: u'キ',
    0x58: u'ク',
    0x59: u'ケ',
    0x5A: u'コ',
    0x5B: u'サ',
    0x5C: u'シ',
    0x5D: u'ス',
    0x5E: u'セ',
    0x5F: u'ソ',
    0x60: u'タ',
    0x61: u'チ',
    0x62: u'ツ',
    0x63: u'テ',
    0x64: u'ト',
    0x65: u'ナ',
    0x66: u'ニ',
    0x67: u'ヌ',
    0x68: u'ネ',
    0x69: u'ノ',
    0x6A: u'ハ',
    0x6B: u'ヒ',
    0x6C: u'フ',
    0x6D: u'ヘ',
    0x6E: u'ホ',
    0x6F: u'マ',
    0x70: u'ミ',
    0x71: u'ム',
    0x72: u'メ',
    0x73: u'モ',
    0x74: u'ヤ',
    0x75: u'ユ',
    0x76: u'ヨ',
    0x77: u'ラ',
    0x78: u'リ',
    0x79: u'ル',
    0x7A: u'レ',
    0x7B: u'ロ',
    0x7C: u'ワ',
    0x7D: u'ヲ',
    0x7E: u'ン',
    0x7F: u'ァ',
    0x80: u'ィ',
    0x81: u'ゥ',
    0x82: u'ェ',
    0x83: u'ォ',
    0x84: u'ャ',
    0x85: u'ュ',
    0x86: u'ョ',
    0x87: u'ガ',
    0x88: u'ギ',
    0x89: u'グ',
    0x8A: u'ゲ',
    0x8B: u'ゴ',
    0x8C: u'ザ',
    0x8D: u'ジ',
    0x8E: u'ズ',
    0x8F: u'ゼ',
    0x90: u'ゾ',
    0x91: u'ダ',
    0x92: u'ヂ',
    0x93: u'ヅ',
    0x94: u'デ',
    0x95: u'ド',
    0x96: u'バ',
    0x97: u'ビ',
    0x98: u'ブ',
    0x99: u'ベ',
    0x9A: u'ボ',
    0x9B: u'パ',
    0x9C: u'ピ',
    0x9D: u'プ',
    0x9E: u'ペ',
    0x9F: u'ポ',
    0xA0: u'ッ',

# Numbers
    0xA1: u'0',
    0xA2: u'1',
    0xA3: u'2',
    0xA4: u'3',
    0xA5: u'4',
    0xA6: u'5',
    0xA7: u'6',
    0xA8: u'7',
    0xA9: u'8',
    0xAA: u'9',

# English characters
    0xB0: u'‥', #u'…',
    0xB1: u'“',
    0xB2: u'”',
    0xB3: u'‘',
    0xB4: u'’', #u'\'',
    0xB5: u'♂',
    0xB6: u'♀',
    0xB7: u'¥',
    0xB8: u',',
    0xB9: u'×',
    0xBA: u'/',
    0xBB: u'A',
    0xBC: u'B',
    0xBD: u'C',
    0xBE: u'D',
    0xBF: u'E',
    0xC0: u'F',
    0xC1: u'G',
    0xC2: u'H',
    0xC3: u'I',
    0xC4: u'J',
    0xC5: u'K',
    0xC6: u'L',
    0xC7: u'M',
    0xC8: u'N',
    0xC9: u'O',
    0xCA: u'P',
    0xCB: u'Q',
    0xCC: u'R',
    0xCD: u'S',
    0xCE: u'T',
    0xCF: u'U',
    0xD0: u'V',
    0xD1: u'W',
    0xD2: u'X',
    0xD3: u'Y',
    0xD4: u'Z',
    0xD5: u'a',
    0xD6: u'b',
    0xD7: u'c',
    0xD8: u'd',
    0xD9: u'e',
    0xDA: u'f',
    0xDB: u'g',
    0xDC: u'h',
    0xDD: u'i',
    0xDE: u'j',
    0xDF: u'k',
    0xE0: u'l',
    0xE1: u'm',
    0xE2: u'n',
    0xE3: u'o',
    0xE4: u'p',
    0xE5: u'q',
    0xE6: u'r',
    0xE7: u's',
    0xE8: u't',
    0xE9: u'u',
    0xEA: u'v',
    0xEB: u'w',
    0xEC: u'x',
    0xED: u'y',
    0xEE: u'z',

# Japanese punctuation
    0x00: u'　',
    0xAB: u'！',
    0xAC: u'？',
    0xAD: u'。',
    0xAE: u'ー',
    0xAF: u'·',
    #0xB0: u'⋯',

    0xF9: u'{UNK_CTRL_F9}',
    0xFA: u'\\l',
    0xFB: u'\\p',
    0xFC: {
	0: '{NAME_END}',
	1: '{COLOR}',
	2: '{HIGHLIGHT}',
	3: '{SHADOW}',
	4: '{COLOR_HIGHLIGHT_SHADOW}',
	6: '{SIZE}',
	8: '{PAUSE}',
	9: '{PAUSE_UNTIL_PRESS}',
	12: '{ESCAPE}',
	13: '{SHIFT_TEXT}',
	16: '{PLAY_MUSIC}',
	21: '{ENLARGE}',
	22: '{SET_TO_DEFAULT_SIZE}',
	23: '{PAUSE_MUSIC}',
	24: '{RESUME_MUSIC}',
    },
    0xFD: {
	1: u'{PLAYER}',
	2: u'{STR_VAR_1}',
	3: u'{STR_VAR_2}',
	4: u'{STR_VAR_3}',
	5: u'{KUN}',
	6: u'{RIVAL}',
	7: u'{VERSION}',
	8: u'{EVIL_TEAM}',
	9: u'{GOOD_TEAM}',
	10: u'{EVIL_LEADER}',
	11: u'{GOOD_LEADER}',
	12: u'{EVIL_LEGENDARY}',
	13: u'{GOOD_LEGENDARY}',
    },
    0xFE: u'\\n',
    0xFF: u'$',

}


def reverse_charmap(charmap):
    encode = {}
    def recurse(keys, value):
        if type(value) is dict:
            for k, v in value.items():
                if k is None:
                    recurse(keys, v)
                else:
                    recurse(keys + [k], v)
        else:
            encode[value] = ''.join(map(chr, keys))
    recurse([], charmap)
    return encode

def old_reverse_charmap(charmap):
    encode = {}
    for k, v in charmap.items():
        if type(v) is dict:
            for k2, v2 in v.items():
                if k2 is not None:
                    encode[v2] = chr(k) + chr(k2)
                else:
                    encode[v2] = chr(k)
        else:
            encode[v] = chr(k)
    return encode

en_encode = reverse_charmap(en_decode)
