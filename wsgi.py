import logging.config
import os

import slivka

SETTINGS_FILE = 'settings.yml'

settings_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    SETTINGS_FILE
)
slivka.settings.read_yaml_file(settings_path)
slivka.settings.init_logs()
logging.config.dictConfig(slivka.settings.LOGGER_CONFIG)

from slivka.server.forms import FormFactory
from slivka.server.serverapp import app

form_factory = FormFactory()
for configuration in slivka.settings.service_configurations.values():
    form_factory.add_form(configuration)

app.config.update(
    DEBUG=False,
    MEDIA_DIR=slivka.settings.MEDIA_DIR,
    SECRET_KEY=slivka.settings.SECRET_KEY
)
