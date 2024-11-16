import logging


class Logger:
    def __init__(self, name="globalLogger"):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(name)

    def getLevel(self):
        return self.logger.getEffectiveLevel()

    def setDebug(self):
        self.logger.setLevel(logging.DEBUG)

    def log(self, level, message):
        if level == "debug":
            self.logger.debug(message)
        elif level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)


logger = Logger()
