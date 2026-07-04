import logging
import sys
from concurrent import futures

import grpc

import execute
import input_pb2_grpc
from config_service import ConfigService
from input_backend import KarabinerBackend
from input_backend import UsbGadgetBackend
from input_service import HidKeyboardService
from input_service import HidMouseService
from input_service import InputService
from server import InputMethodsService

root_logger = logging.getLogger()
root_logger.propagate = True

stdout_logger = logging.StreamHandler(sys.stdout)
stdout_logger.setLevel(0)
stdout_logger.addFilter(lambda record: record.levelno < logging.WARNING)

stderr_logger = logging.StreamHandler(sys.stderr)
stderr_logger.setLevel(logging.WARNING)

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

    if config_service.output_backend == 'karabiner':
        backend = KarabinerBackend(
            helper_command=config_service.karabiner_helper_command,
            logger=logging.getLogger(__name__),
            device_hash=config_service.karabiner_device_hash,
        )
    else:
        backend = UsbGadgetBackend(
            keyboard_path=config_service.keyboard_path,
            mouse_path=config_service.mouse_path,
            media_path=config_service.media_path,
            logger=logging.getLogger(__name__),
        )

    hid_service = HidKeyboardService(
        backend=backend,
        logger=logging.getLogger(__name__),
    )

    mouse_hid_service = HidMouseService(
        config_service=config_service,
        backend=backend,
        logger=logging.getLogger(__name__),
    )

    input_service = InputService(
        hid_service=hid_service,
        mouse_service=mouse_hid_service,
        config_service=config_service,
        logger=logging.getLogger(__name__),
    )

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
    if (
        config_service.output_backend == 'karabiner'
        and host == '0.0.0.0'
        and not config_service.karabiner_allow_remote
    ):
        logger.warning('Karabiner backend selected; binding to 127.0.0.1 instead of 0.0.0.0')
        host = '127.0.0.1'
    elif config_service.host == '0.0.0.0':
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
        backend.close()
        server.stop(0)
        thread_pool.shutdown()
        logger.info('Server stopped')
