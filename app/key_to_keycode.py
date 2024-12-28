import app.hid.keycodes as keycodes
import app.key as key

# Map from internal key representation to HID keycode and modifier
KEY_TO_KEYCODE = {
    key.KEY_0: keycodes.KEYCODE_NUMBER_0,
    key.KEY_1: keycodes.KEYCODE_NUMBER_1,
    key.KEY_2: keycodes.KEYCODE_NUMBER_2,
    key.KEY_3: keycodes.KEYCODE_NUMBER_3,
    key.KEY_4: keycodes.KEYCODE_NUMBER_4,
    key.KEY_5: keycodes.KEYCODE_NUMBER_5,
    key.KEY_6: keycodes.KEYCODE_NUMBER_6,
    key.KEY_7: keycodes.KEYCODE_NUMBER_7,
    key.KEY_8: keycodes.KEYCODE_NUMBER_8,
    key.KEY_9: keycodes.KEYCODE_NUMBER_9,
    key.KEY_A: keycodes.KEYCODE_A,
    key.KEY_B: keycodes.KEYCODE_B,
    key.KEY_C: keycodes.KEYCODE_C,
    key.KEY_D: keycodes.KEYCODE_D,
    key.KEY_E: keycodes.KEYCODE_E,
    key.KEY_F: keycodes.KEYCODE_F,
    key.KEY_G: keycodes.KEYCODE_G,
    key.KEY_H: keycodes.KEYCODE_H,
    key.KEY_I: keycodes.KEYCODE_I,
    key.KEY_J: keycodes.KEYCODE_J,
    key.KEY_K: keycodes.KEYCODE_K,
    key.KEY_L: keycodes.KEYCODE_L,
    key.KEY_M: keycodes.KEYCODE_M,
    key.KEY_N: keycodes.KEYCODE_N,
    key.KEY_O: keycodes.KEYCODE_O,
    key.KEY_P: keycodes.KEYCODE_P,
    key.KEY_Q: keycodes.KEYCODE_Q,
    key.KEY_R: keycodes.KEYCODE_R,
    key.KEY_S: keycodes.KEYCODE_S,
    key.KEY_T: keycodes.KEYCODE_T,
    key.KEY_U: keycodes.KEYCODE_U,
    key.KEY_V: keycodes.KEYCODE_V,
    key.KEY_W: keycodes.KEYCODE_W,
    key.KEY_X: keycodes.KEYCODE_X,
    key.KEY_Y: keycodes.KEYCODE_Y,
    key.KEY_Z: keycodes.KEYCODE_Z,
    key.KEY_F1: keycodes.KEYCODE_F1,
    key.KEY_F2: keycodes.KEYCODE_F2,
    key.KEY_F3: keycodes.KEYCODE_F3,
    key.KEY_F4: keycodes.KEYCODE_F4,
    key.KEY_F5: keycodes.KEYCODE_F5,
    key.KEY_F6: keycodes.KEYCODE_F6,
    key.KEY_F7: keycodes.KEYCODE_F7,
    key.KEY_F8: keycodes.KEYCODE_F8,
    key.KEY_F9: keycodes.KEYCODE_F9,
    key.KEY_F10: keycodes.KEYCODE_F10,
    key.KEY_F11: keycodes.KEYCODE_F11,
    key.KEY_F12: keycodes.KEYCODE_F12,
    key.KEY_NUMLOCK: keycodes.KEYCODE_NUM_LOCK,
    key.KEY_SCROLL: keycodes.KEYCODE_SCROLL_LOCK,
    key.KEY_BACK: keycodes.KEYCODE_BACKSPACE_DELETE,
    key.KEY_TAB: keycodes.KEYCODE_TAB,
    key.KEY_RETURN: keycodes.KEYCODE_ENTER,
    key.KEY_LSHIFT: keycodes.MODIFIER_LEFT_SHIFT,
    key.KEY_RSHIFT: keycodes.MODIFIER_RIGHT_SHIFT,
    key.KEY_LCONTROL: keycodes.MODIFIER_LEFT_CTRL,
    key.KEY_RCONTROL: keycodes.MODIFIER_RIGHT_CTRL,
    key.KEY_LMENU: keycodes.MODIFIER_LEFT_ALT,
    key.KEY_RMENU: keycodes.MODIFIER_RIGHT_ALT,
    key.KEY_CAPITAL: keycodes.KEYCODE_CAPS_LOCK,
    key.KEY_ESCAPE: keycodes.KEYCODE_ESCAPE,
    key.KEY_SPACE: keycodes.KEYCODE_SPACEBAR,
    key.KEY_PRIOR: keycodes.KEYCODE_PAGE_UP,
    key.KEY_NEXT: keycodes.KEYCODE_PAGE_DOWN,
    key.KEY_END: keycodes.KEYCODE_END,
    key.KEY_HOME: keycodes.KEYCODE_HOME,
    key.KEY_LEFT: keycodes.KEYCODE_LEFT_ARROW,
    key.KEY_UP: keycodes.KEYCODE_UP_ARROW,
    key.KEY_RIGHT: keycodes.KEYCODE_RIGHT_ARROW,
    key.KEY_DOWN: keycodes.KEYCODE_DOWN_ARROW,
    key.KEY_PRINT: keycodes.KEYCODE_PRINT_SCREEN,
    key.KEY_INSERT: keycodes.KEYCODE_INSERT,
    key.KEY_DELETE: keycodes.KEYCODE_DELETE,
    key.KEY_LSUPER: keycodes.MODIFIER_LEFT_META,
    key.KEY_RSUPER: keycodes.MODIFIER_RIGHT_META,
    # Numpad keys
    key.KEY_NUMPAD0: keycodes.KEYCODE_NUMPAD_0,
    key.KEY_NUMPAD1: keycodes.KEYCODE_NUMPAD_1,
    key.KEY_NUMPAD2: keycodes.KEYCODE_NUMPAD_2,
    key.KEY_NUMPAD3: keycodes.KEYCODE_NUMPAD_3,
    key.KEY_NUMPAD4: keycodes.KEYCODE_NUMPAD_4,
    key.KEY_NUMPAD5: keycodes.KEYCODE_NUMPAD_5,
    key.KEY_NUMPAD6: keycodes.KEYCODE_NUMPAD_6,
    key.KEY_NUMPAD7: keycodes.KEYCODE_NUMPAD_7,
    key.KEY_NUMPAD8: keycodes.KEYCODE_NUMPAD_8,
    key.KEY_NUMPAD9: keycodes.KEYCODE_NUMPAD_9,
    key.KEY_MULTIPLY: keycodes.KEYCODE_NUMPAD_MULTIPLY,
    key.KEY_ADD: keycodes.KEYCODE_NUMPAD_PLUS,
    key.KEY_SUBTRACT: keycodes.KEYCODE_NUMPAD_MINUS,
}


def key_to_keycode(key: int) -> int:
    """Convert internal key representation to HID keycode.

    Args:
            key: Internal key representation from key

    Returns:
            Tuple of keycode for HID USB usage

    Raises:
            KeyError: If key is not found in mapping
    """
    return KEY_TO_KEYCODE[key]
