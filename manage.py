#!/usr/bin/env python3

import os
import sys

home = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = 'settings.yaml'


if __name__ == "__main__":
    home = os.environ.get('SLIVKA_HOME', home)
    os.environ.setdefault('SLIVKA_HOME', home)

    settings_path = os.path.join(home, SETTINGS_FILE)
    os.environ.setdefault('SLIVKA_SETTINGS', settings_path)
    sys.path.append(home)
    try:
        import slivka.command
    except ImportError:
        raise ImportError(
            "Couldn't import slivka. Make sure it's installed corectly "
            "and available on you PYTHONPATH environment variable. "
            "Check if you activated virtual environment."
        )
    slivka.command.manager()
