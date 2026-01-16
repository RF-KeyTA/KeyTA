import logging
import re

from jinja2 import Environment, PackageLoader

from keyta.rf_export.keywords import RFKeywordCall
from keyta.rf_export.resource import RFResource
from keyta.rf_export.testsuite import RFTestSuite

_logger = logging.getLogger('django')


def rf_var(name: str) -> str:
    return "${" + name + "}"


EMPTY = rf_var('EMPTY')


def call_keyword(keyword_call: RFKeywordCall):
    params = [escape_spaces(param) for param in keyword_call['params']]
    return rf_join([keyword_call['keyword'], *params])


def dict_as_kwargs(dic):
    return [
        escape_spaces(f'{key}={val or EMPTY}')
        for key, val in dic.items()
    ]


def escape_backslashes(text: str):
    # A Windows path
    if re.search(r'[A-Za-z]:\\', text) or re.search(r'\\\\.*\\', text):
        return re.sub(
        r"\\(\w)",
        r"\\\\\1",
            text.replace(r'\ ', '##BACKSLASH_SPACE##')
        ).replace('##BACKSLASH_SPACE##', r'\ ')

    return text


def escape_spaces(text: str):
    return re.sub(r"\s\s+", r"\\ \\ ", text)


def keyword_arguments(args, kwargs):
    return rf_join(
        [rf_var(arg) for arg in args] +
        [rf_var(kwarg) + '=' + (default_value or EMPTY)
         for kwarg, default_value in kwargs.items()]
    )


def kwargs_list(kwargs: dict[str, str]):
    return rf_join(dict_as_kwargs(kwargs))


def rf_join(strings: list[str]):
    return "   ".join(strings)


def splitlines(string: str) -> list[str]:
    return [
        line.lstrip()
        for line in string.splitlines()
    ]


env = Environment(loader=PackageLoader('keyta.rf_export'))
env.globals['call_keyword'] = call_keyword
env.globals['keyword_arguments'] = keyword_arguments
env.globals['kwargs_list'] = kwargs_list
env.globals['rf_join'] = rf_join
env.filters['splitlines'] = splitlines


def gen_testsuite(testsuite: RFTestSuite) -> str:
    robot_template = env.get_template('template.robot.jinja')
    return escape_backslashes(robot_template.render(testsuite))


def gen_resource(resource: RFResource) -> str:
    resource_template = env.get_template('template.resource.jinja')
    return escape_backslashes(resource_template.render(resource))
