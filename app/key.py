# Internal key representation

from dataclasses import dataclass
from enum import Enum

import input_pb2


class KeyState(Enum):
    UP = 0
    DOWN = 1


class KeyActionType(Enum):
    UP = 0
    DOWN = 1
    PRESS = 2


class ButtonActionType(Enum):
    UP = 0
    DOWN = 1
    PRESS = 2
    MOVE = 3


@dataclass(frozen=True)
class KeyOptions:
    no_repeat: bool
    disable_unwanted_modifiers: bool

    @classmethod
    def from_pb(cls, options: input_pb2.KeyOptions):
        return cls(
            no_repeat=options.no_repeat,
            disable_unwanted_modifiers=options.no_modifiers,
        )

    def to_pb(self):
        options = input_pb2.KeyOptions(
            no_repeat=self.no_repeat if self.no_repeat is not None else False,
            no_modifiers=self.disable_unwanted_modifiers
            if self.disable_unwanted_modifiers is not None
            else False,
        )
        return options

    def __str__(self):
        return f'KeyOptions(no_repeat: {self.no_repeat}, disable_unwanted_modifiers: {self.disable_unwanted_modifiers})'


class Key(Enum):
    KEY_0 = 0
    KEY_1 = 1
    KEY_2 = 2
    KEY_3 = 3
    KEY_4 = 4
    KEY_5 = 5
    KEY_6 = 6
    KEY_7 = 7
    KEY_8 = 8
    KEY_9 = 9
    KEY_A = 10
    KEY_B = 11
    KEY_C = 12
    KEY_D = 13
    KEY_E = 14
    KEY_F = 15
    KEY_G = 16
    KEY_H = 17
    KEY_I = 18
    KEY_J = 19
    KEY_K = 20
    KEY_L = 21
    KEY_M = 22
    KEY_N = 23
    KEY_O = 24
    KEY_P = 25
    KEY_Q = 26
    KEY_R = 27
    KEY_S = 28
    KEY_T = 29
    KEY_U = 30
    KEY_V = 31
    KEY_W = 32
    KEY_X = 33
    KEY_Y = 34
    KEY_Z = 35
    KEY_F1 = 36
    KEY_F2 = 37
    KEY_F3 = 38
    KEY_F4 = 39
    KEY_F5 = 40
    KEY_F6 = 41
    KEY_F7 = 42
    KEY_F8 = 43
    KEY_F9 = 44
    KEY_F10 = 45
    KEY_F11 = 46
    KEY_F12 = 47
    KEY_NUMLOCK = 48
    KEY_SCROLL = 49
    KEY_BACK = 50
    KEY_TAB = 51
    KEY_RETURN = 52
    KEY_LSHIFT = 53
    KEY_RSHIFT = 54
    KEY_LCONTROL = 55
    KEY_RCONTROL = 56
    KEY_LMENU = 57
    KEY_RMENU = 58
    KEY_CAPITAL = 59
    KEY_ESCAPE = 60
    KEY_CONVERT = 61
    KEY_NONCONVERT = 62
    KEY_ACCEPT = 63
    KEY_MODECHANGE = 64
    KEY_SPACE = 65
    KEY_PRIOR = 66
    KEY_NEXT = 67
    KEY_END = 68
    KEY_HOME = 69
    KEY_LEFT = 70
    KEY_UP = 71
    KEY_RIGHT = 72
    KEY_DOWN = 73
    KEY_SELECT = 74
    KEY_PRINT = 75
    KEY_EXECUTE = 76
    KEY_SNAPSHOT = 77
    KEY_INSERT = 78
    KEY_DELETE = 79
    KEY_HELP = 80
    KEY_LSUPER = 81
    KEY_RSUPER = 82
    KEY_APPS = 83
    KEY_SLEEP = 84
    KEY_NUMPAD0 = 85
    KEY_NUMPAD1 = 86
    KEY_NUMPAD2 = 87
    KEY_NUMPAD3 = 88
    KEY_NUMPAD4 = 89
    KEY_NUMPAD5 = 90
    KEY_NUMPAD6 = 91
    KEY_NUMPAD7 = 92
    KEY_NUMPAD8 = 93
    KEY_NUMPAD9 = 94
    KEY_MULTIPLY = 95
    KEY_ADD = 96
    KEY_SEPARATOR = 97
    KEY_SUBTRACT = 98
    KEY_DECIMAL = 99
    KEY_DIVIDE = 100
    KEY_OEM_PLUS = 101
    KEY_OEM_COMMA = 102
    KEY_OEM_MINUS = 103
    KEY_OEM_PERIOD = 104
    KEY_OEM_1_SEMICOLON = 105
    KEY_OEM_2_FORWARD_SLASH = 106
    KEY_OEM_3_BACKTICK = 107
    KEY_OEM_4_SQUARE_BRACKET_OPEN = 108
    KEY_OEM_5_BACKSLASH = 109
    KEY_OEM_6_SQUARE_BRACKET_CLOSE = 110
    KEY_OEM_7_SINGLE_QUOTE = 111
    # Media keys
    KEY_MEDIA_PLAY_PAUSE = 112
    KEY_MEDIA_PREV_TRACK = 113
    KEY_MEDIA_NEXT_TRACK = 114
    KEY_VOLUME_MUTE = 115
    KEY_VOLUME_UP = 116
    KEY_VOLUME_DOWN = 117
    KEY_MEDIA_STOP = 118
    KEY_BROWSER_BACK = 119
    KEY_BROWSER_FORWARD = 120
    KEY_BROWSER_REFRESH = 121
