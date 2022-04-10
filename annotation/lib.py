import configparser
import string
import random
from pathlib import Path
from warnings import warn

import numpy as np


def read_config(
    file: str = "./config.ini",
    section: str = "DEFAULT",
    encoding: str = None,
    notfound_ok: bool = False,
    default: dict = None,
    cast: bool = False,
    strict_cast: bool = False,
    strict_key: bool = False,
) -> dict:
    """Read configuration file

    Args:
        file (str or Path, optional): Configuration file path
        section (str, optional): Section
        encoding (str, optional): File encoding
        notfound_ok (bool, optional): If True, return empty dict.
        default (dict, optional): Default values of config
        cast (bool, optional): If True, cast to type of default value.
        strict_cast (bool, optional): If False, cast as much as possible.
        strict_key (bool, optional): If False, keys can be added, and warn.

    Returns:
        dict

    Raises:
        FileNotFoundError: If `notfound_ok` is False and `file` not found.
        ValueError: If `strict_cast` is True and failed to cast.
        KeyError: If `strict_key` is True and some keys of configfile is not in default.
    """
    filepath = Path(file)
    config = configparser.ConfigParser()
    if filepath.is_file():
        with filepath.open(mode="r", encoding=encoding) as f:
            config.read_file(f)
    elif not notfound_ok:
        raise FileNotFoundError(file)

    if default is None:
        config_d = dict(config[section])
    else:
        config_d_f = dict(config[section])
        config_d = default.copy()
        for k, v in config_d_f.items():
            if k in config_d:
                if cast:
                    try:
                        # cast to type(default[k])
                        config_d[k] = type(config_d[k])(v)
                    except ValueError as e:
                        if strict_cast:
                            raise ValueError(e)
                        else:
                            config_d[k] = v
                else:
                    config_d[k] = v
            elif strict_key:
                raise KeyError(k)
            else:
                warn(f"Key '{k}' is not in default")

    return config_d


def gen_randmaps(n=100, shape=[4,4]) -> np.ndarray:
    """Generate random (2d) maps.

    Args:
        n (int, optional): Numer of maps
        shape (int, optional): Shape of each map

    Returns:
        numpy.ndarray
    """
    return np.random.random([n] + list(shape))


def gen_randstrs(n=100, l=8) -> list:
    """Generate random strings.

    Args:
        n (int, optional): Numer of strings
        l (int, optional): Length of each string

    Returns:
        list: List of strings

    Raises:
        Exception: If the number is insufficient
    """
    names = list()
    for _ in range(n * 5):
        name = "".join(
            random.choices(string.ascii_letters + string.digits, k=l))
        if name in names:
            # Duplicate
            continue
        names.append(name)
        if len(names) >= n:
            break
    if len(names) < n:
        raise Exception()
    return names
