import io
import json
import os
import re
import tempfile
import threading
import unicodedata
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zlib import crc32

from jinja2 import Environment, PackageLoader
from robot.libdoc import libdoc_cli
from robot.run import run
from robot.running import TestSuite

from .IProcess import IProcess
from .rf_log import RobotLog, save_log, translate


global_storage = {}
global_storage_lock = threading.Lock()
tmp_dir = Path(tempfile.gettempdir()) / 'KeyTA'


def export_robot_file(testsuite: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    robot_file = dest_dir / 'Testsuite.robot'

    with open(robot_file, 'w', encoding='utf-8') as file_handle:
        file_handle.write(testsuite)

    return robot_file


def format_filename(testsuite_name: str):
    slug = slugify(testsuite_name)

    if len(slug) > 64:
        return f'{slug[:64]}_{crc32(slug.encode())}'

    return slug


def get_keywords(robot_file: Path) -> list:
    suite = TestSuite.from_file_system(robot_file).to_dict()
    keywords = suite['resource']['keywords']
    tmp_dir = Path(tempfile.gettempdir()) / 'KeyTA'

    for import_ in suite['resource']['imports']:
        import_name = import_['name']
        libdoc_json = str(tmp_dir / f'{import_name}.json')
        libdoc_cli([import_name, libdoc_json], exit=False)

        with open(libdoc_json, 'r', encoding='utf-8') as file:
            libdoc_dict = json.load(file)

            for keyword in libdoc_dict['keywords']:
                args = []

                for arg in keyword['args']:
                    name = arg['name']
                    kind = arg['kind']

                    if name:
                        if kind == 'VAR_POSITIONAL':
                            args.append('*' + name)
                        elif kind == 'VAR_NAMED':
                            args.append('**' + name)
                        else:
                            args.append(name)

                keywords.append({
                    'name': f'{import_name.removesuffix(".resource")}.{keyword["name"]}',
                    'args': args
                })

    return keywords


def robot_run(testsuite_name: str, testsuite: str, execution_state: dict):
    testsuite_fs_name = format_filename(testsuite_name)
    dest_dir = tmp_dir / testsuite_fs_name
    robot_file = export_robot_file(testsuite, dest_dir)
    output_dir = dest_dir / 'output'
    output_file = output_dir / 'output.json'
    robot_kwargs = {
        'listener': 'keyta.Listener',
        'maxassignlength': '1000', # RF truncates return values larger than this in the log
        'outputdir': output_dir,
        'output': 'output.json'
    }

    result = run(str(robot_file), **robot_kwargs, stdout=io.StringIO(), stderr=io.StringIO())
    log_data = RobotLog(testsuite_name).simplify_output(get_keywords(robot_file), output_file)
    log_file = save_log(testsuite_fs_name, log_data, output_dir)
    robot_result = {
        'log': str(log_file.relative_to(tmp_dir)),
        'result': 'PASS' if result == 0 else 'FAIL'
    }

    with global_storage_lock:
        global_storage.update(**execution_state)
        global_storage.update(**log_data)
        global_storage.update(**robot_result)

    return robot_result


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    source: django.utils.text.slugify
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.functions = {
            'robot_run': robot_run
        }
        super().__init__(request, client_address, server_class, directory=str(Path(__file__).resolve().parent))

    def do_GET(self):
        if self.path.endswith('exec-error'):
            with global_storage_lock:
                failed_step = global_storage['failed_step']
                failed_step.update(**global_storage['keywords'][failed_step['id']])
                env = Environment(loader=PackageLoader('keyta.rf_log', package_path='templates'))
                env.filters['translate'] = translate
                template = env.get_template('failed_step.jinja.html')
                response = template.render({'step': failed_step}).encode('utf-8')
                self.send_response(HTTPStatus.OK)
                self.send_header("Access-Control-Allow-Origin", '*')
                self.send_header("Content-type", 'text/html')
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        if self.path.endswith('log-icon'):
            with global_storage_lock:
                log = global_storage['log']
                icon = '<i class="fa-regular fa-file-lines" style="font-size: 36px"></i>'
                url =  f'http://127.0.0.1:1471/{log}'

                response = f'<a href="{url}" target="_blank">{icon}</a>'.encode('utf-8')

                self.send_response(HTTPStatus.OK)
                self.send_header("Access-Control-Allow-Origin", '*')
                self.send_header("Content-type", 'text/html')
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        if self.path.endswith('result-icon'):
            with global_storage_lock:
                icon = ''
                result = global_storage['result']

                if result == 'FAIL':
                    icon = '<i class="fa-solid fa-circle-xmark" style="color: #dc3545; font-size: 36px"></i>'

                if result == 'PASS':
                    icon = '<i class="fa-solid fa-circle-check" style="color: green; font-size: 36px"></i>'

                response = str(icon).encode('utf-8')

                self.send_response(HTTPStatus.OK)
                self.send_header("Access-Control-Allow-Origin", '*')
                self.send_header("Content-type", 'text/html')
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        if self.path.endswith('.html') or self.path.endswith('.jpg') or self.path.endswith('.png') or self.path.endswith('.robot'):
            path = Path(str(tmp_dir) + self.path)

            if path.exists():
                self.send_response(HTTPStatus.OK)
                if self.path.endswith('.html'):
                    self.send_header("Content-type", 'text/html')
                if self.path.endswith('.jpg'):
                    self.send_header("Content-type", 'image/jpeg')
                if self.path.endswith('.png'):
                    self.send_header("Content-type", 'image/png')
                if self.path.endswith('.robot'):
                    self.send_header("Content-type", 'text/plain')
                self.send_header("Content-Length", str(os.stat(path).st_size))
                self.end_headers()

                with open(path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                message = f"The file '{path}' does not exist.".encode('utf-8')
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header("Content-type", 'text/plain')
                self.send_header("Content-Length", str(len(message)))
                self.end_headers()
                self.wfile.write(message)
        elif Path(self.path).suffix in {'.css', '.js', '.woff2'}:
            super().do_GET()
        else:
            self.send_response(HTTPStatus.OK)
            self.send_header("Access-Control-Allow-Origin", '*')
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header('Access-Control-Allow-Methods', self.headers.get('Access-Control-Request-Method'))
        self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin'))
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()

    def do_POST(self):
        function = self.path.lstrip('/')
        kwargs = self.get_request_body()
        result = self.functions[function](**kwargs)
        response = json.dumps(result).encode('utf-8')

        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", '*')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def get_request_body(self) -> dict:
        content_len = int(self.headers.get('content-length'))
        data = self.rfile.read(content_len).decode('utf-8')

        if data:
            return json.loads(data, strict=False)
        else:
            return {}


class RobotRemoteServer(IProcess, ThreadingHTTPServer):
    def __init__(self, host: str, port: int):
        super().__init__((host, port), RequestHandler)

    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()
