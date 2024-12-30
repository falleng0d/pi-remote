import app.hid.keycodes as keycodes

from key import Key

# Map from internal key representation to HID keycode and modifier
KEY_TO_KEYCODE = {
    Key.KEY_0: keycodes.KEYCODE_NUMBER_0,
    Key.KEY_1: keycodes.KEYCODE_NUMBER_1,
    Key.KEY_2: keycodes.KEYCODE_NUMBER_2,
    Key.KEY_3: keycodes.KEYCODE_NUMBER_3,
    Key.KEY_4: keycodes.KEYCODE_NUMBER_4,
    Key.KEY_5: keycodes.KEYCODE_NUMBER_5,
    Key.KEY_6: keycodes.KEYCODE_NUMBER_6,
    Key.KEY_7: keycodes.KEYCODE_NUMBER_7,
    Key.KEY_8: keycodes.KEYCODE_NUMBER_8,
    Key.KEY_9: keycodes.KEYCODE_NUMBER_9,
    Key.KEY_A: keycodes.KEYCODE_A,
    Key.KEY_B: keycodes.KEYCODE_B,
    Key.KEY_C: keycodes.KEYCODE_C,
    Key.KEY_D: keycodes.KEYCODE_D,
    Key.KEY_E: keycodes.KEYCODE_E,
    Key.KEY_F: keycodes.KEYCODE_F,
    Key.KEY_G: keycodes.KEYCODE_G,
    Key.KEY_H: keycodes.KEYCODE_H,
    Key.KEY_I: keycodes.KEYCODE_I,
    Key.KEY_J: keycodes.KEYCODE_J,
    Key.KEY_K: keycodes.KEYCODE_K,
    Key.KEY_L: keycodes.KEYCODE_L,
    Key.KEY_M: keycodes.KEYCODE_M,
    Key.KEY_N: keycodes.KEYCODE_N,
    Key.KEY_O: keycodes.KEYCODE_O,
    Key.KEY_P: keycodes.KEYCODE_P,
    Key.KEY_Q: keycodes.KEYCODE_Q,
    Key.KEY_R: keycodes.KEYCODE_R,
    Key.KEY_S: keycodes.KEYCODE_S,
    Key.KEY_T: keycodes.KEYCODE_T,
    Key.KEY_U: keycodes.KEYCODE_U,
    Key.KEY_V: keycodes.KEYCODE_V,
    Key.KEY_W: keycodes.KEYCODE_W,
    Key.KEY_X: keycodes.KEYCODE_X,
    Key.KEY_Y: keycodes.KEYCODE_Y,
    Key.KEY_Z: keycodes.KEYCODE_Z,
    Key.KEY_F1: keycodes.KEYCODE_F1,
    Key.KEY_F2: keycodes.KEYCODE_F2,
    Key.KEY_F3: keycodes.KEYCODE_F3,
    Key.KEY_F4: keycodes.KEYCODE_F4,
    Key.KEY_F5: keycodes.KEYCODE_F5,
    Key.KEY_F6: keycodes.KEYCODE_F6,
    Key.KEY_F7: keycodes.KEYCODE_F7,
    Key.KEY_F8: keycodes.KEYCODE_F8,
    Key.KEY_F9: keycodes.KEYCODE_F9,
    Key.KEY_F10: keycodes.KEYCODE_F10,
    Key.KEY_F11: keycodes.KEYCODE_F11,
    Key.KEY_F12: keycodes.KEYCODE_F12,
    Key.KEY_NUMLOCK: keycodes.KEYCODE_NUM_LOCK,
    Key.KEY_SCROLL: keycodes.KEYCODE_SCROLL_LOCK,
    Key.KEY_BACK: keycodes.KEYCODE_BACKSPACE_DELETE,
    Key.KEY_TAB: keycodes.KEYCODE_TAB,
    Key.KEY_RETURN: keycodes.KEYCODE_ENTER,
    Key.KEY_LSHIFT: keycodes.MODIFIER_LEFT_SHIFT,
    Key.KEY_RSHIFT: keycodes.MODIFIER_RIGHT_SHIFT,
    Key.KEY_LCONTROL: keycodes.MODIFIER_LEFT_CTRL,
    Key.KEY_RCONTROL: keycodes.MODIFIER_RIGHT_CTRL,
    Key.KEY_LMENU: keycodes.MODIFIER_LEFT_ALT,
    Key.KEY_RMENU: keycodes.MODIFIER_RIGHT_ALT,
    Key.KEY_CAPITAL: keycodes.KEYCODE_CAPS_LOCK,
    Key.KEY_ESCAPE: keycodes.KEYCODE_ESCAPE,
    Key.KEY_SPACE: keycodes.KEYCODE_SPACEBAR,
    Key.KEY_PRIOR: keycodes.KEYCODE_PAGE_UP,
    Key.KEY_NEXT: keycodes.KEYCODE_PAGE_DOWN,
    Key.KEY_END: keycodes.KEYCODE_END,
    Key.KEY_HOME: keycodes.KEYCODE_HOME,
    Key.KEY_LEFT: keycodes.KEYCODE_LEFT_ARROW,
    Key.KEY_UP: keycodes.KEYCODE_UP_ARROW,
    Key.KEY_RIGHT: keycodes.KEYCODE_RIGHT_ARROW,
    Key.KEY_DOWN: keycodes.KEYCODE_DOWN_ARROW,
    Key.KEY_PRINT: keycodes.KEYCODE_PRINT_SCREEN,
    Key.KEY_INSERT: keycodes.KEYCODE_INSERT,
    Key.KEY_DELETE: keycodes.KEYCODE_DELETE,
    Key.KEY_LSUPER: keycodes.MODIFIER_LEFT_META,
    Key.KEY_RSUPER: keycodes.MODIFIER_RIGHT_META,
    Key.KEY_NUMPAD0: keycodes.KEYCODE_NUMPAD_0,
    Key.KEY_NUMPAD1: keycodes.KEYCODE_NUMPAD_1,
    Key.KEY_NUMPAD2: keycodes.KEYCODE_NUMPAD_2,
    Key.KEY_NUMPAD3: keycodes.KEYCODE_NUMPAD_3,
    Key.KEY_NUMPAD4: keycodes.KEYCODE_NUMPAD_4,
    Key.KEY_NUMPAD5: keycodes.KEYCODE_NUMPAD_5,
    Key.KEY_NUMPAD6: keycodes.KEYCODE_NUMPAD_6,
    Key.KEY_NUMPAD7: keycodes.KEYCODE_NUMPAD_7,
    Key.KEY_NUMPAD8: keycodes.KEYCODE_NUMPAD_8,
    Key.KEY_NUMPAD9: keycodes.KEYCODE_NUMPAD_9,
    Key.KEY_MULTIPLY: keycodes.KEYCODE_NUMPAD_MULTIPLY,
    Key.KEY_ADD: keycodes.KEYCODE_NUMPAD_PLUS,
    Key.KEY_SUBTRACT: keycodes.KEYCODE_NUMPAD_MINUS,
    Key.KEY_DECIMAL: keycodes.KEYCODE_NUMPAD_DOT,
    Key.KEY_DIVIDE: keycodes.KEYCODE_NUMPAD_DIVIDE,
    Key.KEY_OEM_PLUS: keycodes.KEYCODE_EQUAL_SIGN,
    Key.KEY_OEM_COMMA: keycodes.KEYCODE_COMMA,
    Key.KEY_OEM_MINUS: keycodes.KEYCODE_MINUS,
    Key.KEY_OEM_PERIOD: keycodes.KEYCODE_PERIOD,
    Key.KEY_OEM_1_SEMICOLON: keycodes.KEYCODE_SEMICOLON,
    Key.KEY_OEM_2_FORWARD_SLASH: keycodes.KEYCODE_FORWARD_SLASH,
    Key.KEY_OEM_3_BACKTICK: keycodes.KEYCODE_ACCENT_GRAVE,
    Key.KEY_OEM_4_SQUARE_BRACKET_OPEN: keycodes.KEYCODE_LEFT_BRACKET,
    Key.KEY_OEM_5_BACKSLASH: keycodes.KEYCODE_BACKSLASH,
    Key.KEY_OEM_6_SQUARE_BRACKET_CLOSE: keycodes.KEYCODE_RIGHT_BRACKET,
    Key.KEY_OEM_7_SINGLE_QUOTE: keycodes.KEYCODE_SINGLE_QUOTE,
    Key.KEY_MEDIA_PLAY_PAUSE: keycodes.KEYCODE_MEDIA_PLAY_PAUSE,
    Key.KEY_MEDIA_PREV_TRACK: keycodes.KEYCODE_MEDIA_PREV_TRACK,
    Key.KEY_MEDIA_NEXT_TRACK: keycodes.KEYCODE_MEDIA_NEXT_TRACK,
    Key.KEY_VOLUME_MUTE: keycodes.KEYCODE_VOLUME_MUTE,
    Key.KEY_VOLUME_UP: keycodes.KEYCODE_VOLUME_UP,
    Key.KEY_VOLUME_DOWN: keycodes.KEYCODE_VOLUME_DOWN,
    Key.KEY_BROWSER_REFRESH: keycodes.KEYCODE_REFRESH,
}


