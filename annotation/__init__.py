from argparse import ArgumentParser
from typing import Optional, List

from . import gui, message
from .lib import config as configlib
from .data import Data, Config, CONFIG_DEFAULT
from .version import __version__


__all__ = (
    "__version__",
    "main",
)


def main(args: Optional[List[str]] = None) -> None:
    parser = ArgumentParser()

    parser_mode = parser.add_mutually_exclusive_group()
    parser_mode.add_argument(
        "--gui", "-g",
        action="store_true")
    parser_mode.add_argument(
        "--deploy", "-d",
        action="store_true")
    parser_mode.add_argument(
        "--register", "-r",
        action="store_true")
    parser_mode.add_argument(
        "--deploy-result",
        action="store_true",
        help=message.DEPROYRESULT)
    parser_mode.add_argument(
        "--create-config-file",
        action="store_true",
        help="Create default configuration file")
    parser_mode.add_argument(
        "--create-sample-datafile",
        action="store_true",
        help="Create sample datafile (sample.pkl.xz)")

    parser.add_argument(
        "--file", "-f",
        required=False, default=None,
        help=message.DATAFILE)
    parser.add_argument(
        "--workdir", "-w",
        required=False, default=None,
        help=message.WORKDIR)
    parser.add_argument(
        "--config-file",
        required=False, default="./config.ini",
        help=message.CONFIGFILE)
    parser.add_argument(
        "--config-section",
        required=False, default="annotation",
        help=message.CONFIGSECTION)
    parser.add_argument(
        "--verbose", "-v",
        action="store_true")

    args = parser.parse_args(args)

    # Load configuration file
    kwargs = dict(
        file=args.config_file,
        section=args.config_section,
        notfound_ok=True,
        default=CONFIG_DEFAULT,
        cast=False,
        strict_cast=False,
        strict_key=True,
    )
    try:
        config = configlib.load(**kwargs)
    except Exception:
        print("configlib.load(section='DEFAULT')")
        kwargs["section"] = "DEFAULT"
        config = configlib.load(**kwargs)

    config = Config(config)
    if args.file is not None:
        config["datafile"] = args.file
    if args.workdir is not None:
        config["workdir"] = args.workdir
    config.conv()
    config["verbose"] = bool(config["verbose"] + args.verbose)

    if args.create_config_file:
        if args.verbose:
            print("create_config_file:", args.config_file)
        configlib.save(
            {args.config_section: CONFIG_DEFAULT},
            file=args.config_file,
            section=None)
        return None

    if args.deploy_result:
        # Deploy annotated images only
        config["n"] = 0
        config["n_example"] = None

    # GUI
    if args.gui:
        gui.main(config=config, args=args)
        return None

    # Initialize 'Data' class
    data = Data(config)

    if args.create_sample_datafile:
        data.create_sample_datafile()
        return None

    if args.deploy and args.register:
        raise Exception("Both '--deploy' and '--register' are active")

    # Load pickle datafile
    data.load()

    if args.deploy:
        data.deploy()
    elif args.register:
        data.register()

    return None
