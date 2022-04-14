from configparser import ConfigParser
from random import choices
from string import ascii_letters, digits
from pathlib import Path
from warnings import warn

import numpy as np


class config(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def load(
        file: str = "./config.ini",
        section: str = "DEFAULT",
        encoding: str = None,
        notfound_ok: bool = False,
        default: dict = None,
        cast: bool = False,
        strict_cast: bool = False,
        strict_key: bool = False,
    ) -> dict:
        """Read configuration file and convert its section to dict.

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
        config = ConfigParser()
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

    @staticmethod
    def save(
        data: dict,
        file: str = "./config.ini",
        section: str = "DEFAULT",
        encoding: str = None,
        exist_ok: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Save configuration dict to file.

        Args:
            data (dict): Configuration data (supports single/multiple sections)
            file (str or Path, optional): Configuration file path
            section (str, optional): Section (if single-section data)
            encoding (str, optional): File encoding
            exist_ok (bool, optional): If False and file exists, raise an error.
            overwrite (bool, optional): If True and file exists, overwrite.

        Returns:
            None

        Raises:
            FileExistsError: If `exist_ok` is False and `file` exists.
        """
        filepath = Path(file)
        config = ConfigParser()

        multisection = True
        for v in data.values():
            if not isinstance(v, dict):
                multisection = False
                break

        if multisection:
            config.read_dict(data)
        else:
            config.read_dict({section: data})

        write = True
        if filepath.is_file():
            if overwrite:
                pass
            elif exist_ok:
                write = False
            else:
                raise FileExistsError(str(filepath))
        if write:
            with filepath.open(mode="w", encoding=encoding) as f:
                config.write(f)
        return None


class random(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def image(n=100, shape=[4,4]) -> np.ndarray:
        """Generate random (2d) images.

        Args:
            n (int, optional): Numer of maps
            shape (int, optional): Shape of each map

        Returns:
            numpy.ndarray
        """
        return np.random.random([n] + list(shape))

    @staticmethod
    def string(n=100, l=8) -> list:
        """Generate random strings.

        Args:
            n (int, optional): Numer of strings
            l (int, optional): Length of each string

        Returns:
            list: List of strings

        Raises:
            Exception: If the number is insufficient
        """
        ts = list()
        for _ in range(n * 5):
            t = "".join(
                choices(ascii_letters + digits, k=l))
            if t in ts:
                # Duplicate
                continue
            ts.append(t)
            if len(ts) >= n:
                break
        if len(ts) < n:
            raise Exception()
        return ts
