import logging
import re

from jinja2 import Environment, PackageLoader

from apps.rf_export.keywords import RFKeywordCall
from apps.rf_export.resource import RFResource
from apps.rf_export.testsuite import RFTestSuite

_logger = logging.getLogger('django')


def call_keyword(keyword_call: RFKeywordCall):
    kw_call_args = [
        arg or '${EMPTY}'
        for arg in keyword_call['args']
    ]

    kw_call = (
            [keyword_call['keyword']] +
            kw_call_args +
            dict_as_kwargs(keyword_call['kwargs'])
    )

    if return_value := keyword_call['return_value']:
        return rf_join([return_value] + kw_call)

    return rf_join(kw_call)


def dict_as_kwargs(dic):
    return [
        escape_spaces(f'{key}={val}')
        for key, val in dic.items()
    ]


def escape_backslashes(text: str):
    return re.sub(r"\\(\w)", r"\\\\\1", text)


def escape_spaces(text: str):
    return re.sub(r"\s\s+", r"\\ \\ ", text)


def keyword_arguments(args, kwargs):
    return rf_join(
        [gen_rf_var(arg) for arg in args] +
        [gen_rf_var(kwarg) + '=' + (default_value or gen_rf_var('EMPTY'))
        for kwarg, default_value in kwargs.items()]
    )


def gen_rf_var(name: str) -> str:
    return "${" + name + "}"


def library_args(kwargs: dict[str, str]):
    return rf_join(dict_as_kwargs(kwargs))


def splitlines(string: str) -> list[str]:
    return [
        line.lstrip()
        for line in string.splitlines()
    ]


env = Environment(loader=PackageLoader('apps.rf_export'))
env.globals['call_keyword'] = call_keyword
env.globals['keyword_arguments'] = keyword_arguments
env.globals['library_args'] = library_args
env.filters['splitlines'] = splitlines


def gen_testsuite(testsuite: RFTestSuite) -> str:
    robot_template = env.get_template('template.robot.jinja')
    return escape_backslashes(robot_template.render(testsuite))


def gen_resource(resource: RFResource) -> str:
    resource_template = env.get_template('template.resource.jinja')
    return escape_backslashes(resource_template.render(resource))


def rf_join(strings: list[str]):
    return "   ".join(strings)
