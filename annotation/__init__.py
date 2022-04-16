from argparse import ArgumentParser

from . import gui, message
from .lib import config as configlib
from .data import Data, Config, CONFIG_DEFAULT

__version__ = "1.5.1"


class Arguments(ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument(
            "--deploy", "-d",
            action="count", default=0)
        self.add_argument(
            "--register", "-r",
            action="count", default=0)
        self.add_argument(
            "--verbose", "-v",
            action="count", default=0)
        self.add_argument(
            "--gui", "-g",
            action="count", default=0)
        self.add_argument(
            "--file", "-f",
            required=False, default=None,
            help=message.DATAFILE)
        self.add_argument(
            "--workdir", "-w",
            required=False, default=None,
            help=message.WORKDIR)
        self.add_argument(
            "--config-file",
            required=False, default="./config.ini",
            help=message.CONFIGFILE)
        self.add_argument(
            "--config-section",
            required=False, default="annotation",
            help=message.CONFIGSECTION)
        self.add_argument(
            "--deploy-result",
            action="count", default=0,
            help=message.DEPROYRESULT)
        self.add_argument(
            "--create-config-file",
            action="count", default=0,
            help="Create default configuration file")
        self.add_argument(
            "--create-sample-datafile",
            action="count", default=0,
            help="Create sample datafile (sample.pkl.xz)")
        return None

    def parse_args(self, args=None, namespace=None):
        pargs = super().parse_args(args=args, namespace=namespace)
        # deploy if deploy-result
        pargs.deploy += pargs.deploy_result
        # cast to bool
        pargs.deploy = bool(pargs.deploy)
        pargs.register = bool(pargs.register)
        pargs.gui = bool(pargs.gui)
        pargs.deploy_result = bool(pargs.deploy_result)
        pargs.create_config_file = bool(pargs.create_config_file)
        pargs.create_sample_datafile = bool(pargs.create_sample_datafile)
        return pargs


def main(args=None) -> None:
    # Parse optional arguments
    args = Arguments().parse_args(args=args)

    # Load configuration file
    kwargs = dict(
        file=args.config_file,
        section=args.config_section,
        notfound_ok=True,
        default=CONFIG_DEFAULT,
        cast=True,
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

    config["verbose"] = bool(config["verbose"] + args.verbose)
    if args.file is not None:
        config["datafile"] = args.file
    if args.workdir is not None:
        config["workdir"] = args.workdir

    config.conv()

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

    # Initialize 'Data' class
    data = Data(config)

    if args.create_sample_datafile:
        data.create_sample_datafile()
        return None

    if args.gui:
        gui.main(data=data, args=args, config=config)
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
