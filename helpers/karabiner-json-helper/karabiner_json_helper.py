#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import BinaryIO

DEFAULT_SOCKET_PATH = (
    '/Library/Application Support/org.pqrs/tmp/rootonly/'
    'karabiner_virtual_hid_device_service.sock'
)
DATAGRAM_SOCKET_DIR = '/Library/Application Support/org.pqrs/tmp/rootonly/vhidd_server'
DATAGRAM_SOCKET_PATH = (
    '/Library/Application Support/org.pqrs/tmp/rootonly/'
    'virtual_hid_device_service_server.sock'
)
DATAGRAM_CLIENT_DIR = '/Library/Application Support/org.pqrs/tmp/rootonly/vhidd_client'
CLIENT_PROTOCOL_VERSION = 7
DATAGRAM_CLIENT_PROTOCOL_VERSION = 5
DEFAULT_VENDOR_ID = 0x16C0
DEFAULT_PRODUCT_ID = 0x27DB
KEYBOARD_PAGE = 0x07
CONSUMER_PAGE = 0x0C
MAX_KEYS = 32
HEARTBEAT_INTERVAL_SECONDS = 3.0
CONNECT_TIMEOUT_SECONDS = 10.0
CONNECT_RETRY_INTERVAL_SECONDS = 0.2
LOCAL_DATAGRAM_USER_DATA = 1
LOCAL_DATAGRAM_HEARTBEAT = 0
LOCAL_DATAGRAM_HEARTBEAT_DEADLINE_MS = 5000


class MessageType(IntEnum):
    HEARTBEAT = 0
    USER_DATA = 1
    HEALTH_CHECK = 2
    HEALTH_CHECK_RESPONSE = 3
    REQUEST = 4
    RESPONSE = 5


class RequestType(IntEnum):
    VIRTUAL_HID_KEYBOARD_INITIALIZE = 0
    VIRTUAL_HID_KEYBOARD_TERMINATE = 1
    VIRTUAL_HID_KEYBOARD_RESET = 2
    VIRTUAL_HID_POINTING_INITIALIZE = 3
    VIRTUAL_HID_POINTING_TERMINATE = 4
    VIRTUAL_HID_POINTING_RESET = 5
    POST_KEYBOARD_INPUT_REPORT = 6
    POST_CONSUMER_INPUT_REPORT = 7
    POST_APPLE_VENDOR_KEYBOARD_INPUT_REPORT = 8
    POST_APPLE_VENDOR_TOP_CASE_INPUT_REPORT = 9
    POST_GENERIC_DESKTOP_INPUT_REPORT = 10
    POST_POINTING_INPUT_REPORT = 11


class DatagramRequestType(IntEnum):
    VIRTUAL_HID_KEYBOARD_INITIALIZE = 1
    VIRTUAL_HID_KEYBOARD_TERMINATE = 2
    VIRTUAL_HID_POINTING_INITIALIZE = 4
    VIRTUAL_HID_POINTING_TERMINATE = 5
    POST_KEYBOARD_INPUT_REPORT = 7
    POST_CONSUMER_INPUT_REPORT = 8
    POST_POINTING_INPUT_REPORT = 12


class DatagramResponseType(IntEnum):
    VIRTUAL_HID_KEYBOARD_READY = 4
    VIRTUAL_HID_POINTING_READY = 5


@dataclass
class PendingResponse:
    event: threading.Event = field(default_factory=threading.Event)
    payload: bytes = b''


