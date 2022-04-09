import configparser
from pathlib import Path


def read_config(
    file: str = "./config.ini",
    section: str = "DEFAULT",
    encoding: str = None,
    notfound_ok: bool = False,
) -> dict:
    filepath = Path(file)
    config = configparser.ConfigParser()
    if filepath.is_file():
        with filepath.open(mode="r", encoding=encoding) as f:
            config.read_file(f)
    elif not notfound_ok:
        raise FileNotFoundError(file)
    return dict(config[section])
