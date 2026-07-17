import json
import logging
import multiprocessing
import shlex
import subprocess
from typing import NoReturn
from collections.abc import Iterable


KEYBOARD_PAGE = 0x07
CONSUMER_PAGE = 0x0C

_hid_lock = multiprocessing.Lock()


class InputBackend:
    def send_keyboard_report(self, modifiers: int, keys: tuple[int, ...]) -> None:
        raise NotImplementedError

    def send_consumer_report(self, usage: int) -> None:
        raise NotImplementedError

    def send_mouse_report(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class UsbGadgetBackend(InputBackend):
    def __init__(
        self,
        keyboard_path: str,
        mouse_path: str,
        media_path: str,
        logger: logging.Logger,
    ):
        self.keyboard_path = keyboard_path
        self.mouse_path = mouse_path
        self.media_path = media_path
        self._logger = logger

    def _write_to_hid(self, hid_path: str, buffer: Iterable[int]) -> None:
        if self._logger.getEffectiveLevel() == logging.DEBUG:
            self._logger.debug(
                'writing to HID interface %s: %s',
                hid_path,
                ' '.join([f'{x:#04x}' for x in buffer]),
            )

        try:
            with _hid_lock:
                with open(hid_path, 'ab+') as hid_handle:
                    hid_handle.write(bytearray(buffer))
        except BlockingIOError:
            self._logger.error(
                'Failed to write to HID interface: %s. Is USB cable connected?', hid_path
            )

    def send_keyboard_report(self, modifiers: int, keys: tuple[int, ...]) -> None:
        self._write_to_hid(self.keyboard_path, (modifiers, 0, *keys))

    def send_consumer_report(self, usage: int) -> None:
        self._write_to_hid(self.media_path, (usage & 0xFF, usage >> 8))

    def send_mouse_report(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        self._write_to_hid(
            self.mouse_path,
            (
                buttons,
                x & 0xFF,
                y & 0xFF,
                vertical_wheel & 0xFF,
                horizontal_wheel & 0xFF,
            ),
        )

    def close(self) -> None:
        pass


class KarabinerBackend(InputBackend):
    def __init__(
        self,
        helper_command: str,
        logger: logging.Logger,
        device_hash: int = 0,
    ):
        if not helper_command:
            raise ValueError('karabiner_helper_command must be set')

        self._logger = logger
        self._device_hash = device_hash
        self._process = subprocess.Popen(
            shlex.split(helper_command),
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._keys_down: set[int] = set()
        self._modifiers_down = 0
        self._consumer_down = 0

    def _send(self, message: dict[str, object]) -> None:
        stdin = self._process.stdin
        if stdin is None or self._process.poll() is not None:
            self._raise_helper_not_running()

        try:
            stdin.write(json.dumps(message, separators=(',', ':')) + '\n')
            stdin.flush()
        except BrokenPipeError:
            self._raise_helper_not_running()

    def _raise_helper_not_running(self) -> NoReturn:
        detail = self._process.stderr.read().strip() if self._process.stderr else ''
        if detail:
            raise RuntimeError(f'Karabiner helper is not running: {detail}')
        raise RuntimeError('Karabiner helper is not running')

    def _send_key_event(self, page: int, code: int, value: int) -> None:
        self._send(
            {
                'type': 'key',
                'page': page,
                'code': code,
                'value': value,
                'device_hash': self._device_hash,
            }
        )

    def _set_consumer_key(self, usage: int, value: int) -> None:
        self._send_key_event(CONSUMER_PAGE, usage, value)

    def send_keyboard_report(self, modifiers: int, keys: tuple[int, ...]) -> None:
        previous_keys = self._keys_down
        next_keys = {key for key in keys if key}

        changed_modifiers = self._modifiers_down ^ modifiers
        for bit in range(8):
            modifier = 1 << bit
            if changed_modifiers & modifier:
                self._send_key_event(
                    KEYBOARD_PAGE,
                    0xE0 + bit,
                    1 if modifiers & modifier else 0,
                )

        for key in previous_keys - next_keys:
            self._send_key_event(KEYBOARD_PAGE, key, 0)
        for key in next_keys - previous_keys:
            self._send_key_event(KEYBOARD_PAGE, key, 1)

        self._modifiers_down = modifiers
        self._keys_down = next_keys

    def send_consumer_report(self, usage: int) -> None:
        if self._consumer_down and self._consumer_down != usage:
            self._set_consumer_key(self._consumer_down, 0)
            self._consumer_down = 0
        if usage and usage != self._consumer_down:
            self._set_consumer_key(usage, 1)
            self._consumer_down = usage
        elif not usage and self._consumer_down:
            self._set_consumer_key(self._consumer_down, 0)
            self._consumer_down = 0

    def send_mouse_report(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        self._send(
            {
                'type': 'mouse',
                'buttons': buttons,
                'x': x,
                'y': y,
                'vertical_wheel': vertical_wheel,
                'horizontal_wheel': horizontal_wheel,
                'device_hash': self._device_hash,
            }
        )

    def close(self) -> None:
        if self._process.stdin is not None:
            self._process.stdin.close()
        self._process.terminate()
