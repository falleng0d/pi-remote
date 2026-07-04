import unittest

from hid import keycodes
from key import Key
from key_utils import key_to_keycode


class KeyUtilsTest(unittest.TestCase):
    def test_media_keys_have_consumer_page_usages(self):
        self.assertEqual(key_to_keycode(Key.KEY_MEDIA_STOP), keycodes.KEYCODE_MEDIA_STOP)
        self.assertEqual(key_to_keycode(Key.KEY_BROWSER_BACK), keycodes.KEYCODE_BROWSER_BACK)
        self.assertEqual(key_to_keycode(Key.KEY_BROWSER_FORWARD), keycodes.KEYCODE_BROWSER_FORWARD)
        self.assertEqual(key_to_keycode(Key.KEY_BROWSER_REFRESH), keycodes.KEYCODE_BROWSER_REFRESH)


if __name__ == '__main__':
    unittest.main()
