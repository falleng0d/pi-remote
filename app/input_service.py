import logging
import time
from typing import BinaryIO
from typing import Iterable

from config_service import ConfigService
from hid import keycodes
from hid.keycodes import modifier_keycodes
from key import Key
from key import KeyActionType
from key import KeyOptions
from key_utils import is_media_key
from key_utils import is_modifier_key
from key_utils import key_to_keycode


def _write_to_hid_handle(hid_handle: BinaryIO, buffer: Iterable[int]):
    try:
        hid_handle.write(bytearray(buffer))
    except BlockingIOError:
        logging.error('Failed to write to HID interface. Is USB cable connected?')


def _write_to_hid(hid_path: str, buffer: Iterable[int]):
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


def release_all_keys(keyboard_path: str):
    _write_to_hid(keyboard_path, [0] * 8)


class HidKeyboardService:
    """Service for sending input events to the target machine over USB HID."""

    keyboard_path: str
    media_path: str
    _logger: logging.Logger
    _pressed_keys: tuple[int, ...]
    _active_modifiers: dict[int, bool]
    _modifiers_byte: int

    def _send_key_hid_state(self):
        _write_to_hid(
            self.keyboard_path, (self._modifiers_byte, 0, *self._pressed_keys)
        )

    def _send_media_hid_state(self, media_key: int):
        _write_to_hid(self.media_path, (media_key, 0))

    def __init__(self, keyboard_path: str, media_path: str, logger: logging.Logger):
        self.keyboard_path = keyboard_path
        self.media_path = media_path
        self._logger = logger
        self._pressed_keys = (0, 0, 0, 0, 0, 0)
        self._modifiers_byte = 0
        self._active_modifiers = {
            keycodes.MODIFIER_LEFT_CTRL: False,
            keycodes.MODIFIER_LEFT_SHIFT: False,
            keycodes.MODIFIER_LEFT_ALT: False,
            keycodes.MODIFIER_LEFT_META: False,
            keycodes.MODIFIER_RIGHT_CTRL: False,
            keycodes.MODIFIER_RIGHT_SHIFT: False,
            keycodes.MODIFIER_RIGHT_ALT: False,
            keycodes.MODIFIER_RIGHT_META: False,
        }

    def _recalculate_modifiers_byte(self):
        modifier_bitmask = 0

        for modifier, value in self._active_modifiers.items():
            if value:
                modifier_bitmask |= modifier

        self._modifiers_byte = modifier_bitmask

    def _set_modifier_state(self, modifier: int, state: bool):
        if modifier not in self._active_modifiers:
            raise ValueError(f'Key {modifier} is not a modifier key')

        self._active_modifiers[modifier] = state
        self._recalculate_modifiers_byte()

    def _set_key_state(self, keyCode: int, state: bool):
        if state and keyCode not in self._pressed_keys:
            try:
                free_index = self._pressed_keys.index(0)
                self._pressed_keys = tuple(
                    keyCode if i == free_index else k
                    for i, k in enumerate(self._pressed_keys)
                )
            except ValueError:
                raise ValueError('Cannot press more than 6 keys at once')
        else:
            self._pressed_keys = tuple(
                0 if k == keyCode else k for k in self._pressed_keys
            )

    def is_modifier(self, keyCode: int) -> bool:
        return keyCode in modifier_keycodes

    def is_modifier_pressed(self, keyCode: int) -> bool:
        return keyCode in self._active_modifiers

    def is_key_pressed(self, keyCode: int) -> bool:
        return keyCode in self._pressed_keys[2:]

    def send_key_state(self, keyCode: int, action: KeyActionType):
        self._set_key_state(keyCode, True if action == KeyActionType.DOWN else False)
        self._send_key_hid_state()

    def send_key_press(self, keyCode: int, interval: int = 30):
        self.send_key_state(keyCode, KeyActionType.DOWN)
        time.sleep(interval / 1000)
        self.send_key_state(keyCode, KeyActionType.UP)

    def send_media_key_state(self, keyCode: int, action: KeyActionType):
        self._send_media_hid_state(keyCode if action == KeyActionType.DOWN else 0)

    def send_media_key_press(self, keyCode: int, interval: int = 30):
        self._send_media_hid_state(keyCode)
        time.sleep(interval / 1000)
        self._send_media_hid_state(0)

    def send_modifier_state(self, modifier: int, action: KeyActionType):
        if not self.is_modifier(modifier):
            raise ValueError(f'Key {modifier} is not a modifier key')

        self._set_modifier_state(
            modifier, True if action == KeyActionType.DOWN else False
        )

        self._send_key_hid_state()

    def send_modifier_press(self, modifier: int, interval: int = 30):
        if not self.is_modifier(modifier):
            raise ValueError(f'Key {modifier} is not a modifier key')

        self.send_modifier_state(modifier, KeyActionType.DOWN)
        time.sleep(interval / 1000)
        self.send_modifier_state(modifier, KeyActionType.UP)

    def unpress_all_keys(self):
        self._pressed_keys = (0, 0, 0, 0, 0, 0, 0, 0)

        for modifier in self._active_modifiers:
            self._active_modifiers[modifier] = False

        self._recalculate_modifiers_byte()
        self._send_key_hid_state()
        self._send_media_hid_state(0)


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

    def _press_media_key(self, key_code: int, action_type: KeyActionType):
        if action_type == KeyActionType.PRESS:
            self._kb_service.send_media_key_press(
                key_code, self._config_service.key_press_interval
            )
        else:
            self._kb_service.send_media_key_state(key_code, action_type)

    def press_key(self, key: Key, action_type: KeyActionType, options: KeyOptions):
        key_code = key_to_keycode(key)
        self._logger.info(
            f'Pressing {action_type.name} {key.name}({key_code}) {options}'
        )
        if is_modifier_key(key):
            self._kb_service.send_modifier_state(key_code, action_type)
        elif is_media_key(key):
            self._press_media_key(key_code, action_type)
        else:
            self._press_key(key_code, action_type, options)
