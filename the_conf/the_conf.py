import logging

from the_conf import files, command_line, node

logger = logging.getLogger(__name__)
DEFAULT_ORDER = 'cmd', 'files', 'env'


class TheConf(node.ConfNode):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *metaconfs, cmd_line_opts=None):
        self._source_order = DEFAULT_ORDER
        self._config_files = None
        self._main_conf_file = None
        self._cmd_line_opts = cmd_line_opts

        super().__init__()
        for mc in metaconfs:
            if isinstance(mc, str):
                _, _, mc = next(files.read(mc))
            if self._source_order is DEFAULT_ORDER:
                self._source_order = mc.get('source_order', DEFAULT_ORDER)
            if self._config_files is None:
                self._config_files = mc.get('config_files', None)

            self._load_parameters(*mc['parameters'])
        self.load()

    def load_files(self):
        if self._config_files is None:
            return
        for config_file, _, config in files.read(*self._config_files):
            paths = (path for path, _, _ in self._get_path_val_param())
            for path, value in files.extract_values(
                    paths, config, config_file):
                self._set_to_path(path, value)

    def load_cmd(self, opts=None):
        parser = command_line.get_parser(self)
        cmd_line_args = parser.parse_args(opts)
        config_file = getattr(cmd_line_args, command_line.CONFIG_OPT_DEST)
        if config_file:
            self._config_files.insert(0, config_file)
        for path, _, _ in self._get_path_val_param():
            value = getattr(cmd_line_args, command_line.path_to_dest(path))
            if value is not None:
                self._set_to_path(path, value)

    def load_env(self):
        pass

    def load(self):
        for order in self._source_order:
            if order == 'files':
                self.load_files()
            elif order == 'cmd':
                self.load_cmd(self._cmd_line_opts)
            elif order == 'env':
                self.load_env()
            else:
                raise Exception('unknown order %r')

        for path, value, param in self._get_path_val_param():
            if value is node.NoValue and param.get('required'):
                raise ValueError('loading finished and %r is not set'
                        % '.'.join(path))

    def extract_config(self):
        config = {}
        for paths, value, param in self._get_path_val_param():
            if value is node.NoValue:
                continue
            if 'default' in param and value == param['default']:
                continue
            curr_config = config
            for path in paths[:-1]:
                curr_config[path] = {}
                curr_config = curr_config[path]
            curr_config[paths[-1]] = value
        return config

    def write(self, config_file=None):
        if config_file is None and not self._config_files:
            raise ValueError('no config file to write in')

        files.write(self.extract_config(),
                config_file or self._config_files[0])
