import re
from typing import Generator, Tuple

from the_conf.utils import Index, NoValue


def iter_on_environ_from_path(
    path: list, environ: dict
) -> Generator[Tuple[list, str], None, None]:
    """Will extract from `environ` all values matching a given path.

    If the given path contains no `Index`, the transformation is
    straighforward: all caps, joined on underscores. This key will be extracted
    from environ if present.
    >>> patern(['eki', 'patang'])
    ... "EKI_PATANG"

    If the given path describe a value being part of a list, the environ keys
    will be matched against a pattern, all matching keys in environ will be
    extracted.
    >>> pattern(["eki", Index, "patang"])
    ... r"EKI_(\\d+)_PATANG"
    >>> matchin(environ)
    ... "EKI_0_PATANG"
    ... "EKI_1_PATANG"
    ... "EKI_10_PATANG"
    """
    if Index not in path:
        env_key = "_".join(map(str.upper, path))
        if env_key in environ:
            yield path, environ[env_key]
    else:
        patterns = []
        indexes_places = []
        for i, elem in enumerate(path):
            if elem is Index:
                patterns.append(r"(\d+)")
                indexes_places.append(i)
            else:
                patterns.append(elem.upper())
        pattern = r"_".join(patterns)
        for environ_key in sorted(environ):
            match = re.match(pattern, environ_key)
            if match:
                amended_path = [
                    elem
                    if i not in indexes_places
                    else int(match.groups()[indexes_places.index(i)])
                    for i, elem in enumerate(path)
                ]
                yield amended_path, environ[environ_key]


def index_to_remove(iterator):
    statuses = {}
    for path, value, _ in iterator:
        if not any(isinstance(key, int) for key in path):
            continue
        path_to_remove = []
        for part in path:
            path_to_remove.append(part)
            if isinstance(part, int):
                break
        path_to_remove = tuple(path_to_remove)
        if value is NoValue:
            if path_to_remove not in statuses:
                statuses[path_to_remove] = "remove"
        else:
            statuses[path_to_remove] = "keep"
    return sorted(
        (key for key, value in statuses.items() if value == "remove"),
        reverse=True,
    )
