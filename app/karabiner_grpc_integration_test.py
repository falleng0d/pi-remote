"""Manual Karabiner gRPC integration test.

Run on macOS with Karabiner-Elements installed, a logged-in GUI session, and
root privileges so the helper can reach Karabiner's root-only socket.

Example:
    sudo env PI_REMOTE_LIVE_KARABINER=1 PYTHONPATH=. ./.venv/bin/python -m unittest \
        app.karabiner_grpc_integration_test

The test stays skipped unless PI_REMOTE_LIVE_KARABINER=1 is set.
"""

from __future__ import annotations

import os
import shlex
import socket
import string
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / 'app'
for path in (str(REPO_ROOT), str(APP_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import grpc

from app import input_pb2
from app import input_pb2_grpc
from app.key import Key as InternalKey

try:
    import tkinter as tk
except ImportError:  # pragma: no cover - tkinter is platform dependent.
    tk = None


TEXT = 'pi'

ASCII_KEY_IDS = {
    ch: getattr(InternalKey, f'KEY_{ch.upper()}').value for ch in string.ascii_lowercase
}
ASCII_KEY_IDS.update({str(i): getattr(InternalKey, f'KEY_{i}').value for i in range(10)})
ASCII_KEY_IDS[' '] = InternalKey.KEY_SPACE.value


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def _repo_root() -> Path:
    return REPO_ROOT


def _helper_command() -> str:
    helper_script = _repo_root() / 'helpers' / 'karabiner-json-helper' / 'karabiner_json_helper.py'
    return f'{shlex.quote(sys.executable)} {shlex.quote(str(helper_script))}'


def _wait_for_server(channel: grpc.Channel, process: Any, timeout: float = 10.0) -> None:
    ready = grpc.channel_ready_future(channel)
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f'pi-remote exited early with code {process.returncode}')

        try:
            ready.result(timeout=0.2)
            return
        except grpc.FutureTimeoutError:
            pass

    raise TimeoutError('Timed out waiting for pi-remote to start')


def _wait_for_entry_text(entry: Any, expected: str, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        entry.update()
        if entry.get() == expected:
            return
        time.sleep(0.05)

    raise AssertionError(f'Expected {expected!r}, got {entry.get()!r}')


class KarabinerGrpcIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        missing = []
        if sys.platform != 'darwin':
            missing.append('macOS')
        if os.environ.get('PI_REMOTE_LIVE_KARABINER') != '1':
            missing.append('PI_REMOTE_LIVE_KARABINER=1')
        if os.geteuid() != 0:
            missing.append('root')
        if tk is None:
            missing.append('tkinter')

        if missing:
            self.skipTest('Karabiner integration prerequisites missing: ' + ', '.join(missing))

    def test_types_text_into_a_focused_entry(self) -> None:
        port = _free_port()
        config = tempfile.TemporaryDirectory()
        server = None
        root = None

        try:
            config_path = Path(config.name) / 'remotecontrol.cfg'
            config_path.write_text(
                '\n'.join(
                    [
                        "debug = False",
                        "cursor_speed = 1.0",
                        "cursor_acceleration = 1.0",
                        "key_press_interval = 33",
                        f'port = {port}',
                        "host = '127.0.0.1'",
                        "output_backend = 'karabiner'",
                        f'karabiner_helper_command = {_helper_command()!r}',
                        'karabiner_device_hash = 0',
                        'karabiner_allow_remote = False',
                        '',
                    ]
                )
            )

            server_env = os.environ.copy()
            server_env['PYTHONPATH'] = os.pathsep.join(
                [str(_repo_root()), str(APP_DIR), server_env.get('PYTHONPATH', '')]
            ).strip(os.pathsep)

            server = subprocess.Popen(
                [sys.executable, '-m', 'app.main'],
                cwd=config.name,
                env=server_env,
            )

            channel = grpc.insecure_channel(f'127.0.0.1:{port}')
            _wait_for_server(channel, server)
            stub = input_pb2_grpc.InputMethodsStub(channel)

            assert tk is not None
            tk_module = cast(Any, tk)
            root = tk_module.Tk()
            root.title('pi-remote karabiner integration test')
            entry = tk_module.Entry(root)
            entry.pack()
            root.update()
            entry.focus_force()
            root.update()

            for ch in TEXT:
                stub.PressKey(
                    input_pb2.Key(
                        id=ASCII_KEY_IDS[ch],
                        type=input_pb2.KeyActionType.PRESS,
                    )
                )

            _wait_for_entry_text(entry, TEXT)
        finally:
            if root is not None:
                root.destroy()
            if server is not None and server.poll() is None:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)
            config.cleanup()


if __name__ == '__main__':
    unittest.main()
