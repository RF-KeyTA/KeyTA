import os
import re

from robot import result, running
from robot.api import logger
from robot.api.interfaces import ListenerV3
from robot.libraries.BuiltIn import BuiltIn


# On Windows, calling os.system("") makes ANSI escape sequences
# get processed correctly
os.system("")


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def get_robosapiens():
    library = 'RoboSAPiens'

    try:
        return BuiltIn().get_library_instance(library)
    except:
        pass

    try:
        return BuiltIn().get_library_instance(library + '.DE')
    except:
        pass

    return None


class Listener(ListenerV3):
    def end_library_keyword(self, data: running.Keyword, implementation: running.LibraryKeyword, result: result.Keyword):
        if result.failed and implementation.full_name.startswith('RoboSAPiens'):
            if robosapiens := get_robosapiens():
                robosapiens.save_screenshot('LOG')

    def end_test(self, data: running.TestCase, result: result.TestCase):
        if result.failed:
            message = result.message
            logger.error(escape_ansi(message))
