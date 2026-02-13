import base64
import json
import os
import re
import traceback
import uuid
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader
from jinja2.filters import escape


def format_date(date: datetime):
    return date.strftime('%H:%M:%S %d.%m.%Y')


def format_kw_name(name: str) -> str:
    if '::' in name:
        _, kw_name = name.split('::')
        return kw_name

    return name


def format_newline(text: str):
    return text.replace('\n', '<br>')


def format_time(time_str):
    time = int(time_str)

    if time < 60:
        return '%s %s' % (time, translate('seconds'))

    return '%s:%s %s' % (time // 60, time % 60, translate('minutes'))


def format_value(value):
    try:
        return json.loads(value)
    except:
        return value


def get_return_values(step: dict):
    messages: list[str] = [
        dic['message']
        for dic in step['body']
        if dic.get('type', None) == 'MESSAGE'
    ]

    return {
        unrobot(return_value): format_value(message.removeprefix(f'{return_value} = '))
        for return_value in step['assign']
        for message in messages
        if message.startswith(return_value)
    }


def parse_date(date_str: str):
    return datetime.fromisoformat(date_str)


def parse_object(pairs):
    body = False
    result = []

    for k, v in pairs:
        # Filter out duplicate "body" keys before calling dict
        # because they would overwrite the actual test body
        if k == 'body':
            if not body:
                result.append((k, v))
                body = True
        else:
            result.append((k, v))

    return dict(result)


def save_log(filename: str, testsuite_name: str, output_file: str, keywords: list) -> Path:
    output_dir = Path(output_file).parent

    try:
        log_data = RobotLog(testsuite_name).simplify_output(keywords, output_file)
        env = Environment(loader=PackageLoader('keyta.rf_log', package_path='templates'))
        env.filters['translate'] = translate
        template = env.get_template('testcase_log.jinja.html')
        log = template.render({**template_assets(), 'rf': log_data})
        log_path = output_dir / (filename + '.html')

        with open(log_path, 'w', encoding='utf-8') as file_handle:
            file_handle.write(log)
    except:
        print(traceback.print_exc())
        log_path = output_dir / 'log.html'

    return log_path


def template_assets():
    cwd = Path(os.path.realpath(__file__)).parent
    logo = open(cwd / 'static' / 'RF_Logo.png', mode='rb').read()
    logo_b64 = base64.b64encode(logo).decode('utf-8')

    return {
        "logo": f"data:image/jpg;base64, {logo_b64}",
        "icon": {
            "action": '<i class="fa-solid fa-cubes-stacked"></i>',
            "go_back": '<i class="fa-solid fa-arrow-left-long fa-xl"></i>',
            "go_to": '<i class="fa-solid fa-arrow-up-right-from-square"></i>',
            "sequence": '<i class="fa-solid fa-arrows-turn-to-dots"></i>',
            "testcase": '<i class="fa-solid fa-list-check"></i>'
        }
    }


def translate(text):
    translations = {
        'Elapsed time': 'Laufzeit',
        'minutes': 'Minuten',
        'Robot Framework Log': 'Robot Framework Protokoll',
        'Start time': 'Datum',
        'seconds': 'Sekunden'
    }

    lang = os.environ.get('KEYTA_LANG')

    if lang == 'de':
        return translations[text]

    return text


def unrobot(token):
    if token == '${EMPTY}':
        return ''

    dict_access = re.compile(r'\${(.*)}\[(.*)\]')

    if match := re.match(dict_access, token):
        return f'{match.group(1)}.{match.group(2)}'

    if token.startswith('${') and token.endswith('}'):
        return token.removeprefix('${').removesuffix('}')

    return token


class RobotLog:
    def __init__(self, testsuite_name: str):
        self.keyword_args = {}
        self.items = {
            "errors": dict(),
            "keywords": dict(),
            "test_cases": [],
            "testsuite": {
                'name': testsuite_name
            }
        }

    def simplify_output(self, keywords: list, output_json: str) -> dict:
        for keyword in keywords:
            name = keyword['name']

            self.keyword_args[name] = [unrobot(arg) for arg in keyword.get('args', [])]

        with open(output_json, encoding='utf-8') as file:
            output = json.load(file, object_pairs_hook=parse_object)

        for error in output['errors']:
            error['message'] = format_newline(str(escape(error['message'])))
            message = error['message']
            self.items['errors'][message] = {
                'id': str(uuid.uuid4())
            } | error

        for test in output['suite']['tests']:
            simple_test = self.simplify_test(test)
            self.items['test_cases'].append(simple_test)

        return self.items

    def simplify_step(self, step: dict, parent_id: str, assign: dict|None = None, level=0) -> dict:
        name = step['name']
        kind = 'ROBOT_KW'

        if '::' in name:
            if name.startswith('A'):
                kind = 'ACTION'

            if name.startswith('S'):
                kind = 'SEQUENCE'

        if 'owner' in step:
            name = step['owner'] + '.' + step['name']

        step_id = str(uuid.uuid4())

        result = {
            'parent_id': parent_id,
            'id': step_id,
            'name': format_kw_name(name),
            'kind': kind,
            'status': step['status'],
            'start_time': format_date(parse_date(step['start_time'])),
            'elapsed_time': format_time(step['elapsed_time']),
            'steps': [],
            'args': {},
            'return_values': dict(),
        }

        messages = set()

        if 'message' in step:
            message = format_newline(str(escape(step['message'])))
            result['message'] = message
            messages.add(message)

        if 'body' in step:
            for item in step['body']:
                if item.get('type') == 'MESSAGE' and not item.get('html'):
                    message = format_newline(str(escape(item['message'])))
                    if step['status'] == 'FAIL':
                        if item['level'] == 'FAIL':
                            messages.add(message)
                    else:
                        messages.add(message)

                if item.get('html'):
                    messages.add(re.sub(r'width="[^"]+"', 'width="100%"', item['message']))

                if item.get('type') == 'IF/ELSE ROOT':
                    for branch in item['body']:
                        for branch_step in branch['body']:
                            branch_step_id = str(uuid.uuid4())
                            simple_step = self.simplify_step(branch_step, branch_step_id, level=level + 1)
                            simple_step_id = simple_step['id']
                            result['steps'].append(simple_step_id)
                            self.items['keywords'][simple_step_id] = simple_step

                if not 'type' in item:
                    simple_step = self.simplify_step(item, step_id, level=level + 1)
                    simple_step_id = simple_step['id']
                    result['steps'].append(simple_step_id)
                    self.items['keywords'][simple_step_id] = simple_step

            result['messages'] = list(messages)

        if 'doc' in step and step['doc'].startswith('http'):
            result.update({'url': step['doc']})

        if 'args' in step:
            arg_name_index = 0
            arg_names = self.keyword_args[name]
            args = {}
            vararg_name = None
            varargs = []
            varkwarg_name = None
            varkwargs = []

            def format_arg_value(arg_name, arg_value):
                value = arg_value.removeprefix(f'{arg_name}=')

                if assign: return assign[value]
                if level < 2: return unrobot(value)
                return value

            for arg in step['args']:
                arg_name = arg_names[arg_name_index]

                if arg_name.startswith('**'):
                    varkwargs.append(arg)

                    if arg_name not in args:
                        varkwarg_name = arg_name
                        args[varkwarg_name] = []
                elif arg_name.startswith('*'):
                    if match := re.match(r'(\w+)=', arg):
                        name = match.group(1)
                        if name in set(arg_names):
                            arg_name_index += 2
                            args[name] = format_arg_value(name, arg)
                    else:
                        varargs.append(arg)

                        if arg_name not in args:
                            vararg_name = arg_name
                            args[vararg_name] = []
                else:
                    arg_name_index += 1
                    args[arg_name] = format_arg_value(arg_name, arg)

            if vararg_name:
                args[vararg_name] = (4 * '&nbsp;').join(varargs)

            if varkwarg_name:
                args[varkwarg_name] = (4 * '&nbsp;').join(varkwargs)

            result.update({'args': args})

        if 'assign' in step and 'body' in step:
            result.update({'return_values': get_return_values(step)})

        return result

    def simplify_test(self, test: dict):
        test_id = str(uuid.uuid4())

        result = {
            'id': test_id,
            'name': test['name'],
            'status': test['status'],
            'start_time': format_date(parse_date(test['start_time'])),
            'elapsed_time': format_time(test['elapsed_time']),
            'steps': []
        }

        if 'setup' in test:
            setup = self.simplify_step(test['setup'], test_id)
            setup_id = setup['id']
            self.items['keywords'][setup_id] = setup
            result['steps'].append(setup_id)
            result.update({'setup': setup})

        if 'body' in test:
            for step in test['body']:
                if step.get('type') == 'VAR':
                    continue

                if 'name' in step:
                    simple_step = self.simplify_step(step, test_id)
                    step_id = simple_step['id']
                    result['steps'].append(step_id)
                    self.items['keywords'][step_id] = simple_step

                if step.get('type') == 'FOR':
                    for iter in step['body']:
                        for step in iter['body']:
                            simple_step = self.simplify_step(step, test_id, assign=iter['assign'])
                            step_id = simple_step['id']
                            result['steps'].append(step_id)
                            self.items['keywords'][step_id] = simple_step

        if 'teardown' in test:
            teardown = self.simplify_step(test['teardown'], test_id)
            teardown_id = teardown['id']
            self.items['keywords'][teardown_id] = teardown
            result['steps'].append(teardown_id)
            result.update({'teardown': teardown})

        return result
