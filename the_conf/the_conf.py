import logging

from the_conf.files import read, extract_values
from the_conf.node import ConfNode

logger = logging.getLogger(__name__)
DEFAULT_ORDER = 'cmd', 'files', 'env'


class TheConf(ConfNode):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *paths):
        self._source_order = DEFAULT_ORDER
        self._config_files = None
        self._main_conf_file = None

        super().__init__()
        for path, ext, meta_config in read(*paths):
            if self._source_order is DEFAULT_ORDER:
                self._source_order \
                        = meta_config.get('source_order', DEFAULT_ORDER)
            if self._config_files is None:
                self._config_files = meta_config.get('config_files', None)

            self._load_parameters(*meta_config['parameters'])
        self.load()

    def load_files(self):
        for config_file, ext, config in read(*self._config_files):
            paths = self._get_all_parameters_path()
            for path, value in extract_values(paths, config, config_file):
                self._set_to_path(path, value)

    def load_cmd(self):
        pass

    def load_env(self):
        pass

    def load(self):
        for order in self._source_order:
            if order == 'files':
                self.load_files()
            elif order == 'cmd':
                self.load_cmd()
            elif order == 'env':
                self.load_env()
            else:
                raise Exception('unknown order %r')
