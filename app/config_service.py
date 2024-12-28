import logging
import types
from pathlib import Path

from app.input_service import InputService


class PyPreferences:
    filepath: Path
    data: dict[str, any]

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

    def _save(self):
        with open(self.filepath, 'w') as file:
            for key, value in self.data.items():
                file.write(f'{key} = {repr(value)}\n')

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._save()


class ConfigService:
    _input_service: InputService
    _logger: logging.Logger
    _initialized = False
    _is_debug = False
    _cursor_speed = 1.0
    _cursor_acceleration = 1.0
    _key_press_interval = 33
    _host = '0.0.0.0'
    _port = 9036

    _key_repeat_delay = 300  # 300ms (CONSTANT)
    _key_repeat_interval = 1000 // 30  # 15hz (CONSTANT)

    def __init__(self, input_service: InputService, logger: logging.Logger):
        self._input_service = input_service
        self._prefs = PyPreferences('remotecontrol.cfg')
        self._logger = logger

    @property
    def cursor_speed(self):
        return self._cursor_speed

    @property
    def cursor_acceleration(self):
        return self._cursor_acceleration

    @property
    def key_press_interval(self):
        return self._key_press_interval

    @property
    def key_repeat_delay(self):
        return self._key_repeat_delay

    @property
    def key_repeat_interval(self):
        return self._key_repeat_interval

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def is_debug(self):
        return self._is_debug

    def load(self):
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

        self._initialized = True

        self.log_preferences()

    def log_preferences(self):
        self._logger.info('Host: %s', self._host)
        self._logger.info('Port: %s', self._port)
        self._logger.info('Debug: %s', self._is_debug)
        self._logger.info('Cursor speed: %s', self._cursor_speed)
        self._logger.info('Cursor acceleration: %s', self._cursor_acceleration)
        self._logger.info('Key press interval: %s', self._key_press_interval)

    def set_cursor_speed(self, speed: float):
        if not self._initialized:
            raise Exception('Preferences not initialized!')
        if speed < 0 or speed > 2:
            raise ValueError('Speed must be between 0 and 2')

        self._prefs.set('cursor_speed', speed)
        self._cursor_speed = speed

    def set_cursor_acceleration(self, acceleration: float):
        if not self._initialized:
            raise Exception('Preferences not initialized!')
        if acceleration < 0 or acceleration > 2:
            raise ValueError('Acceleration must be between 0 and 2')

        self._prefs.set('cursor_acceleration', acceleration)
        self._cursor_acceleration = acceleration

    def set_key_press_interval(self, interval: int):
        if not self._initialized:
            raise Exception('Preferences not initialized!')
        if interval < 0 or interval > 1000:
            raise ValueError('Interval must be between 0 and 1000')

        self._prefs.set('key_press_interval', interval)
        self._key_press_interval = interval

    def set_host(self, host: str):
        if not self._initialized:
            raise Exception('Preferences not initialized!')

        self._prefs.set('host', host)
        self._host = host

    def set_port(self, port: int):
        if not self._initialized:
            raise Exception('Preferences not initialized!')
        if port < 1 or port > 65535:
            raise ValueError('Port must be between 1 and 65535')

        self._prefs.set('port', port)
        self._port = port

    def set_debug(self, debug: bool):
        if not self._initialized:
            raise Exception('Preferences not initialized!')

        self._prefs.set('debug', debug)
        self._is_debug = debug
        self._input_service.is_debug = debug
