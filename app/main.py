import logging
from concurrent import futures

import grpc

import input_pb2_grpc
from config_service import ConfigService
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

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    thread_pool = futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(thread_pool)

    input_service = InputService()

    config_service = ConfigService(
        input_service=input_service,
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
    server.wait_for_termination()
