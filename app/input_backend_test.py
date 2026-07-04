import subprocess
import unittest

from input_backend import KarabinerBackend


class KarabinerBackendTest(unittest.TestCase):
    def test_keyboard_report_sends_state_transitions(self):
        backend = KarabinerBackend.__new__(KarabinerBackend)
        backend._device_hash = 0
        backend._keys_down = set()
        backend._modifiers_down = 0
        backend._consumer_down = 0

        sent = []

        def send(message: dict[str, object]) -> None:
            sent.append(message)

        backend._send = send

        backend.send_keyboard_report(1, (4, 0, 0, 0, 0, 0))
        backend.send_keyboard_report(0, (0, 0, 0, 0, 0, 0))

        self.assertEqual(
            sent,
            [
                {'type': 'key', 'page': 7, 'code': 224, 'value': 1, 'device_hash': 0},
                {'type': 'key', 'page': 7, 'code': 4, 'value': 1, 'device_hash': 0},
                {'type': 'key', 'page': 7, 'code': 224, 'value': 0, 'device_hash': 0},
                {'type': 'key', 'page': 7, 'code': 4, 'value': 0, 'device_hash': 0},
            ],
        )

    def test_send_includes_helper_stderr_when_process_exited(self):
        backend = KarabinerBackend.__new__(KarabinerBackend)
        backend._process = subprocess.Popen(
            ['python3', '-c', 'import sys; sys.stderr.write("socket missing\\n")'],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        backend._process.wait()

        try:
            with self.assertRaisesRegex(RuntimeError, 'socket missing'):
                backend._send({'type': 'key'})
        finally:
            if backend._process.stdin is not None:
                backend._process.stdin.close()
            if backend._process.stderr is not None:
                backend._process.stderr.close()


if __name__ == '__main__':
    unittest.main()
