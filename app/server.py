import logging
from concurrent import futures

import grpc

import input_pb2
import input_pb2_grpc
from config_service import ConfigService
from input_service import InputService
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
        key_id = request.id
        request_type = KeyActionType(request.type)
        options = (
            KeyOptions.from_pb(request.options) if request.HasField('options') else None
        )

        print(f'Pressing key {key_id} with action {request_type.name}')
        self.input_svc.press_key(key_id, request_type, options)

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
        raise NotImplementedError()

    def MoveMouse(
        self,
        request: input_pb2.MouseMove,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        raise NotImplementedError()

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


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    input_service = InputService()
    config_service = ConfigService(input_service=input_service)
    config_service.load()  # Load configuration from file

    input_pb2_grpc.add_InputMethodsServicer_to_server(
        InputMethodsService(
            config_service=config_service,
            logger=logging.getLogger(__name__),
        ),
        server,
    )

    address = f'{config_service.host}:{config_service.port}'
    server.add_insecure_port(address)
    server.start()

    logging.info(f'Server started on {address}')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
