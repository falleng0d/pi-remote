import unittest
from unittest.mock import mock_open
from unittest.mock import patch

from app.config_service import PyPreferences


class TestPyPreferences(unittest.TestCase):
    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='DEBUG = True\nCURSOR_SPEED = 1.5\n',
    )
    @patch('pathlib.Path.exists', return_value=True)
    def setUp(self, mock_exists, mock_open):
        self.prefs = PyPreferences('test_settings.cfg')

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='DEBUG = True\nCURSOR_SPEED = 1.5\n',
    )
    @patch('pathlib.Path.exists', return_value=True)
    def test_load(self, mock_exists, mock_open):
        self.prefs._load()
        self.assertEqual(self.prefs.data['DEBUG'], True)
        self.assertEqual(self.prefs.data['CURSOR_SPEED'], 1.5)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_save(self, mock_exists, mock_open):
        self.prefs.set('DEBUG', False)
        self.prefs.set('CURSOR_SPEED', 1.0)
        mock_open().write.assert_any_call('DEBUG = False\n')
        mock_open().write.assert_any_call('CURSOR_SPEED = 1.0\n')

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='DEBUG = True\nCURSOR_SPEED = 1.5\n',
    )
    @patch('pathlib.Path.exists', return_value=True)
    def test_get(self, mock_exists, mock_open):
        self.prefs._load()
        self.assertEqual(self.prefs.get('DEBUG'), True)
        self.assertEqual(self.prefs.get('CURSOR_SPEED'), 1.5)
        self.assertEqual(self.prefs.get('NON_EXISTENT_KEY', 'default'), 'default')

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_set(self, mock_exists, mock_open):
        self.prefs.set('DEBUG', False)
        self.assertEqual(self.prefs.data['DEBUG'], False)
        self.prefs.set('CURSOR_SPEED', 1.0)
        self.assertEqual(self.prefs.data['CURSOR_SPEED'], 1.0)


if __name__ == '__main__':
    unittest.main()
