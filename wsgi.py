import os

import slivka.conf.logging
import slivka.server

home = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('SLIVKA_HOME', home)
slivka.conf.logging.configure_logging()

slivka.server.init()
application = app = slivka.server.create_app()

