import logging

TYPE_MAPPING = {'int': int, 'str': str, 'list': list, 'dict': dict, 'bool': bool}
logger = logging.getLogger(__name__)


class ConfNode:

    def __init__(self, parent=None, *parameters):
        self._parent = parent
        self._parameters = {}
        self._load_parameters(*parameters)

    def _load_parameters(self, *parameters):
        for parameter in parameters:
            for name, value in parameter.items():
                if isinstance(value, list) and not hasattr(self, name):
                    setattr(self, name, ConfNode(self, *value))
                elif isinstance(value, list):
                    getattr(self, name)._load_parameters(*value)
                else:
                    self._load_parameter(name, value)

    def _load_parameter(self, name, settings):
        if name in self._parameters:
            logger.debug('ignoring')
            return
        assert 'type' in settings
        # FIXME something smarter that'd allow custom type
        settings['type'] = TYPE_MAPPING[settings['type']]
        has_default = bool(settings.get('default'))
        has_among = bool(settings.get('among'))
        settings['required'] = bool(settings.get('required'))
        settings['read_only'] = bool(settings.get('read_only'))
        if has_among:
            assert isinstance(settings['among'], list)
        if has_default and has_among:
            assert settings.get('default') in settings.get('among')
        if has_default and settings['required']:
            assert False, "required parameter can't have default value"
        self._parameters[name] = settings
        if settings.get('default'):
            setattr(self, name, settings['default'])

    def __setattr__(self, key, value):
        if key.startswith('_') or isinstance(value, ConfNode):
            return super().__setattr__(key, value)
        if key not in self._parameters:
            raise Exception('%r is unknown' % key)
        if 'among' in self._parameters[key]:
            assert value in self._parameters[key]['among']
        if 'type' in self._parameters[key]:
            value = self._parameters[key]['type'](value)
        return super().__setattr__(key, value)