def _read_exact(source: BinaryIO | socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        if isinstance(source, socket.socket):
            chunk = source.recv(remaining)
        else:
            chunk = source.read(remaining)
        if not chunk:
            raise EOFError('connection closed')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def encode_frame(message_type: MessageType, payload: bytes = b'') -> bytes:
    body = bytes([message_type]) + payload
    return struct.pack('>I', len(body)) + body


def encode_request_frame(request_id: int, payload: bytes) -> bytes:
    return encode_frame(MessageType.REQUEST, struct.pack('>Q', request_id) + payload)


def encode_response_frame(request_id: int, payload: bytes = b'') -> bytes:
    return encode_frame(MessageType.RESPONSE, struct.pack('>Q', request_id) + payload)


def read_frame(source: BinaryIO | socket.socket) -> tuple[MessageType, bytes]:
    body_size = struct.unpack('>I', _read_exact(source, 4))[0]
    if body_size < 1:
        raise ValueError('invalid empty frame body')
    body = _read_exact(source, body_size)
    return MessageType(body[0]), body[1:]


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0


def find_datagram_socket_path() -> str | None:
    fixed_socket = Path(DATAGRAM_SOCKET_PATH)
    if fixed_socket.exists():
        return str(fixed_socket)
    candidates = sorted(Path(DATAGRAM_SOCKET_DIR).glob('*.sock'), key=_mtime)
    return str(candidates[-1]) if candidates else None


def is_datagram_socket_path(socket_path: str) -> bool:
    return '/vhidd_server/' in socket_path or socket_path == DATAGRAM_SOCKET_PATH


def connect_socket(socket_path: str) -> socket.socket:
    deadline = time.monotonic() + CONNECT_TIMEOUT_SECONDS
    while True:
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            connection.connect(socket_path)
            return connection
        except (FileNotFoundError, ConnectionRefusedError):
            connection.close()
            if time.monotonic() >= deadline:
                raise
            time.sleep(CONNECT_RETRY_INTERVAL_SECONDS)
        except Exception:
            connection.close()
            raise


def request_payload(request_type: RequestType, payload: bytes = b'') -> bytes:
    return struct.pack('<HB', CLIENT_PROTOCOL_VERSION, request_type) + payload


def datagram_request_payload(request_type: DatagramRequestType, payload: bytes = b'') -> bytes:
    return b'cp' + struct.pack('<HB', DATAGRAM_CLIENT_PROTOCOL_VERSION, request_type) + payload


def keyboard_parameters(country_code: int) -> bytes:
    return struct.pack('<QQQ', DEFAULT_VENDOR_ID, DEFAULT_PRODUCT_ID, country_code)


def keys_payload(keys: set[int]) -> bytes:
    ordered_keys = sorted(keys)
    if len(ordered_keys) > MAX_KEYS:
        raise ValueError(f'cannot press more than {MAX_KEYS} keys on this page')
    return struct.pack('<32H', *(ordered_keys + [0] * (MAX_KEYS - len(ordered_keys))))


def keyboard_report(modifiers: int, keys: set[int]) -> bytes:
    return struct.pack('<BBB', 1, modifiers & 0xFF, 0) + keys_payload(keys)


def consumer_report(keys: set[int]) -> bytes:
    return struct.pack('<B', 2) + keys_payload(keys)


def signed_byte(value: int) -> int:
    return max(-128, min(127, value)) & 0xFF


def pointing_report(
    buttons: int,
    x: int,
    y: int,
    vertical_wheel: int,
    horizontal_wheel: int,
) -> bytes:
    return struct.pack(
        '<IBBBB',
        buttons & 0xFFFFFFFF,
        signed_byte(x),
        signed_byte(y),
        signed_byte(vertical_wheel),
        signed_byte(horizontal_wheel),
    )


class DryRunClient:
    def __init__(self):
        self.messages: list[dict[str, int | str]] = []

    def start(self) -> None:
        pass

    def close(self) -> None:
        pass

    def send_key(self, page: int, code: int, value: int) -> None:
        validate_key(page, code, value)
        self.messages.append({'type': 'key', 'page': page, 'code': code, 'value': value})

    def send_mouse(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        validate_mouse(buttons)
        self.messages.append(
            {
                'type': 'mouse',
                'buttons': buttons,
                'x': x,
                'y': y,
                'vertical_wheel': vertical_wheel,
                'horizontal_wheel': horizontal_wheel,
            }
        )


class KarabinerVirtualHIDClient:
    def __init__(self, socket_path: str, country_code: int):
        self._socket_path = socket_path
        self._country_code = country_code
        self._socket: socket.socket | None = None
        self._reader_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._write_lock = threading.Lock()
        self._pending_lock = threading.Lock()
        self._pending: dict[int, PendingResponse] = {}
        self._next_request_id = 1
        self._closed = threading.Event()
        self._modifiers = 0
        self._keyboard_keys: set[int] = set()
        self._consumer_keys: set[int] = set()

    def start(self) -> None:
        self._socket = connect_socket(self._socket_path)
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        self._send_request(
            RequestType.VIRTUAL_HID_KEYBOARD_INITIALIZE,
            keyboard_parameters(self._country_code),
        )
        self._send_request(RequestType.VIRTUAL_HID_POINTING_INITIALIZE)

    def close(self) -> None:
        if self._socket is not None:
            for request_type in (
                RequestType.VIRTUAL_HID_KEYBOARD_TERMINATE,
                RequestType.VIRTUAL_HID_POINTING_TERMINATE,
            ):
                try:
                    self._send_request(request_type, timeout_seconds=0.2)
                except (OSError, RuntimeError, TimeoutError):
                    pass
        self._closed.set()
        current_socket = self._socket
        self._socket = None
        if current_socket is not None:
            try:
                current_socket.close()
            except OSError:
                pass

    def _send_raw_frame(self, frame: bytes) -> None:
        if self._socket is None:
            raise RuntimeError('Karabiner socket is not connected')
        with self._write_lock:
            self._socket.sendall(frame)

    def _send_request(
        self,
        request_type: RequestType,
        payload: bytes = b'',
        timeout_seconds: float = 2.0,
    ) -> bytes:
        request_id = self._next_request_id
        self._next_request_id += 1
        pending = PendingResponse()
        with self._pending_lock:
            self._pending[request_id] = pending
        self._send_raw_frame(
            encode_request_frame(request_id, request_payload(request_type, payload))
        )
        if not pending.event.wait(timeout_seconds):
            with self._pending_lock:
                self._pending.pop(request_id, None)
            raise TimeoutError(f'timed out waiting for Karabiner response to {request_type.name}')
        return pending.payload

    def _read_loop(self) -> None:
        try:
            while not self._closed.is_set() and self._socket is not None:
                message_type, payload = read_frame(self._socket)
                self._handle_frame(message_type, payload)
        except (EOFError, OSError):
            if not self._closed.is_set():
                self._closed.set()

    def _heartbeat_loop(self) -> None:
        while not self._closed.wait(HEARTBEAT_INTERVAL_SECONDS):
            try:
                self._send_raw_frame(encode_frame(MessageType.HEARTBEAT))
            except (OSError, RuntimeError):
                self._closed.set()
                return

    def _handle_frame(self, message_type: MessageType, payload: bytes) -> None:
        if message_type == MessageType.HEALTH_CHECK:
            self._send_raw_frame(encode_frame(MessageType.HEALTH_CHECK_RESPONSE))
            return
        if message_type == MessageType.REQUEST:
            if len(payload) < 8:
                raise ValueError('request frame is missing request id')
            request_id = struct.unpack('>Q', payload[:8])[0]
            self._send_raw_frame(encode_response_frame(request_id))
            return
        if message_type == MessageType.RESPONSE:
            if len(payload) < 8:
                raise ValueError('response frame is missing request id')
            request_id = struct.unpack('>Q', payload[:8])[0]
            with self._pending_lock:
                pending = self._pending.pop(request_id, None)
            if pending is not None:
                pending.payload = payload[8:]
                pending.event.set()

    def send_key(self, page: int, code: int, value: int) -> None:
        validate_key(page, code, value)
        if page == KEYBOARD_PAGE:
            self._send_keyboard_key(code, value)
        else:
            self._send_consumer_key(code, value)

    def _send_keyboard_key(self, code: int, value: int) -> None:
        if 0xE0 <= code <= 0xE7:
            bit = 1 << (code - 0xE0)
            if value:
                self._modifiers |= bit
            else:
                self._modifiers &= ~bit
        elif value:
            self._keyboard_keys.add(code)
        else:
            self._keyboard_keys.discard(code)
        self._send_request(
            RequestType.POST_KEYBOARD_INPUT_REPORT,
            keyboard_report(self._modifiers, self._keyboard_keys),
            timeout_seconds=0.5,
        )

    def _send_consumer_key(self, code: int, value: int) -> None:
        if value:
            self._consumer_keys.add(code)
        else:
            self._consumer_keys.discard(code)
        self._send_request(
            RequestType.POST_CONSUMER_INPUT_REPORT,
            consumer_report(self._consumer_keys),
            timeout_seconds=0.5,
        )

    def send_mouse(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        validate_mouse(buttons)
        self._send_request(
            RequestType.POST_POINTING_INPUT_REPORT,
            pointing_report(buttons, x, y, vertical_wheel, horizontal_wheel),
            timeout_seconds=0.5,
        )


class KarabinerDatagramHIDClient:
    def __init__(self, socket_path: str, country_code: int):
        self._socket_path = socket_path
        self._country_code = country_code
        self._socket: socket.socket | None = None
        self._reader_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._client_socket_path = ''
        self._closed = threading.Event()
        self._write_lock = threading.Lock()
        self._status_lock = threading.Lock()
        self._keyboard_ready = False
        self._pointing_ready = False
        self._modifiers = 0
        self._keyboard_keys: set[int] = set()
        self._consumer_keys: set[int] = set()

    def start(self) -> None:
        client_dir = Path(DATAGRAM_CLIENT_DIR)
        client_dir.mkdir(parents=True, exist_ok=True)
        self._client_socket_path = str(client_dir / f'pi_remote_{os.getpid()}.sock')
        Path(self._client_socket_path).unlink(missing_ok=True)

        connection = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        connection.bind(self._client_socket_path)
        connection.connect(self._socket_path)
        self._socket = connection
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        self._send_request(
            DatagramRequestType.VIRTUAL_HID_KEYBOARD_INITIALIZE,
            keyboard_parameters(self._country_code),
        )
        self._send_request(DatagramRequestType.VIRTUAL_HID_POINTING_INITIALIZE)
        self._wait_until_ready()

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._send_request(
                    DatagramRequestType.POST_KEYBOARD_INPUT_REPORT,
                    keyboard_report(0, set()),
                )
                self._send_request(
                    DatagramRequestType.POST_CONSUMER_INPUT_REPORT,
                    consumer_report(set()),
                )
                self._send_request(DatagramRequestType.VIRTUAL_HID_KEYBOARD_TERMINATE)
                self._send_request(DatagramRequestType.VIRTUAL_HID_POINTING_TERMINATE)
            except OSError:
                pass
            self._closed.set()
            try:
                self._socket.close()
            finally:
                self._socket = None
        if self._client_socket_path:
            Path(self._client_socket_path).unlink(missing_ok=True)

    def _send_request(self, request_type: DatagramRequestType, payload: bytes = b'') -> None:
        if self._socket is None:
            raise RuntimeError('Karabiner socket is not connected')
        request = (
            bytes([LOCAL_DATAGRAM_USER_DATA])
            + datagram_request_payload(request_type, payload)
        )
        with self._write_lock:
            self._socket.send(request)

    def _send_heartbeat(self) -> None:
        if self._socket is None:
            raise RuntimeError('Karabiner socket is not connected')
        heartbeat = struct.pack('<BI', LOCAL_DATAGRAM_HEARTBEAT, LOCAL_DATAGRAM_HEARTBEAT_DEADLINE_MS)
        with self._write_lock:
            self._socket.send(heartbeat)

    def _read_loop(self) -> None:
        while not self._closed.is_set() and self._socket is not None:
            try:
                data = self._socket.recv(1024)
            except OSError:
                return
            if len(data) < 3 or data[0] != LOCAL_DATAGRAM_USER_DATA:
                continue
            response_type = data[1]
            value = bool(data[2])
            with self._status_lock:
                if response_type == DatagramResponseType.VIRTUAL_HID_KEYBOARD_READY:
                    self._keyboard_ready = value
                elif response_type == DatagramResponseType.VIRTUAL_HID_POINTING_READY:
                    self._pointing_ready = value

    def _heartbeat_loop(self) -> None:
        while not self._closed.wait(1.0):
            try:
                self._send_heartbeat()
            except OSError:
                return

    def _wait_until_ready(self) -> None:
        deadline = time.monotonic() + CONNECT_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            with self._status_lock:
                if self._keyboard_ready and self._pointing_ready:
                    return
            time.sleep(0.05)
        raise TimeoutError('timed out waiting for Karabiner virtual HID devices to become ready')

    def send_key(self, page: int, code: int, value: int) -> None:
        validate_key(page, code, value)
        if page == KEYBOARD_PAGE:
            self._send_keyboard_key(code, value)
        else:
            self._send_consumer_key(code, value)

    def _send_keyboard_key(self, code: int, value: int) -> None:
        if 0xE0 <= code <= 0xE7:
            bit = 1 << (code - 0xE0)
            if value:
                self._modifiers |= bit
            else:
                self._modifiers &= ~bit
        elif value:
            self._keyboard_keys.add(code)
        else:
            self._keyboard_keys.discard(code)
        self._send_request(
            DatagramRequestType.POST_KEYBOARD_INPUT_REPORT,
            keyboard_report(self._modifiers, self._keyboard_keys),
        )

    def _send_consumer_key(self, code: int, value: int) -> None:
        if value:
            self._consumer_keys.add(code)
        else:
            self._consumer_keys.discard(code)
        self._send_request(
            DatagramRequestType.POST_CONSUMER_INPUT_REPORT,
            consumer_report(self._consumer_keys),
        )

    def send_mouse(
        self,
        buttons: int,
        x: int,
        y: int,
        vertical_wheel: int,
        horizontal_wheel: int,
    ) -> None:
        validate_mouse(buttons)
        self._send_request(
            DatagramRequestType.POST_POINTING_INPUT_REPORT,
            pointing_report(buttons, x, y, vertical_wheel, horizontal_wheel),
        )


def _int_field(message: dict[str, object], name: str) -> int:
    value = message.get(name)
    if not isinstance(value, int):
        raise ValueError(f'{name} must be an integer')
    return value


def validate_key(page: int, code: int, value: int) -> None:
    if value not in (0, 1):
        raise ValueError(f'key value must be 0 or 1, got {value}')
    if page not in (KEYBOARD_PAGE, CONSUMER_PAGE):
        raise ValueError(f'unsupported HID usage page: {page}')
    if not 0 <= code <= 0xFFFF:
        raise ValueError(f'HID usage code out of range: {code}')


def validate_mouse(buttons: int) -> None:
    if not 0 <= buttons <= 0xFFFFFFFF:
        raise ValueError(f'mouse button bitmask out of range: {buttons}')


def handle_message(
    client: KarabinerVirtualHIDClient | KarabinerDatagramHIDClient | DryRunClient,
    message: dict[str, object],
) -> None:
    message_type = message.get('type')
    if message_type == 'key':
        client.send_key(
            _int_field(message, 'page'),
            _int_field(message, 'code'),
            _int_field(message, 'value'),
        )
    elif message_type == 'mouse':
        client.send_mouse(
            _int_field(message, 'buttons'),
            _int_field(message, 'x'),
            _int_field(message, 'y'),
            _int_field(message, 'vertical_wheel'),
            _int_field(message, 'horizontal_wheel'),
        )
    else:
        raise ValueError(f'unsupported helper message type: {message_type}')


def run(client: KarabinerVirtualHIDClient | KarabinerDatagramHIDClient | DryRunClient) -> int:
    client.start()
    try:
        for line_number, line in enumerate(sys.stdin, 1):
            if not line.strip():
                continue
            try:
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise ValueError('JSON message must be an object')
                handle_message(client, message)
            except (json.JSONDecodeError, ValueError) as error:
                raise ValueError(f'line {line_number}: {error}') from error
    finally:
        client.close()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='pi-remote helper for Karabiner VirtualHIDDevice')
    parser.add_argument('--socket-path', default=DEFAULT_SOCKET_PATH)
    parser.add_argument('--keyboard-country-code', type=int, default=33)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def create_client(socket_path: str, country_code: int) -> KarabinerVirtualHIDClient | KarabinerDatagramHIDClient:
    if socket_path == DEFAULT_SOCKET_PATH and not Path(socket_path).exists():
        datagram_socket_path = find_datagram_socket_path()
        if datagram_socket_path:
            return KarabinerDatagramHIDClient(datagram_socket_path, country_code)
    if is_datagram_socket_path(socket_path):
        return KarabinerDatagramHIDClient(socket_path, country_code)
    return KarabinerVirtualHIDClient(socket_path, country_code)


def main() -> int:
    args = parse_args()
    if args.dry_run:
        client = DryRunClient()
    else:
        client = create_client(args.socket_path, args.keyboard_country_code)
    try:
        return run(client)
    except PermissionError as error:
        sys.stderr.write(
            f'Permission denied connecting to Karabiner socket {args.socket_path!r}. '
            'Run this helper as root, e.g. with sudo.\n'
        )
        return error.errno or 1
    except (OSError, TimeoutError, ValueError) as error:
        sys.stderr.write(f'{error}\n')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
