from enum import Enum


class Button(Enum):
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2
    FORWARD = 3
    BACK = 4


MOUSE_LEFT = 1 << 0
MOUSE_RIGHT = 1 << 1
MOUSE_MIDDLE = 1 << 2
MOUSE_BACK = 1 << 3
MOUSE_FORWARD = 1 << 4

BUTTON_TO_HID = {
    Button.LEFT: MOUSE_LEFT,
    Button.RIGHT: MOUSE_RIGHT,
    Button.MIDDLE: MOUSE_MIDDLE,
    Button.FORWARD: MOUSE_FORWARD,
    Button.BACK: MOUSE_BACK,
}


def button_to_hid(button):
    return BUTTON_TO_HID[button]
