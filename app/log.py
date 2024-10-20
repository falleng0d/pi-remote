"""Contains the configuration for our custom logging setup.

The file that contains the `main` function must load this module before any
of the other local imports.
"""

import logging


def create_root_logger(handler):
    """Creates a pre-configured root logger.

    It sets up the logger with custom formatting and attaches the provided
    handler.

    Args:
        handler: The log handler that shall be used (type `logging.Handler`).

    Returns:
        A logger object of type `logging.Logger`.
    """
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s.%(msecs)03d %(name)-15s %(levelname)-4s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return root_logger
