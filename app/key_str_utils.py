from key import Key

STR_TO_KEY = {
    # Numbers
    '0': Key.KEY_0,
    '1': Key.KEY_1,
    '2': Key.KEY_2,
    '3': Key.KEY_3,
    '4': Key.KEY_4,
    '5': Key.KEY_5,
    '6': Key.KEY_6,
    '7': Key.KEY_7,
    '8': Key.KEY_8,
    '9': Key.KEY_9,
    # Letters
    'a': Key.KEY_A,
    'b': Key.KEY_B,
    'c': Key.KEY_C,
    'd': Key.KEY_D,
    'e': Key.KEY_E,
    'f': Key.KEY_F,
    'g': Key.KEY_G,
    'h': Key.KEY_H,
    'i': Key.KEY_I,
    'j': Key.KEY_J,
    'k': Key.KEY_K,
    'l': Key.KEY_L,
    'm': Key.KEY_M,
    'n': Key.KEY_N,
    'o': Key.KEY_O,
    'p': Key.KEY_P,
    'q': Key.KEY_Q,
    'r': Key.KEY_R,
    's': Key.KEY_S,
    't': Key.KEY_T,
    'u': Key.KEY_U,
    'v': Key.KEY_V,
    'w': Key.KEY_W,
    'x': Key.KEY_X,
    'y': Key.KEY_Y,
    'z': Key.KEY_Z,
    # Function keys
    'F1': Key.KEY_F1,
    'F2': Key.KEY_F2,
    'F3': Key.KEY_F3,
    'F4': Key.KEY_F4,
    'F5': Key.KEY_F5,
    'F6': Key.KEY_F6,
    'F7': Key.KEY_F7,
    'F8': Key.KEY_F8,
    'F9': Key.KEY_F9,
    'F10': Key.KEY_F10,
    'F11': Key.KEY_F11,
    'F12': Key.KEY_F12,
    # Special keys
    'NumLock': Key.KEY_NUMLOCK,
    'ScrollLock': Key.KEY_SCROLL,
    'Backspace': Key.KEY_BACK,
    'Tab': Key.KEY_TAB,
    'Enter': Key.KEY_RETURN,
    'Return': Key.KEY_RETURN,
    'LShift': Key.KEY_LSHIFT,
    'RShift': Key.KEY_RSHIFT,
    'Shift': Key.KEY_LSHIFT,  # Default to left
    'LCtrl': Key.KEY_LCONTROL,
    'RCtrl': Key.KEY_RCONTROL,
    'Ctrl': Key.KEY_LCONTROL,  # Default to left
    'LAlt': Key.KEY_LMENU,
    'RAlt': Key.KEY_RMENU,
    'Alt': Key.KEY_LMENU,  # Default to left
    'CapsLock': Key.KEY_CAPITAL,
    'Escape': Key.KEY_ESCAPE,
    'Esc': Key.KEY_ESCAPE,
    'Space': Key.KEY_SPACE,
    'PageUp': Key.KEY_PRIOR,
    'PageDown': Key.KEY_NEXT,
    'End': Key.KEY_END,
    'Home': Key.KEY_HOME,
    'Left': Key.KEY_LEFT,
    'Up': Key.KEY_UP,
    'Right': Key.KEY_RIGHT,
    'Down': Key.KEY_DOWN,
    'PrintScreen': Key.KEY_PRINT,
    'Insert': Key.KEY_INSERT,
    'Delete': Key.KEY_DELETE,
    'Del': Key.KEY_DELETE,
    'LWin': Key.KEY_LSUPER,
    'RWin': Key.KEY_RSUPER,
    'Win': Key.KEY_LSUPER,  # Default to left
    # Numpad
    'Numpad0': Key.KEY_NUMPAD0,
    'Numpad1': Key.KEY_NUMPAD1,
    'Numpad2': Key.KEY_NUMPAD2,
    'Numpad3': Key.KEY_NUMPAD3,
    'Numpad4': Key.KEY_NUMPAD4,
    'Numpad5': Key.KEY_NUMPAD5,
    'Numpad6': Key.KEY_NUMPAD6,
    'Numpad7': Key.KEY_NUMPAD7,
    'Numpad8': Key.KEY_NUMPAD8,
    'Numpad9': Key.KEY_NUMPAD9,
    'NumpadMultiply': Key.KEY_MULTIPLY,
    'NumpadAdd': Key.KEY_ADD,
    'NumpadSubtract': Key.KEY_SUBTRACT,
    'NumpadDecimal': Key.KEY_DECIMAL,
    'NumpadDivide': Key.KEY_DIVIDE,
    # OEM keys
    '+': Key.KEY_OEM_PLUS,
    ',': Key.KEY_OEM_COMMA,
    '-': Key.KEY_OEM_MINUS,
    '.': Key.KEY_OEM_PERIOD,
    ';': Key.KEY_OEM_1_SEMICOLON,
    '/': Key.KEY_OEM_2_FORWARD_SLASH,
    '`': Key.KEY_OEM_3_BACKTICK,
    '[': Key.KEY_OEM_4_SQUARE_BRACKET_OPEN,
    '\\': Key.KEY_OEM_5_BACKSLASH,
    ']': Key.KEY_OEM_6_SQUARE_BRACKET_CLOSE,
    "'": Key.KEY_OEM_7_SINGLE_QUOTE,
    # Media keys
    'MediaPlayPause': Key.KEY_MEDIA_PLAY_PAUSE,
    'MediaPrevTrack': Key.KEY_MEDIA_PREV_TRACK,
    'MediaNextTrack': Key.KEY_MEDIA_NEXT_TRACK,
    'VolumeMute': Key.KEY_VOLUME_MUTE,
    'VolumeUp': Key.KEY_VOLUME_UP,
    'VolumeDown': Key.KEY_VOLUME_DOWN,
    'MediaStop': Key.KEY_MEDIA_STOP,
    'BrowserBack': Key.KEY_BROWSER_BACK,
    'BrowserForward': Key.KEY_BROWSER_FORWARD,
    'BrowserRefresh': Key.KEY_BROWSER_REFRESH,
}

for letter in 'abcdefghijklmnopqrstuvwxyz':
    STR_TO_KEY[letter.upper()] = STR_TO_KEY[letter]


def str_to_key(key_str: str) -> Key:
    """Convert string key name to Key enum."""
    if key_str in STR_TO_KEY:
        return STR_TO_KEY[key_str]

    raise KeyError(f"Key '{key_str}' not found in mapping")


def key_action_type_from_name(name: str):
    from key import KeyActionType

    name = name.upper()
    if name == 'UP':
        return KeyActionType.UP
    elif name == 'DOWN':
        return KeyActionType.DOWN
    else:
        return KeyActionType.PRESS
