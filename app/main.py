import logging
from concurrent import futures

import grpc

import execute
import input_pb2_grpc
from config_service import ConfigService
from input_service import HidKeyboardService
from input_service import HidMouseService
from input_service import InputService
from server import InputMethodsService

root_logger = logging.getLogger()
root_logger.propagate = True

# log to stdout if INFO or higher and stderr if WARNING or higher
stdout_logger = logging.StreamHandler()
stdout_logger.addFilter(lambda record: record.levelno >= logging.WARNING)
stdout_logger.setLevel(logging.INFO)

stderr_logger = logging.StreamHandler()
stderr_logger.setLevel(0)
stderr_logger.addFilter(lambda record: record.levelno < logging.WARNING)

formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
stdout_logger.setFormatter(formatter)
stderr_logger.setFormatter(formatter)

root_logger.addHandler(stdout_logger)
root_logger.addHandler(stderr_logger)


def _noop(*args, **kwargs):
    pass


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # warm up processes
    execute.with_timeout_t(_noop, timeout_in_seconds=1)

    thread_pool = futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(thread_pool)

    config_service = ConfigService(logger=logging.getLogger(__name__))

    hid_service = HidKeyboardService(
        keyboard_path='/dev/null',
        media_path='/dev/null',
        logger=logging.getLogger(__name__),
    )

    mouse_hid_service = HidMouseService(
        mouse_path='/dev/null',
        logger=logging.getLogger(__name__),
    )

    input_service = InputService(
        hid_service=hid_service,
        mouse_service=mouse_hid_service,
        config_service=config_service,
        logger=logging.getLogger(__name__),
    )

    hid_service.keyboard_path = config_service.keyboard_path
    hid_service.media_path = config_service.media_path
    mouse_hid_service.mouse_path = config_service.mouse_path

    if config_service.is_debug:
        root_logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    input_pb2_grpc.add_InputMethodsServicer_to_server(
        InputMethodsService(
            config_service=config_service,
            input_service=input_service,
            logger=logging.getLogger(__name__),
        ),
        server,
    )

    host = config_service.host
    if config_service.host == '0.0.0.0':
        host = '[::]'

    address = f'{host}:{config_service.port}'
    logger.info(f'Starting server on {address}')

    server.add_insecure_port(address)
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info('Shutting down server')
        hid_service.unpress_all_keys()
        server.stop(0)
        thread_pool.shutdown()
        logger.info('Server stopped')
