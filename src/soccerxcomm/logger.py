import sys
import threading
from datetime import datetime

from termcolor import cprint


class Logger:
    _FORMAT = ""

    _lock = threading.Lock()

    def __init__(self, namespace: str) -> None:
        super().__init__()

        gettrace = getattr(sys, "gettrace", None)
        if gettrace is not None and gettrace():
            self._debug = True
        else:
            self._debug = False

        self._namespace = namespace

    def debug(self, message: str) -> None:
        if not self._debug:
            return

        with Logger._lock:
            cprint(f'{Logger._get_current_time_string()} ',
                   color='cyan', end='')
            cprint(f'DEBUG ', color='dark_grey', end='')
            cprint(f'[{self._namespace}] {message}', color='dark_grey', end='')
            print()

    def info(self, message: str) -> None:
        with Logger._lock:
            cprint(f'{Logger._get_current_time_string()} ',
                   color='cyan', end='')
            cprint(f'INFO  ', color='blue', end='')
            cprint(f'[{self._namespace}] {message}', color='white', end='')
            print()

    def warn(self, message: str) -> None:
        with Logger._lock:
            cprint(f'{Logger._get_current_time_string()} ',
                   color='cyan', end='')
            cprint(f'WARN  ', color='yellow', end='')
            cprint(f'[{self._namespace}] {message}', color='yellow', end='')
            print()

    def error(self, message: str) -> None:
        with Logger._lock:
            cprint(f'{Logger._get_current_time_string()} ',
                   color='cyan', end='')
            cprint(f'ERROR ', color='red', end='')
            cprint(f'[{self._namespace}] {message}', color='red', end='')
            print()

    @staticmethod
    def _get_current_time_string() -> str:
        return datetime.now().strftime(f'%H:%M:%S')
