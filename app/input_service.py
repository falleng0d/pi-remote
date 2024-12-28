from hid.keyboard import send_keystroke
from request_parsers.keystroke import Keystroke


class InputService:
    keyboard_path: str

    def __init__(self, keyboard_path: str):
        self.keyboard_path = keyboard_path

    async def press_key(self, key: Keystroke):
        send_keystroke(self.keyboard_path, key)
