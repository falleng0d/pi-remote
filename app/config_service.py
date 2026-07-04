import logging
import types
from pathlib import Path

class NotInitializedError(Exception):
    pass


class PyPreferences:
    filepath: Path
    data: dict[str, object]

    def __init__(self, filename: str):
        # First check local directory
        local_path = Path(filename)
        home_path = Path.home() / filename

        # Use local file if it exists, otherwise use home directory
        self.filepath = local_path if local_path.exists() else home_path
        if not self.filepath.exists():
            self.filepath.write_text('')
        self._load()

    def _load(self):
        filename = str(self.filepath)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except OSError as e:
            raise Exception(f'Unable to load configuration file ({e.strerror})')
        self.data = {
            key: value for key, value in d.__dict__.items() if not key.startswith('_')
        }

    def save(self):
        with open(self.filepath, 'w') as file:
            for key, value in self.data.items():
                file.write(f'{key} = {repr(value)}\n')

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()


class ConfigService:
    _logger: logging.Logger
    _initialized = False
    _is_debug = False
    _cursor_speed = 1.0
    _cursor_acceleration = 1.0
    _key_press_interval = 33
    _host = '0.0.0.0'
    _port = 9036
    _output_backend = 'usb-gadget'
    _keyboard_path = '/dev/null'
    _mouse_path = '/dev/null'
    _media_path = '/dev/null'
    _karabiner_helper_command = ''
    _karabiner_device_hash = 0
    _karabiner_allow_remote = False

    _key_repeat_delay = 300  # 300ms (CONSTANT)
    _key_repeat_interval = 1000 // 30  # 15hz (CONSTANT)

    def __init__(self, logger: logging.Logger):
        self._prefs = PyPreferences('remotecontrol.cfg')
        self._logger = logger
        self._load()

    @property
    def cursor_speed(self) -> float:
        return self._cursor_speed

    @property
    def cursor_acceleration(self) -> float:
        return self._cursor_acceleration

    @property
    def key_press_interval(self) -> int:
        return self._key_press_interval

    @property
    def key_repeat_delay(self) -> int:
        return self._key_repeat_delay

    @property
    def key_repeat_interval(self) -> int:
        return self._key_repeat_interval

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def keyboard_path(self) -> str:
        return self._keyboard_path

    @property
    def mouse_path(self) -> str:
        return self._mouse_path

    @property
    def media_path(self) -> str:
        return self._media_path

    @property
    def output_backend(self) -> str:
        return self._output_backend

    @property
    def karabiner_helper_command(self) -> str:
        return self._karabiner_helper_command

    @property
    def karabiner_device_hash(self) -> int:
        return self._karabiner_device_hash

    @property
    def karabiner_allow_remote(self) -> bool:
        return self._karabiner_allow_remote

    def _load(self):
        self._cursor_speed = self._prefs.get('cursor_speed', self._cursor_speed)
        self._cursor_acceleration = self._prefs.get(
            'cursor_acceleration', self._cursor_acceleration
        )
        self._key_press_interval = self._prefs.get(
            'key_press_interval', self._key_press_interval
        )
        self._host = self._prefs.get('host', self._host)
        self._port = self._prefs.get('port', self._port)
        self._is_debug = self._prefs.get('debug', self._is_debug)
        self._output_backend = self._prefs.get('output_backend', self._output_backend)
        self._keyboard_path = self._prefs.get('keyboard_path', self._keyboard_path)
        self._mouse_path = self._prefs.get('mouse_path', self._mouse_path)
        self._media_path = self._prefs.get('media_path', self._media_path)
        self._karabiner_helper_command = self._prefs.get(
            'karabiner_helper_command', self._karabiner_helper_command
        )
        self._karabiner_device_hash = self._prefs.get(
            'karabiner_device_hash', self._karabiner_device_hash
        )
        self._karabiner_allow_remote = self._prefs.get(
            'karabiner_allow_remote', self._karabiner_allow_remote
        )

        if self._output_backend == 'karabiner' and self._prefs.get('host') is None:
            self._host = '127.0.0.1'

        self._initialized = True

        self._save()

    def _save(self):
        self._prefs.set('cursor_speed', self._cursor_speed)
        self._prefs.set('cursor_acceleration', self._cursor_acceleration)
        self._prefs.set('key_press_interval', self._key_press_interval)
        self._prefs.set('host', self._host)
        self._prefs.set('port', self._port)
        self._prefs.set('debug', self._is_debug)
        self._prefs.set('output_backend', self._output_backend)
        self._prefs.set('keyboard_path', self._keyboard_path)
        self._prefs.set('mouse_path', self._mouse_path)
        self._prefs.set('media_path', self._media_path)
        self._prefs.set('karabiner_helper_command', self._karabiner_helper_command)
        self._prefs.set('karabiner_device_hash', self._karabiner_device_hash)
        self._prefs.set('karabiner_allow_remote', self._karabiner_allow_remote)

        self._prefs.save()
        
        self._logger.info('Preferences saved')
        
        self.log_preferences()

    def log_preferences(self):
        self._logger.info('Host: %s', self._host)
        self._logger.info('Port: %s', self._port)
        self._logger.info('Debug: %s', self._is_debug)
        self._logger.info('Cursor speed: %s', self._cursor_speed)
        self._logger.info('Cursor acceleration: %s', self._cursor_acceleration)
        self._logger.info('Key press interval: %s', self._key_press_interval)
        self._logger.info('Output backend: %s', self._output_backend)
        self._logger.info('Keyboard path: %s', self._keyboard_path)
        self._logger.info('Mouse path: %s', self._mouse_path)
        self._logger.info('Media path: %s', self._media_path)
        self._logger.info('Karabiner helper command: %s', self._karabiner_helper_command)
        self._logger.info('Karabiner allow remote: %s', self._karabiner_allow_remote)

    def set_cursor_speed(self, speed: float):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')
        if speed < 0 or speed > 2:
            raise ValueError('Speed must be between 0 and 2')

        self._cursor_speed = speed
        
        self._save()

    def set_cursor_acceleration(self, acceleration: float):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')
        if acceleration < 0 or acceleration > 2:
            raise ValueError('Acceleration must be between 0 and 2')

        self._cursor_acceleration = acceleration
        
        self._save()

    def set_key_press_interval(self, interval: int):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')
        if interval < 0 or interval > 1000:
            raise ValueError('Interval must be between 0 and 1000')

        self._key_press_interval = interval
        
        self._save()

    def set_host(self, host: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._host = host
        
        self._save()

    def set_port(self, port: int):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')
        if port < 1 or port > 65535:
            raise ValueError('Port must be between 1 and 65535')

        self._port = port
        
        self._save()

    def set_debug(self, debug: bool):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._is_debug = debug
        
        self._save()

    def set_keyboard_path(self, path: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._keyboard_path = path
        
        self._save()

    def set_mouse_path(self, path: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._mouse_path = path
        
        self._save()

    def set_media_path(self, path: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._media_path = path
        
        self._save()

    def set_output_backend(self, output_backend: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')
        if output_backend not in ('usb-gadget', 'karabiner'):
            raise ValueError('Output backend must be usb-gadget or karabiner')

        self._output_backend = output_backend

        self._save()

    def set_karabiner_helper_command(self, command: str):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._karabiner_helper_command = command

        self._save()

    def set_karabiner_allow_remote(self, allow_remote: bool):
        if not self._initialized:
            raise NotInitializedError('Preferences not initialized!')

        self._karabiner_allow_remote = allow_remote

        self._save()
