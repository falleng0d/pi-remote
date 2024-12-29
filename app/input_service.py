import logging
import time
from typing import BinaryIO
from typing import List

from config_service import ConfigService
from hid.keycodes import modifier_keys
from key import KeyActionType
from key import KeyOptions
from key import is_modifier_key
from key_to_keycode import key_to_keycode


def _write_to_hid_handle(hid_handle: BinaryIO, buffer: list[int]):
    try:
        hid_handle.write(bytearray(buffer))
    except BlockingIOError:
        logging.error('Failed to write to HID interface. Is USB cable connected?')


def _write_to_hid(hid_path: str, buffer: list[int]):
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        logging.debug(
            'writing to HID interface %s: %s',
            hid_path,
            ' '.join([f'{x:#04x}' for x in buffer]),
        )

    try:
        with open(hid_path, 'ab+') as hid_handle:
            hid_handle.write(bytearray(buffer))
    except BlockingIOError:
        logging.error(
            'Failed to write to HID interface: %s. Is USB cable connected?', hid_path
        )


def send_hid_state(hid_path: str, pressed_keys: List[int], modifiers_bitmask: int):
    """Sends pressed keys and active modifiers to the HID interface.

    - Up to 6 keys can be pressed at once.
    - Modifiers are sent in the first byte of the buffer
    - The second byte of the buffer is always 0.
    - From the third byte onwards, the buffer contains the keycodes of the keys
    """
    if len(pressed_keys) > 6:
        raise ValueError('Cannot send more than 6 keys at once')

    buf = [0] * 8
    buf[0] = modifiers_bitmask
    for i, key_code in enumerate(pressed_keys):
        buf[i + 2] = key_code

    _write_to_hid(hid_path, buf)


def release_all_keys(keyboard_path: str):
    _write_to_hid(keyboard_path, [0] * 8)


class HidKeyboardService:
    """Service for sending input events to the target machine over USB HID."""

    keyboard_path: str
    _logger: logging.Logger
    _pressed_keys: List[int]
    _active_modifiers: List[int]

    def _send_hid_state(self):
        send_hid_state(
            self.keyboard_path, self._pressed_keys, self._get_modifiers_bitmap()
        )

    def __init__(self, keyboard_path: str, logger: logging.Logger):
        self.keyboard_path = keyboard_path
        self._logger = logger
        self._pressed_keys = []
        self._active_modifiers = []

    def _get_modifiers_bitmap(self) -> int:
        modifier_bitmask = 0

        for modifier in self._active_modifiers:
            modifier_bitmask |= modifier

        return modifier_bitmask

    def is_modifier(self, keyCode: int) -> bool:
        return keyCode in modifier_keys

    def is_modifier_pressed(self, keyCode: int) -> bool:
        return keyCode in self._active_modifiers

    def is_key_pressed(self, keyCode: int) -> bool:
        return keyCode in self._pressed_keys

    def send_key_state(self, keyCode: int, action: KeyActionType):
        if action == KeyActionType.DOWN and not self.is_key_pressed(keyCode):
            self._pressed_keys.append(keyCode)
            self._send_hid_state()
        elif action == KeyActionType.UP and self.is_key_pressed(keyCode):
            self._pressed_keys.remove(keyCode)
            self._send_hid_state()

    def send_key_press(self, keyCode: int, interval: int = 30):
        self.send_key_state(keyCode, KeyActionType.DOWN)
        time.sleep(interval / 1000)
        self.send_key_state(keyCode, KeyActionType.UP)

    def send_modifier_state(self, modifier: int, action: KeyActionType):
        if not self.is_modifier(modifier):
            raise ValueError(f'Key {modifier} is not a modifier key')

        if action == KeyActionType.DOWN:
            self._active_modifiers.append(modifier)
            self._send_hid_state()
        else:
            self._active_modifiers.remove(modifier)

        self._send_hid_state()

    def send_modifier_press(self, modifier: int, interval: int = 30):
        if not self.is_modifier(modifier):
            raise ValueError(f'Key {modifier} is not a modifier key')

        self.send_modifier_state(modifier, KeyActionType.DOWN)
        time.sleep(interval / 1000)
        self.send_modifier_state(modifier, KeyActionType.UP)

    def unpress_all_keys(self):
        self._pressed_keys = []
        self._active_modifiers = []

        release_all_keys(self.keyboard_path)


class InputService:
    """Service for orchestrating input events."""

    _logger: logging.Logger
    _kb_service: HidKeyboardService
    _config_service: ConfigService

    def __init__(self, hid_service: HidKeyboardService, logger: logging.Logger):
        self._logger = logger
        self._kb_service = hid_service
        self._kb_service.unpress_all_keys()

    def _press_key(self, key_code: int, action_type: KeyActionType, _: KeyOptions):
        if action_type == KeyActionType.PRESS:
            self._kb_service.send_key_press(
                key_code, self._config_service.key_press_interval
            )
        else:
            self._kb_service.send_key_state(key_code, action_type)

    def _press_modifier(self, key_code: int, action_type: KeyActionType):
        if action_type == KeyActionType.PRESS:
            self._kb_service.send_modifier_press(
                key_code, self._config_service.key_press_interval
            )
        else:
            self._kb_service.send_modifier_state(key_code, action_type)

    def press_key(self, key_id: int, action_type: KeyActionType, options: KeyOptions):
        key_code = key_to_keycode(key_id)
        if is_modifier_key(key_id):
            self._logger.info(
                f'Pressing MODIFIER {key_id}->{key_code} {action_type.name} {options}'
            )
            self._kb_service.send_modifier_state(key_code, action_type)
        else:
            self._logger.info(
                f'Pressing KEY {key_id}->{key_code} {action_type.name} {options}'
            )
            self._press_key(key_code, action_type, options)
