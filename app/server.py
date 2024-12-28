import logging
from concurrent import futures

import grpc

import input_pb2
import input_pb2_grpc
from config_service import ConfigService
from input_service import InputService


class InputMethodsService(input_pb2_grpc.InputMethodsServicer):
    _logger: logging.Logger
    config: ConfigService
    # keyboard_input_service: KeyboardInputService

    def __init__(self, config_service: ConfigService, logger: logging.Logger):
        self._logger = logger
        self.config = config_service

    def PressKey(
        self,
        request: input_pb2.Key,
        context: grpc.ServicerContext,
    ) -> input_pb2.Response:
        raise NotImplementedError()

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
            cursor_speed=self.config.cursor_speed,
            cursor_acceleration=self.config.cursor_acceleration,
        )
        return config

    def SetConfig(
        self,
        request: input_pb2.Config,
        context: grpc.ServicerContext,
    ) -> input_pb2.Config:
        self.config.set_cursor_speed(request.cursor_speed)
        self.config.set_cursor_acceleration(request.cursor_acceleration)

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
