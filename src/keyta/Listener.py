import os
import re

from robot import running
from robot.result import TestCase
from robot.api import logger
from robot.api.interfaces import ListenerV3


# On windows, calling os.system("") makes ANSI escape sequences
# get processed correctly
os.system("")


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


class Listener(ListenerV3):
    def end_test(self, data: running.TestCase, result: TestCase):
        if result.failed:
            message = result.message
            logger.error(escape_ansi(message))
