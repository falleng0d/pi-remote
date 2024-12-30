from hid import write as hid_write


def send_mouse_event(
    mouse_path,
    buttons,
    relative_x,
    relative_y,
    vertical_wheel_delta,
    horizontal_wheel_delta,
):
    # pylint: disable=invalid-name
    x, y = _scale_mouse_coordinates(relative_x, relative_y)

    buf = [0] * 7
    buf[0] = buttons
    buf[1] = x & 0xFF
    buf[2] = (x >> 8) & 0xFF
    buf[3] = y & 0xFF
    buf[4] = (y >> 8) & 0xFF
    buf[5] = _translate_vertical_wheel_delta(vertical_wheel_delta) & 0xFF
    buf[6] = horizontal_wheel_delta & 0xFF
    hid_write.write_to_hid_interface(mouse_path, buf)


def _scale_mouse_coordinates(relative_x, relative_y):
    # This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
    max_hid_value = 32767.0
    # pylint: disable=invalid-name
    x = int(relative_x * max_hid_value)
    y = int(relative_y * max_hid_value)
    return x, y


def _translate_vertical_wheel_delta(vertical_wheel_delta):
    # In JavaScript, a negative wheel delta number indicates upward scrolling,
    # but in HID, negative means downward scrolling, so we negate the value to
    # translate from JavaScript semantics to HID semantics.
    return vertical_wheel_delta * -1
