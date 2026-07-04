import logging
import unittest
from typing import cast
from typing import Any

from button import Button
from input_service import HidMouseService
from key import ButtonActionType


class Config:
    cursor_speed = 1.0
    key_press_interval = 0


class Backend:
    def __init__(self):
        self.reports = []

    def send_mouse_report(self, buttons, x, y, vertical_wheel, horizontal_wheel):
        self.reports.append((buttons, x, y, vertical_wheel, horizontal_wheel))


class HidMouseServiceTest(unittest.TestCase):
    def test_mouse_press_sends_down_then_up(self):
        backend = Backend()
        service = HidMouseService(
            cast(Any, Config()),
            cast(Any, backend),
            logging.getLogger(__name__),
        )

        service.send_button_state(Button.LEFT, ButtonActionType.PRESS)

        self.assertEqual(
            backend.reports,
            [
                (1, 0, 0, 0, 0),
                (0, 0, 0, 0, 0),
            ],
        )


if __name__ == '__main__':
    unittest.main()
