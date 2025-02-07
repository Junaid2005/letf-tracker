"""Custom Logger wrapper for the project"""

import logging
from io import StringIO


class Logger:
    """Custom logger class"""

    def __init__(self, name="global_logger"):
        self.log_stream = StringIO()
        self.stream_handler = logging.StreamHandler(self.log_stream)
        self.stream_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        )

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.stream_handler)

    def get_level(self):
        """Returns the log level of the logger"""
        return self.logger.getEffectiveLevel()

    def get_logs(self):
        """Returns all logs"""
        return self.log_stream.getvalue()

    def set_debug(self):
        """Sets the logger to debug mode"""
        self.logger.setLevel(logging.DEBUG)


logger = Logger()