def key_to_keycode(key: Key) -> int:
    """Convert internal key representation to HID keycode.

    Args:
            key: Internal key representation from Key enum

    Returns:
            Tuple of keycode for HID USB usage

    Raises:
            KeyError: If key is not found in mapping
    """
    return KEY_TO_KEYCODE[key]


modifier_keys = {
    Key.KEY_LSHIFT,
    Key.KEY_RSHIFT,
    Key.KEY_LCONTROL,
    Key.KEY_RCONTROL,
    Key.KEY_LMENU,
    Key.KEY_RMENU,
    Key.KEY_LSUPER,
    Key.KEY_RSUPER,
}
media_keys = {
    Key.KEY_MEDIA_PLAY_PAUSE,
    Key.KEY_MEDIA_PREV_TRACK,
    Key.KEY_MEDIA_NEXT_TRACK,
    Key.KEY_VOLUME_MUTE,
    Key.KEY_VOLUME_UP,
    Key.KEY_VOLUME_DOWN,
    Key.KEY_MEDIA_STOP,
    Key.KEY_BROWSER_BACK,
    Key.KEY_BROWSER_FORWARD,
    Key.KEY_BROWSER_REFRESH,
}


def is_modifier_key(key: Key) -> bool:
    return key in modifier_keys


def is_media_key(key: Key) -> bool:
    return key in media_keys


if __name__ == '__main__':
    code = key_to_keycode(Key.KEY_MEDIA_PLAY_PAUSE)
    print(f'Key code for media play/pause: {code}')
