import json
import tempfile
import subprocess
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from .IProcess import IProcess


def valid_dirname(dirname: str):
    subs = {
        ":": " -",
        "\"": "",
        "/": "",
        "\\": "",
        "?": "",
        "*": "",
        "|": "",
        "<": "",
        ">": ""
    }

    return ''.join([
        subs.get(c,c ) for c in dirname
    ])


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
        testsuite: str,
        robot_args: dict[str, str]
):
    tmp_dir = Path(tempfile.gettempdir()) / 'KeyTA' / valid_dirname(testsuite_name)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    output_dir = tmp_dir / 'output'
    robot_file = tmp_dir / 'Testsuite.robot'
    write_file_to_disk(robot_file, testsuite)

    result = subprocess.run(
        ' '.join(
            ['robot', f'--outputdir="{output_dir}"'] + 
            to_cli_kwargs(robot_args) +
            [f'"{robot_file}"']
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return {
        'log': read_file_from_disk(output_dir / 'log.html'),
        'result': 'PASS' if result.returncode == 0 else 'FAIL'
    }


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.functions = {
            'robot_run': robot_run
        }
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", '*')
        self.end_headers()

    def do_POST(self):
        function = self.path.lstrip('/')
        content_len = int(self.headers.get('content-length'))
        data = self.rfile.read(content_len).decode('utf-8')
        kwargs = json.loads(data, strict=False)
        result = self.functions[function](**kwargs)
        response = json.dumps(result).encode('utf-8')

        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", '*')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


class RobotRemoteServer(IProcess, HTTPServer):
    def __init__(self, host: str, port: int):
        super().__init__((host, port), RequestHandler)

    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()
