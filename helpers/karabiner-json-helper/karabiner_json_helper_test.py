import importlib.util
import pathlib
import sys
import unittest

HELPER_PATH = pathlib.Path(__file__).with_name('karabiner_json_helper.py')
SPEC = importlib.util.spec_from_file_location('karabiner_json_helper', HELPER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('Could not load karabiner_json_helper.py')
helper = importlib.util.module_from_spec(SPEC)
sys.modules['karabiner_json_helper'] = helper
SPEC.loader.exec_module(helper)


class KarabinerJsonHelperTest(unittest.TestCase):
    def test_keyboard_report_encodes_modifier_and_keys(self):
        report = helper.keyboard_report(0x02, {0x04, 0x05})

        self.assertEqual(report[:3], bytes([1, 0x02, 0]))
        self.assertEqual(report[3:7], bytes([0x04, 0, 0x05, 0]))
        self.assertEqual(len(report), 67)

    def test_request_frame_uses_big_endian_frame_and_request_id(self):
        frame = helper.encode_request_frame(1, b'abc')

        self.assertEqual(frame[:4], bytes([0, 0, 0, 12]))
        self.assertEqual(frame[4], helper.MessageType.REQUEST)
        self.assertEqual(frame[5:13], bytes([0, 0, 0, 0, 0, 0, 0, 1]))
        self.assertEqual(frame[13:], b'abc')

    def test_pointing_report_encodes_signed_bytes(self):
        report = helper.pointing_report(1, 2, -128, 200, -200)

        self.assertEqual(report, bytes([1, 0, 0, 0, 2, 128, 127, 128]))

    def test_consumer_report_encodes_report_id_and_keys(self):
        report = helper.consumer_report({0x00E9})

        self.assertEqual(report[:3], bytes([2, 0xE9, 0]))
        self.assertEqual(len(report), 65)

    def test_keyboard_initialize_payload_uses_little_endian_structs(self):
        payload = helper.request_payload(
            helper.RequestType.VIRTUAL_HID_KEYBOARD_INITIALIZE,
            helper.keyboard_parameters(33),
        )

        self.assertEqual(payload[:3], bytes([7, 0, 0]))
        self.assertEqual(payload[3:11], (0x16C0).to_bytes(8, 'little'))
        self.assertEqual(payload[11:19], (0x27DB).to_bytes(8, 'little'))
        self.assertEqual(payload[19:27], (33).to_bytes(8, 'little'))

    def test_datagram_request_payload_uses_v6_header(self):
        payload = helper.datagram_request_payload(
            helper.DatagramRequestType.VIRTUAL_HID_KEYBOARD_INITIALIZE,
            helper.keyboard_parameters(33),
        )

        self.assertEqual(payload[:5], bytes([ord('c'), ord('p'), 5, 0, 1]))
        self.assertEqual(payload[5:13], (0x16C0).to_bytes(8, 'little'))
        self.assertEqual(payload[13:21], (0x27DB).to_bytes(8, 'little'))
        self.assertEqual(payload[21:29], (33).to_bytes(8, 'little'))

    def test_dry_run_validates_unsupported_page(self):
        client = helper.DryRunClient()

        with self.assertRaisesRegex(ValueError, 'unsupported HID usage page'):
            client.send_key(1, 4, 1)

    def test_connect_socket_retries_when_socket_is_not_ready(self):
        attempts = []

        class FakeSocket:
            def __init__(self):
                self.closed = False
                attempts.append(self)

            def connect(self, socket_path):
                if len(attempts) == 1:
                    raise FileNotFoundError(2, 'No such file or directory')

            def close(self):
                self.closed = True

        original_socket = helper.socket.socket
        original_sleep = helper.time.sleep
        helper.socket.socket = lambda *_args: FakeSocket()
        helper.time.sleep = lambda _seconds: None
        try:
            connection = helper.connect_socket('/missing-then-ready.sock')
        finally:
            helper.socket.socket = original_socket
            helper.time.sleep = original_sleep

        self.assertTrue(attempts[0].closed)
        self.assertIs(connection, attempts[1])


if __name__ == '__main__':
    unittest.main()
