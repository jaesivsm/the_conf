import logging

from the_conf.files.readers import read
from the_conf.lib import ConfNode

logger = logging.getLogger(__name__)
DEFAULT_ORDER = 'files', 'cmd', 'env'


class TheConf(ConfNode):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *paths):
        super().__init__()
        for config in read(*paths):
            self._source_order = config.get('source_order', DEFAULT_ORDER)
            self._config_files = config.get('config_files', None)
            self._main_conf_file = None

            self._load_parameters(*config['parameters'])
