import logging
from concurrent import futures

import grpc

import input_pb2
import input_pb2_grpc
from button import Button
from config_service import ConfigService
from input_service import InputService
from key import ButtonActionType
from key import Key
from key import KeyActionType
from key import KeyOptions


class InputMethodsService(input_pb2_grpc.InputMethodsServicer):
    _logger: logging.Logger
    config_svc: ConfigService
    input_svc: InputService
    thread_pool: futures.ThreadPoolExecutor

    def __init__(
        self,
        config_service: ConfigService,
        input_service: InputService,
        logger: logging.Logger,
    ):
        self._logger = logger
        self.config_svc = config_service
        self.input_svc = input_service
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=10)

    def PressKey(
        self,
        request: input_pb2.Key,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        key = Key(request.id)
        request_type = KeyActionType(request.type)
        options = (
            KeyOptions.from_pb(request.options) if request.HasField('options') else None
        )

        print(f'Pressing key {key.name} with action {request_type.name}')
        self.input_svc.press_key(key, request_type, options)

        return input_pb2.Response(message='Ok')

    def PressHotkey(
        self,
        request: input_pb2.Hotkey,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        raise NotImplementedError()

    def PressMouseKey(
        self,
        request: input_pb2.MouseKey,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        button = Button(request.id)
        request_type = ButtonActionType(request.type)

        self.input_svc.press_mouse_key(button, request_type)

        return input_pb2.Response(message='Ok')

    def MoveMouse(
        self,
        request: input_pb2.MouseMove,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        self.input_svc.move_mouse(request.x, request.y)

        return input_pb2.Response(message='Ok')

    def Ping(self, _, __) -> input_pb2.Response:
        return input_pb2.Response(message='Ok')

    def GetConfig(
        self,
        request: input_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> input_pb2.Config:
        config = input_pb2.Config(
            cursor_speed=self.config_svc.cursor_speed,
            cursor_acceleration=self.config_svc.cursor_acceleration,
        )
        return config

    def SetConfig(
        self,
        request: input_pb2.Config,
        context: grpc.ServicerContext,
    ) -> input_pb2.Config:
        self.config_svc.set_cursor_speed(request.cursor_speed)
        self.config_svc.set_cursor_acceleration(request.cursor_acceleration)

        return self.GetConfig(input_pb2.Empty(), context)
