from configparser import ConfigParser, DEFAULTSECT
from random import choices
from string import ascii_letters, digits
from pathlib import Path
from typing import Optional

import numpy as np


# class ConfigData(dict):


class config(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def _has_section(data: dict) -> bool:
        has_section = True
        for v in data.values():
            if not isinstance(v, dict):
                has_section = False
                break
        return has_section

    @staticmethod
    def _format_section(data: dict, section: Optional[str] = None) -> dict:
        if config._has_section(data):
            if section is None:
                pass
            elif section not in data:
                data[section] = dict()
        else:
            if section is None:
                raise ValueError("data must have section")
            else:
                data = {section: data}
        return data

    @staticmethod
    def load(
        file: str = "./config.ini",
        section: Optional[str] = None,
        encoding: Optional[str] = None,
        notfound_ok: bool = False,
        default: Optional[dict] = None,
        cast: bool = False,
        strict_cast: bool = False,
        strict_key: bool = False,
    ) -> dict:
        """Read configuration file and convert its section to dict.

        Args:
            file (str or Path, optional): Configuration file path
            section (str, optional): Section (If None, load all sections)
            encoding (str, optional): File encoding
            notfound_ok (bool, optional): If True, return empty dict.
            default (dict, optional): Default values of config
            cast (bool, optional): If True, cast to type of default value.
            strict_cast (bool, optional): If False, cast as much as possible.
            strict_key (bool, optional): If False, keys can be added.

        Returns:
            dict

        Raises:
            FileNotFoundError: If `notfound_ok` is False and `file` not found.
            ValueError: If `strict_cast` is True and failed to cast.
            KeyError: If `strict_key` is True and some keys of configfile is not in default.
        """
        filepath = Path(file)
        config_ = ConfigParser()
        if filepath.is_file():
            with filepath.open(mode="r", encoding=encoding) as f:
                config_.read_file(f)
        elif not notfound_ok:
            raise FileNotFoundError(file)

        allsection = section is None
        if allsection:
            sections = config_.sections()
            if len(dict(config_[DEFAULTSECT])) > 0:
                sections = [DEFAULTSECT] + sections
        else:
            sections = [section]

        if default is None:
            default = dict()
        else:
            default = config._format_section(default, section)
            for k in default.keys():
                if k not in sections:
                    sections.append(k)

        data = dict()
        for s in sections:
            if s in default:
                data[s] = default[s].copy()
            else:
                data[s] = dict()
            for k, v in dict(config_[s]).items():
                if k in data[s]:
                    if cast:
                        try:
                            # cast to type(default[k])
                            v = type(data[s][k])(v)
                        except ValueError as e:
                            if strict_cast:
                                raise ValueError(e)
                elif strict_key:
                    raise KeyError(k)
                data[s][k] = v

        if not allsection:
            data = data[section]

        return data

    @staticmethod
    def save(
        data: dict,
        file: str = "./config.ini",
        section: str = None,
        encoding: Optional[str] = None,
        mode: str = "interactive",
    ) -> None:
        """Save configuration dict to file.

        Args:
            data (dict): Configuration data (supports single/multiple sections)
            file (str or Path, optional): Configuration file path
            section (str, optional): Section (if single-section data)
            encoding (str, optional): File encoding
            mode (str, optional): 'interactive', 'overwrite', 'add', 'leave'
            exist_ok (bool, optional): If False and file exists, raise an error.
            overwrite (bool, optional): If True and file exists, overwrite.

        Returns:
            None

        Raises:
            ValueError: If `mode` is unknown
        """
        filepath = Path(file)
        config_ = ConfigParser()

        data = config._format_section(data, section)
        if section is not None:
            # use only specified section
            data = {section: data[section]}

        write = True
        if filepath.is_file():
            mode = mode.lower()
            if mode in ["i", "interactive"]:
                mode = input(f"'{filepath.name}' already exists --> ([o]verwrite/[a]dd/[l]eave/[c]ancel)?: ").lower()
            if mode in ["o", "overwrite"]:
                pass
            elif mode in ["a", "add"]:
                # always load all sections
                data = config.load(
                    file = file,
                    section = None, 
                    encoding = encoding,
                    default = data,
                    cast = False,
                    strict_key = False)
            elif mode in ["l", "leave", "c", "cancel", "n", "no"]:
                write = False
            else:
                raise ValueError(f"Unknown mode '{mode}'")
        if write:
            config_.read_dict(data)
            with filepath.open(mode="w", encoding=encoding) as f:
                config_.write(f)
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
