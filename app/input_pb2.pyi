from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KeyActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UP: _ClassVar[KeyActionType]
    DOWN: _ClassVar[KeyActionType]
    PRESS: _ClassVar[KeyActionType]
UP: KeyActionType
DOWN: KeyActionType
PRESS: KeyActionType

class KeyOptions(_message.Message):
    __slots__ = ("no_repeat", "no_modifiers", "modifiers")
    NO_REPEAT_FIELD_NUMBER: _ClassVar[int]
    NO_MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    no_repeat: bool
    no_modifiers: bool
    modifiers: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, no_repeat: bool = ..., no_modifiers: bool = ..., modifiers: _Optional[_Iterable[int]] = ...) -> None: ...

class Key(_message.Message):
    __slots__ = ("id", "type", "options")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: KeyActionType
    options: KeyOptions
    def __init__(self, id: _Optional[int] = ..., type: _Optional[_Union[KeyActionType, str]] = ..., options: _Optional[_Union[KeyOptions, _Mapping]] = ...) -> None: ...

class HotkeyOptions(_message.Message):
    __slots__ = ("speed", "no_modifiers")
    SPEED_FIELD_NUMBER: _ClassVar[int]
    NO_MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    speed: int
    no_modifiers: bool
    def __init__(self, speed: _Optional[int] = ..., no_modifiers: bool = ...) -> None: ...

class Hotkey(_message.Message):
    __slots__ = ("hotkey", "type", "options")
    HOTKEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    hotkey: str
    type: KeyActionType
    options: HotkeyOptions
    def __init__(self, hotkey: _Optional[str] = ..., type: _Optional[_Union[KeyActionType, str]] = ..., options: _Optional[_Union[HotkeyOptions, _Mapping]] = ...) -> None: ...

class MouseKey(_message.Message):
    __slots__ = ("id", "type")
    class KeyActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UP: _ClassVar[MouseKey.KeyActionType]
        DOWN: _ClassVar[MouseKey.KeyActionType]
        PRESS: _ClassVar[MouseKey.KeyActionType]
    UP: MouseKey.KeyActionType
    DOWN: MouseKey.KeyActionType
    PRESS: MouseKey.KeyActionType
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: MouseKey.KeyActionType
    def __init__(self, id: _Optional[int] = ..., type: _Optional[_Union[MouseKey.KeyActionType, str]] = ...) -> None: ...

class MouseMove(_message.Message):
    __slots__ = ("x", "y", "relative")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    relative: bool
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., relative: bool = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("cursor_speed", "cursor_acceleration")
    CURSOR_SPEED_FIELD_NUMBER: _ClassVar[int]
    CURSOR_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    cursor_speed: float
    cursor_acceleration: float
    def __init__(self, cursor_speed: _Optional[float] = ..., cursor_acceleration: _Optional[float] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
