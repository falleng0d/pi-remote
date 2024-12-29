#!/usr/bin/env python3

import time


def send_key_event(report):
    with open('/dev/hidg0', 'wb') as keyboard_hid:
        keyboard_hid.write(bytearray(report))


def send_media_key_event(report):
    print('Sending media key event:', [f'{x:#04x}' for x in report])
    with open('/dev/hidg2', 'wb') as media_hid:
        media_hid.write(bytearray(report))

    print(f'Sent media key event: {report}')


def press_and_release_key(keycode):
    send_key_event([0x00, 0x00, keycode, 0x00, 0x00, 0x00, 0x00, 0x00])
    time.sleep(0.01)
    send_key_event([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


keycodes = [0x0B, 0x08, 0x0F, 0x0F, 0x12, 0x2C, 0x1A, 0x12, 0x15, 0x0F, 0x07]

data_size = 2
play_pause = (
    0xCD,  # Play/Pause
    0xB5,  # Next
    0xB6,  # Previous
    0xE9,  # Volume Up
    0xEA,  # Volume Down
)
reset = [0x00] * data_size

if __name__ == '__main__':
    for k in play_pause:
        print(f'Testing media key: {k}')
        data = [0x00] * data_size
        data[0] = k
        send_media_key_event(data)
        time.sleep(0.03)
        send_media_key_event(reset)
        time.sleep(3)

    for keycode in keycodes:
        press_and_release_key(keycode)
