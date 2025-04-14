from dataclasses import dataclass
from typing import List
from typing import Optional

from key import KeyActionType
from key_str_utils import key_action_type_from_name
from key_str_utils import str_to_key


@dataclass
class HotkeyStep:
    """Represents a single step in a hotkey sequence."""

    key_code: int  # Key enum value
    action_type: KeyActionType
    wait: Optional[int] = None  # Wait time in milliseconds before executing this step
    speed: Optional[int] = None  # Speed of key press (only for PRESS action)

    def __str__(self):
        wait_str = f', wait: {self.wait}ms' if self.wait else ''
        speed_str = f', speed: {self.speed}ms' if self.speed else ''
        return f'HotkeyStep(key: {self.key_code}, action: {self.action_type.name}{wait_str}{speed_str})'


def parse_hotkey(hotkey_str: str) -> List[HotkeyStep]:
    """Parse a hotkey string into a list of hotkey steps.

    Syntax:
    - Regular characters: "abc" → Press and release each key in sequence
    - Special keys in braces: "{Ctrl}" → Press and release the Ctrl key
    - Explicit actions: "{Ctrl Down}" → Press the Ctrl key down without releasing
    - Timing control: "{Ctrl Up:500}" → Release the Ctrl key after 500ms

    Args:
        hotkey_str: String representation of a hotkey sequence

    Returns:
        List of HotkeyStep objects
    """
    steps = []

    # Process the hotkey string
    i = 0
    while i < len(hotkey_str):
        if hotkey_str[i] == '{':
            # Find the closing brace
            end_brace = hotkey_str.find('}', i)
            if end_brace == -1:
                # No closing brace, treat as regular character
                key = str_to_key(hotkey_str[i])
                steps.append(
                    HotkeyStep(key_code=key.value, action_type=KeyActionType.DOWN)
                )
                steps.append(
                    HotkeyStep(key_code=key.value, action_type=KeyActionType.UP)
                )
                i += 1
            else:
                # Extract the command inside braces
                command = hotkey_str[i + 1 : end_brace]
                parts = command.split(':')
                subparts = parts[0].split(' ')
                key_name = subparts[0]
                action_name = subparts[1] if len(subparts) > 1 else 'PRESS'
                wait = int(parts[1]) if len(parts) > 1 else None

                key = str_to_key(key_name)
                action = key_action_type_from_name(action_name)

                if action == KeyActionType.PRESS:
                    # PRESS is a combination of DOWN and UP
                    steps.append(
                        HotkeyStep(key_code=key.value, action_type=KeyActionType.DOWN)
                    )
                    steps.append(
                        HotkeyStep(
                            key_code=key.value, action_type=KeyActionType.UP, wait=wait
                        )
                    )
                else:
                    steps.append(
                        HotkeyStep(key_code=key.value, action_type=action, wait=wait)
                    )

                i = end_brace + 1
        else:
            # Regular character
            key = str_to_key(hotkey_str[i])
            steps.append(HotkeyStep(key_code=key.value, action_type=KeyActionType.DOWN))
            steps.append(HotkeyStep(key_code=key.value, action_type=KeyActionType.UP))
            i += 1

    return steps
