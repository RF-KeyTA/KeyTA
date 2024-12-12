import subprocess
from os.path import realpath
from pathlib import Path
from threading import Thread
from typing import Optional

from PIL import Image
from pystray import Icon, Menu, MenuItem # type: ignore

from .IProcess import IProcess
from .rf_remote_server import RobotRemoteServer
from .project.settings import SQLITE_DB


ROBOT_REMOTE_HOST = 'localhost'
ROBOT_REMOTE_PORT = 1471
CWD = Path(realpath(__file__)).parent
DJANGO_DIR = CWD
DJANGO_PORT = 8000


class DaemonThread(Thread):
    def __init__(self, proc: IProcess, name: Optional[str]=None):
        self.proc = proc
        Thread.__init__(self, daemon=True, name=name, target=proc.run)

    def join(self, timeout: Optional[float]=None) -> None:
        self.proc.stop()
        return super().join(timeout)


class DjangoServer:
    def run(self):
        if not SQLITE_DB.exists():
            print('Setting up the database...')
            exec_django_command('migrate')
            exec_django_command('import_library BuiltIn')
        else:
            exec_django_command('migrate')

        return subprocess.Popen(['cmd', f'/C pushd {DJANGO_DIR} && python manage.py runserver'])


def exit_app(icon: Icon, query): # type: ignore
    """
    Callback for exiting KeyTA

    :param icon: The object of the tray icon
    :param query: The text that is displayed on the pressed menu item
    """

    icon.stop()
    django_server.terminate()


def exec_command(command: str, working_dir: Path=CWD):
    return subprocess.run(command, shell=True, cwd=working_dir, stdout=subprocess.PIPE)


def exec_django_command(command: str):
    return exec_command(f'python manage.py {command}', DJANGO_DIR)


def open_keyta():
    open_url('http://localhost:8000')


def open_url(url):
    exec_command(f'start {url}')


def run():
    rf_server_thread.start()
    icon_thread.start()

    try:
        django_server.wait()
    except KeyboardInterrupt:
        django_server.terminate()


django_server = DjangoServer().run()
robot_server = RobotRemoteServer(ROBOT_REMOTE_HOST, ROBOT_REMOTE_PORT)
# The RF logger only works if the current thread is called MainThread
rf_server_thread = DaemonThread(robot_server, name='MainThread')

img = Image.open(CWD / 'icon.png')
img_cropped = img.crop(img.getbbox())
tray_icon = Icon(
    name='KeyTA',
    title='KeyTA',
    icon=img_cropped,
    menu=Menu(
        MenuItem(
            'KeyTA öffnen',
            open_keyta,
            default=True
        ),
        MenuItem(
            'KeyTA beenden',
            exit_app
        )
    )
)
icon_thread = DaemonThread(tray_icon)
