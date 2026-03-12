import os
import signal
import subprocess
import sys
from os.path import realpath
from pathlib import Path
from threading import Thread
from typing import Optional

from .IProcess import IProcess
from .rf_remote_server import RobotRemoteServer
from .project.settings import BASE_URL, SQLITE_DB


CWD = Path(realpath(__file__)).parent
DJANGO_DIR = CWD
ROBOT_REMOTE_HOST = 'localhost'
ROBOT_REMOTE_PORT = 1471


class DaemonThread(Thread):
    def __init__(self, proc: IProcess, name: Optional[str]=None):
        self.proc = proc
        Thread.__init__(self, daemon=True, name=name, target=proc.run)

    def join(self, timeout: Optional[float]=None) -> None:
        self.proc.stop()
        return super().join(timeout)


def django_runserver():
    host_port = BASE_URL.removeprefix('http://')

    if not SQLITE_DB.exists():
        print('Setting up the database...')
        exec_django_command('migrate')
        exec_django_command('import_library BuiltIn')
    else:
        exec_django_command('migrate')

    return subprocess.Popen(f'python manage.py runserver {host_port}', cwd=DJANGO_DIR, shell=True)


def exec_command(command: str, working_dir: Path=CWD):
    return subprocess.run(command, cwd=working_dir, shell=True, stdout=subprocess.PIPE)


def exec_django_command(command: str):
    return exec_command(f'python manage.py {command}', DJANGO_DIR)


def is_running(app: str):
    return len(list_processes(app)) > 1


def list_processes(proc_name: str):
    if os.name == 'nt':
        return [
            proc 
            for proc in 
            subprocess.check_output(['TASKLIST', '/FI', f'imagename eq {proc_name}.exe']).decode('iso-8859-1').splitlines()
            if proc.startswith(proc_name)
        ]

    return [
        proc 
        for proc in 
        subprocess.check_output(['ps', 'aux']).decode().splitlines()
        if proc.endswith(proc_name)
    ]


def open_keyta():
    open_url(BASE_URL)


def open_url(url):
    exec_command(f'start {url}')


class App:
    def __init__(self, texts: dict[str, str]):
        robot_server = RobotRemoteServer(ROBOT_REMOTE_HOST, ROBOT_REMOTE_PORT)
        # The RF logger only works if the current thread is called MainThread
        self.rf_server_thread = DaemonThread(robot_server, name='MainThread')
        self.icon_thread = None

        if not sys.platform.startswith('linux'):
            from PIL import Image
            from pystray import Icon, Menu, MenuItem # type: ignore
            
            img = Image.open(CWD / 'static' / 'keyta.png')
            img_cropped = img.crop(img.getbbox())
            tray_icon = Icon(
                name='KeyTA',
                title='KeyTA',
                icon=img_cropped,
                menu=Menu(
                    MenuItem(
                        texts['open_keyta'],
                        open_keyta,
                        default=True
                    ),
                    MenuItem(
                        texts['terminate_keyta'],
                        lambda icon, query: self.terminate()
                    )
                )
            )
            self.icon_thread = DaemonThread(tray_icon)

    def run(self):
        self.django_server = django_runserver()
        self.rf_server_thread.start()

        if self.icon_thread:
            self.icon_thread.start()

        try:
            self.django_server.wait()
        except KeyboardInterrupt:
            return

    def terminate(self): # type: ignore
        self.django_server.send_signal(signal.CTRL_C_EVENT)


def keyta():
    texts = {
        'open_keyta': 'Open KeyTA',
        'terminate_keyta': 'Terminate KeyTA'
    }

    if not is_running('keyta'):
        App(texts).run()


def keyta_de():
    os.environ['KEYTA_LANG'] = 'de'
    texts = {
        'open_keyta': 'KeyTA starten',
        'terminate_keyta': 'KeyTA beenden'
    }

    if not is_running('keyta-de'):
        App(texts).run()
