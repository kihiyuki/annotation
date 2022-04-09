import configparser
from pathlib import Path
import string
import random

import numpy as np


def read_config(
    file: str = "./config.ini",
    section: str = "DEFAULT",
    encoding: str = None,
    notfound_ok: bool = False,
) -> dict:
    """Read configuration file

    Args:
        file (str, optional): Configuration file path
        section (str, optional): Section
        encoding (str, optional): File encoding
        notfound_ok (bool, optional): If True, return empty dict.

    Returns:
        dict

    Raises:
        FileNotFoundError: If `notfound_ok` is False and `file` not found
    """
    filepath = Path(file)
    config = configparser.ConfigParser()
    if filepath.is_file():
        with filepath.open(mode="r", encoding=encoding) as f:
            config.read_file(f)
    elif not notfound_ok:
        raise FileNotFoundError(file)
    return dict(config[section])


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
