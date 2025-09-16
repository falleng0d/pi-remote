import contextlib
import logging
import multiprocessing
import time
from math import floor
from typing import BinaryIO, Iterable, Callable, Optional
from acceleration_curves import linear, ease_out_quad

import execute
from button import Button
from button import button_to_hid
from config_service import ConfigService
from hid import keycodes
from hid.keycodes import modifier_keycodes
from key import ButtonActionType
from key import HotkeyOptions
from key import Key
from key import KeyActionType
from key import KeyOptions
from key_utils import is_media_key
from key_utils import is_modifier_key
from key_utils import key_to_keycode

_hid_lock = multiprocessing.Lock()

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
        with _hid_lock:
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
        _write_to_hid(self.keyboard_path, (self._modifiers_byte, 0, *self._pressed_keys))

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
            except ValueError as e:
                raise ValueError('Cannot press more than 6 keys at once') from e
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
        self._set_key_state(keyCode, action == KeyActionType.DOWN)
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

        self._set_modifier_state(modifier, action == KeyActionType.DOWN)

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


def _send_mouse_event(mouse_path: str, buffer: Iterable[int]):
    try:
        _write_to_hid(mouse_path, buffer)
    except (BrokenPipeError, ValueError) as e:
        logging.info(f'Failed to write mouse report {[f"{x:#04x}" for x in buffer]}')
        
        raise RuntimeError(f'Failed to write mouse report {[f"{x:#04x}" for x in buffer]}') from e


def send_mouse_event(
    mouse_path: str,
    buttons: int,
    relative_x: float,
    relative_y: float,
    vertical_wheel_delta: int,
    horizontal_wheel_delta: int,
) -> None:
    """Send a mouse event to the target machine over USB HID.

    :param mouse_path: A bitmask representing which mouse buttons are pressed.
    :param buttons: A bitmask representing which mouse buttons are pressed.
    :param relative_x: A value representing mouse's relative y delta.
    :param relative_y: A value representing mouse's relative y delta.
    :param vertical_wheel_delta: A -1, 0, or 1 representing movement of the mouse's
        horizontal scroll wheel.
    :param horizontal_wheel_delta:
    :return: None
    """
    # pylint: disable=invalid-name
    x, y = floor(relative_x * 10), floor(relative_y * 10)

    buf = [0] * 5
    buf[0] = buttons  # Byte 0 = Button 1 pressed
    buf[1] = x & 0xFF
    buf[2] = y & 0xFF
    buf[3] = _translate_vertical_wheel_delta(vertical_wheel_delta) & 0xFF
    buf[4] = horizontal_wheel_delta & 0xFF

    # logging.info(f'Sending packet to mouse: {[f" {x:#04x}" for x in buf]}')

    execute.with_timeout_t(
        _write_to_hid,
        args=(mouse_path, buf),
        timeout_in_seconds=0.005,
    )


def _translate_vertical_wheel_delta(vertical_wheel_delta: int) -> int:
    # a negative wheel delta number indicates upward scrolling but in HID, negative means
    # downward scrolling.
    return vertical_wheel_delta * -1


class HidMouseService:
    """Service for sending input events to the target machine over USB HID.

    Keeps track of the state of the buttons and sends the appropriate events.
    """

    mouse_path: str
    _logger: logging.Logger
    _button_state: int
    _config_service: ConfigService

    def __init__(self, config_service: ConfigService, mouse_path: str, logger: logging.Logger):
        self.mouse_path = mouse_path
        self._logger = logger
        self._button_state = 0
        self._config_service = config_service

    def _write_to_hid(self):
        # Send event with current button state but no movement/scroll
        send_mouse_event(
            self.mouse_path,
            self._button_state,  # Current button state
            0.0,  # No X movement
            0.0,  # No Y movement
            0,  # No vertical scroll
            0,  # No horizontal scroll
        )

    def send_button_state(self, button: Button, action: ButtonActionType):
        """Update button state and send the mouse event."""
        button_mask = button_to_hid(button)

        if action == ButtonActionType.DOWN:
            self._button_state |= button_mask
        elif action == ButtonActionType.UP:
            self._button_state &= ~button_mask
        elif action == ButtonActionType.MOVE:
            self.send_button_press(button)

        self._write_to_hid()

    def send_button_press(self, button: Button):
        """Send a mouse button press event."""
        self.send_button_state(button, ButtonActionType.DOWN)
        time.sleep(0.15)
        self.send_button_state(button, ButtonActionType.UP)

    def send_movement(self, delta_x: float, delta_y: float):
        """Send a mouse movement event."""
        send_mouse_event(
            self.mouse_path,
            self._button_state,  # Keep current button state
            delta_x,
            delta_y,
            0,  # No vertical scroll
            0,  # No horizontal scroll
        )

    def release_all_buttons(self):
        """Release all mouse buttons."""
        self._button_state = 0
        self._write_to_hid()


class InputService:
    """Service for orchestrating input events."""

    _logger: logging.Logger
    _kb_service: HidKeyboardService
    _mouse_service: HidMouseService
    _config_service: ConfigService

    def __init__(
        self,
        hid_service: HidKeyboardService,
        mouse_service: HidMouseService,
        config_service: ConfigService,
        logger: logging.Logger,
    ):
        self._kb_service = hid_service
        self._mouse_service = mouse_service
        self._config_service = config_service
        self._logger = logger

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

    def move_mouse(self, delta_x: float, delta_y: float):
        self._logger.debug(f'Moving mouse by {delta_x}, {delta_y}')
        self._mouse_service.send_movement(delta_x, delta_y)

    def press_mouse_key(self, button: Button, action_type: ButtonActionType):
        self._logger.debug(f'Pressing mouse {action_type.name} {button.name}')
        self._mouse_service.send_button_state(button, action_type)

    def press_hotkey(
        self, hotkey_steps, action_type: KeyActionType, options: HotkeyOptions
    ):
        self._logger.info(
            f'Processing hotkey with {len(hotkey_steps)} steps, action: {action_type.name}'
        )

        if action_type == KeyActionType.UP:
            return

        # Default speed if not specified
        default_speed = (
            options.speed
            if options and options.speed is not None
            else self._config_service.key_press_interval
        )

        # Process each step in the sequence
        for step in hotkey_steps:
            key_code = step.key_code
            step_action = step.action_type

            if step.wait:
                time.sleep(step.wait / 1000)

            key = Key(key_code)

            # Use step-specific speed or default
            speed = step.speed if step.speed is not None else default_speed

            key_options = KeyOptions(
                no_repeat=True,
                disable_unwanted_modifiers=options.disable_unwanted_modifiers if options else False
            )

            self.press_key(key, step_action, key_options)

            if step_action == KeyActionType.PRESS:
                time.sleep(speed / 1000)
