import os
import re
from functools import wraps
from time import sleep

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


def patch_presenter_mode():
    try:
        import Browser.base

        presenter_mode = Browser.base.LibraryComponent.presenter_mode

        @wraps(presenter_mode)
        def wrapper(self, selector, strict):
            selector = self.resolve_selector(selector)
            if self.library.presenter_mode:
                mode = self.get_presenter_mode
                try:
                    self.library.scroll_to_element(selector)
                    self.library.highlight_elements(
                        selector,
                        duration=mode["duration"],
                        width=mode["width"],
                        style=mode["style"],
                        color=mode["color"],
                    )
                except Exception as error:
                    logger.debug(f"On presenter mode supress {error}")
                else:
                    sleep(mode["duration"].seconds)
            return selector

        Browser.base.LibraryComponent.presenter_mode = wrapper
    except:
        pass


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
                try:
                    # This keyword only works when there is an active SAP Session
                    robosapiens.save_screenshot('LOG')
                except:
                    pass

    def end_test(self, data: running.TestCase, result: result.TestCase):
        if result.failed:
            message = result.message
            logger.error(escape_ansi(message))

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        patch_presenter_mode()
