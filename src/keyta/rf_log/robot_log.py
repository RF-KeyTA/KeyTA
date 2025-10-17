import base64
import os
from datetime import datetime
from pathlib import Path
import json
import re
import uuid

from jinja2 import Environment, PackageLoader


def format_date(date: datetime):
    return date.strftime('%H:%M:%S %d.%m.%Y')


def format_time(time_str):
    return '%s %s' % (int(time_str), translate('seconds'))


def format_value(value):
    try:
        return json.loads(value)
    except:
        return value


def translate(text):
    translations = {
        'Elapsed time': 'Laufzeit',
        'Robot Framework Log': 'Robot Framework Protokoll',
        'Start time': 'Datum',
        'seconds': 'Sekunden'
    }

    lang = os.environ.get('KEYTA_LANG')

    if lang == 'de':
        return translations[text]

    return text


def generate_log(rf: dict):
    env = Environment(loader=PackageLoader('keyta.rf_log', package_path='templates'))
    env.filters['translate'] = translate
    log_template = env.get_template('testcase_log.jinja.html')
    cwd = Path(os.path.realpath(__file__)).parent
    logo = open(cwd / 'static' / 'RF_Logo.png', mode='rb').read()
    logo_b64 = base64.b64encode(logo).decode('utf-8')

    return log_template.render({
        "logo": f"data:image/jpg;base64, {logo_b64}",
        "rf": rf,
        "icon": {
            "action": '<i class="fa-solid fa-cubes-stacked"></i>',
            "download": '<i class="fa-solid fa-floppy-disk fa-2xl"></i>',
            "go_back": '<i class="fa-solid fa-arrow-left-long fa-xl"></i>',
            "go_to": '<i class="fa-solid fa-arrow-up-right-from-square"></i>',
            "sequence": '<i class="fa-solid fa-arrows-turn-to-dots"></i>',
            "testcase": '<i class="fa-solid fa-list-check"></i>'
        }
    })


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


def save_log(html):
    with open('log.html', 'w', encoding='utf-8') as file:
        file.write(html)


def unrobot(token):
    if token in ['${EMPTY}', '${None}']:
        return ''

    dict_access = re.compile(r'\${(.*)}\[(.*)\]')

    if match := re.match(dict_access, token):
        return f'{match.group(1)}.{match.group(2)}'

    if token.startswith('${') and token.endswith('}'):
        return token.removeprefix('${').removesuffix('}')

    return token


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


class RobotLog:
    def __init__(self):
        self.keyword_args = {}
        self.items = {
            "test_cases": [],
            "keywords": dict()
        }

    def simplify_output(self, input_json: Path, output_json: Path) -> dict:
        with open(input_json, encoding='utf-8') as file:
            input = json.load(file)
            keywords = input['resource']['keywords']
            for keyword in keywords:
                _, name = keyword['name'].split('::')

                self.keyword_args[name] = [unrobot(arg) for arg in keyword.get('args', [])]

        with open(output_json, encoding='utf-8') as file:
            output = json.load(file, object_pairs_hook=parse_object)

        self.items['errors'] = {
            error['message']: error | {'id': str(uuid.uuid4())}
            for error in output['errors']
        }

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

            _, name = name.split('::')

        if 'owner' in step:
            name = step['owner'] + '.' + step['name']

        step_id = str(uuid.uuid4())

        result = {
            'parent_id': parent_id,
            'id': step_id,
            'name': name,
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
            message = step['message']
            result['message'] = message
            messages.add(message)

        if 'body' in step:
            for item in step['body']:
                if item.get('type') == 'MESSAGE' and not item.get('html'):
                    message = item['message']
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
            args = {}
            dict_access = re.compile(r'(\${.*})\[(.*)\]')
            default_arg_names = ['Param %s' % i for i in range(1, len(step['args']) + 1)]

            for arg_name, arg in zip(self.keyword_args.get(name, default_arg_names), step['args']):
                if assign:
                    if match := re.match(dict_access, arg):
                        dict_, item = match.group(1), match.group(2)
                        args[arg_name] = assign[dict_][item]
                else:
                    if level < 2:
                        args[arg_name] = unrobot(arg)
                    else:
                        args[arg_name] = arg

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

        for step in test['body']:
            if 'name' in step:
                simple_step = self.simplify_step(step, test_id)
                step_id = simple_step['id']
                result['steps'].append(step_id)
                self.items['keywords'][step_id] = simple_step

            if step.get('type') == 'FOR':
                for iter in step['body']:
                    for step in iter['body']:
                        assign = {
                            key: json.loads(value.replace("'", '"'))
                            for key, value in iter['assign'].items()
                            if value
                        }
                        simple_step = self.simplify_step(step, test_id, assign=assign)
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
