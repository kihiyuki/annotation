import sys
import argparse

from .lib import config as configlib
from .data import Data, CONFIG_DEFAULT

__version__ = "1.3.0"


def main(args=None) -> None:
    if args is None:
        args = sys.argv[1:]

    # Parse optional arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deploy", "-d",
        action="count", default=0)
    parser.add_argument(
        "--register", "-r",
        action="count", default=0)
    parser.add_argument(
        "--verbose", "-v",
        action="count", default=0)
    parser.add_argument(
        "--file", "-f",
        required=False, default=None,
        help="Pickled pandas.Dataframe file path")
    parser.add_argument(
        "--workdir", "-w",
        required=False, default=None,
        help="Working directory path")
    parser.add_argument(
        "--config-file",
        required=False, default="./config.ini",
        help="Configuration file path")
    parser.add_argument(
        "--config-section",
        required=False, default="DEFAULT",
        help="Configuration section name")
    parser.add_argument(
        "--deploy-result",
        action="count", default=0,
        help="Deploy results (all annotated images)")
    parser.add_argument(
        "--generate-samplefile",
        action="count", default=0,
        help="Generate sample datafile (sample.pkl.xz)")

    pargs = parser.parse_args(args=args)

    # Load configuration file
    config = configlib.load(
        file=pargs.config_file,
        section=pargs.config_section,
        notfound_ok=True,
        default=CONFIG_DEFAULT,
        cast=True,
        strict_cast=False,
        strict_key=True)

    is_deploy = bool(pargs.deploy)
    is_register = bool(pargs.register)
    config["verbose"] = bool(config["verbose"] + pargs.verbose)
    if pargs.file is not None:
        config["datafile"] = pargs.file
    if pargs.workdir is not None:
        config["workdir"] = pargs.workdir
    is_deploy_result = bool(pargs.deploy_result)
    is_generate_samplefile = bool(pargs.generate_samplefile)

    # bool
    for k in ["random", "backup"]:
        config[k] = bool(config[k])
    # list(separator=",")
    for k in ["labels", "figsize"]:
        if config[k] == "":
            config[k] = list()
        else:
            config[k] = config[k].split(",")
    # list[float]
    for k in ["figsize"]:
        config[k] = [float(x) for x in config[k]]
    # None
    for k in ["n", "n_example", "cmap", "vmin", "vmax"]:
        if config[k] == "":
            config[k] = None

    if is_deploy_result:
        # Deploy annotated images only
        is_deploy = True
        config["n"] = 0
        config["n_example"] = None

    # Initialize 'Data' class
    data = Data(config)

    if is_generate_samplefile:
        data.generate_samplefile()
        return None

    if is_deploy and is_register:
        raise Exception("Both '--deploy' and '--register' are active")

    # Load pickle datafile
    data.load()

    if is_deploy:
        data.deploy()

    if is_register:
        data.register()

    return None
