import json
import logging
from os.path import abspath, expanduser, splitext

import yaml

from the_conf.files.lib import get_fd

logger = logging.getLogger(__name__)


def read_json(path):
    with get_fd(path, 'r') as fd:
        return json.load(fd)


def read_yaml(path):
    with get_fd(path, 'r') as fd:
        return yaml.load(fd.read())


def read(*paths):
    for path in paths:
        path = abspath(expanduser(path.strip()))
        ext = splitext(path)[1][1:]
        if ext in {'yml', 'yaml'}:
            yield read_yaml(path)
        elif ext == 'json':
            yield read_json(path)
        else:
            logger.error("File %r ignored: unknown type (%s)", path, ext)
            continue
