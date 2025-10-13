import json
import os
import posixpath
import re
import subprocess
import tempfile
import traceback
import unicodedata
import urllib

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from robot.running import TestSuite

from .IProcess import IProcess
from .rf_log import generate_log, RobotLog


tmp_dir = Path(tempfile.gettempdir()) / 'KeyTA'


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


def read_file_from_disk(path):
    with open(path, 'r', encoding='utf-8') as file_handle:
        return file_handle.read()


def write_file_to_disk(path, file_contents: str):
    with open(path, 'w', encoding='utf-8') as file_handle:
        file_handle.write(file_contents)


def to_cli_kwargs(kwargs: dict[str, str]):
    return [
        f'--{key}={value}'
        for key, value in kwargs.items()
    ]


def robot_run(
    testsuite_name: str,
    testsuite: str
):
    base_dir = tmp_dir / slugify(testsuite_name)
    base_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / 'output'
    robot_file = base_dir / 'Testsuite.robot'
    write_file_to_disk(robot_file, testsuite)

    robot_kwargs = {
        'listener': 'keyta.Listener',
        'maxassignlength': '1000', # RF truncates return values larger than this in the log
        'outputdir': output_dir,
        'output': 'output.json'
    }

    result = subprocess.run(
        ' '.join(['robot', *to_cli_kwargs(robot_kwargs), str(robot_file)]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        suite = TestSuite.from_file_system(robot_file)
        suite.to_json(output_dir / 'input.json', indent=4)
        log = generate_log(RobotLog().simplify_output(output_dir / 'input.json', output_dir / 'output.json'))
        log_path = output_dir / 'simple_log.html'
        write_file_to_disk(log_path, log)
    except:
        traceback.print_exc()
        log_path = output_dir / 'log.html'

    return {
        'log': os.path.relpath(log_path, tmp_dir).replace('\\', '/'),
        'result': 'PASS' if result.returncode == 0 else 'FAIL'
    }


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.functions = {
            'robot_run': robot_run
        }
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        if self.path.endswith('.html'):
            path = tmp_dir / self.translate_path(self.path)

            if path.exists():
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-type", 'text/html')
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

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        source: http.server.SimpleHTTPRequestHandler
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')

        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)

        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = ''

        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)

        if trailing_slash:
            path += '/'

        return path


class RobotRemoteServer(IProcess, ThreadingHTTPServer):
    def __init__(self, host: str, port: int):
        super().__init__((host, port), RequestHandler)

    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()
