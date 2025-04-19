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
    'NUM_LOCK': Key.KEY_NUMLOCK,
    'SCROLL_LOCK': Key.KEY_SCROLL,
    'BACKSPACE': Key.KEY_BACK,
    'TAB': Key.KEY_TAB,
    'ENTER': Key.KEY_RETURN,
    'RETURN': Key.KEY_RETURN,
    'LSHIFT': Key.KEY_LSHIFT,
    'RSHIFT': Key.KEY_RSHIFT,
    'SHIFT': Key.KEY_LSHIFT,  # Default to left
    'LCTRL': Key.KEY_LCONTROL,
    'RCTRL': Key.KEY_RCONTROL,
    'CTRL': Key.KEY_LCONTROL,  # Default to left
    'LALT': Key.KEY_LMENU,
    'RALT': Key.KEY_RMENU,
    'ALT': Key.KEY_LMENU,  # Default to left
    'CAPS_LOCK': Key.KEY_CAPITAL,
    'ESCAPE': Key.KEY_ESCAPE,
    'ESC': Key.KEY_ESCAPE,
    'SPACE': Key.KEY_SPACE,
    'PAGE_UP': Key.KEY_PRIOR,
    'PAGE_DOWN': Key.KEY_NEXT,
    'END': Key.KEY_END,
    'HOME': Key.KEY_HOME,
    'LEFT': Key.KEY_LEFT,
    'UP': Key.KEY_UP,
    'RIGHT': Key.KEY_RIGHT,
    'DOWN': Key.KEY_DOWN,
    'PRINT_SCREEN': Key.KEY_PRINT,
    'INSERT': Key.KEY_INSERT,
    'DELETE': Key.KEY_DELETE,
    'DEL': Key.KEY_DELETE,
    'LWIN': Key.KEY_LSUPER,
    'RWIN': Key.KEY_RSUPER,
    'WIN': Key.KEY_LSUPER,  # Default to left
    # Numpad
    'NUMPAD_0': Key.KEY_NUMPAD0,
    'NUMPAD_1': Key.KEY_NUMPAD1,
    'NUMPAD_2': Key.KEY_NUMPAD2,
    'NUMPAD_3': Key.KEY_NUMPAD3,
    'NUMPAD_4': Key.KEY_NUMPAD4,
    'NUMPAD_5': Key.KEY_NUMPAD5,
    'NUMPAD_6': Key.KEY_NUMPAD6,
    'NUMPAD_7': Key.KEY_NUMPAD7,
    'NUMPAD_8': Key.KEY_NUMPAD8,
    'NUMPAD_9': Key.KEY_NUMPAD9,
    'NUMPAD_MULTIPLY': Key.KEY_MULTIPLY,
    'NUMPAD_ADD': Key.KEY_ADD,
    'NUMPAD_SUBTRACT': Key.KEY_SUBTRACT,
    'NUMPAD_DECIMAL': Key.KEY_DECIMAL,
    'NUMPAD_DIVIDE': Key.KEY_DIVIDE,
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
    'MEDIA_PLAY_PAUSE': Key.KEY_MEDIA_PLAY_PAUSE,
    'MEDIA_PREV_TRACK': Key.KEY_MEDIA_PREV_TRACK,
    'MEDIA_NEXT_TRACK': Key.KEY_MEDIA_NEXT_TRACK,
    'VOLUME_MUTE': Key.KEY_VOLUME_MUTE,
    'VOLUME_UP': Key.KEY_VOLUME_UP,
    'VOLUME_DOWN': Key.KEY_VOLUME_DOWN,
    'MEDIA_STOP': Key.KEY_MEDIA_STOP,
    'BROWSER_BACK': Key.KEY_BROWSER_BACK,
    'BROWSER_FORWARD': Key.KEY_BROWSER_FORWARD,
    'BROWSER_REFRESH': Key.KEY_BROWSER_REFRESH,
}

for letter in 'abcdefghijklmnopqrstuvwxyz':
    STR_TO_KEY[letter.upper()] = STR_TO_KEY[letter]


def str_to_key(key_str: str) -> Key:
    """Convert string key name to Key enum."""
    key_str = key_str.upper()
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
