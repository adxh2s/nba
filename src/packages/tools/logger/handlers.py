import logging


class FileHandler(logging.FileHandler):
    """
    File handler using UTF-8 encoding.
    """

    def __init__(self, filename: str, mode: str = "a"):
        super().__init__(filename, mode=mode, encoding="utf-8")


class ConsoleHandler(logging.StreamHandler):
    """
    Console logging handler.
    """

    pass
