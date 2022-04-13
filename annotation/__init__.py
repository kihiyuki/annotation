from argparse import ArgumentParser

from .lib import config as configlib
from .data import Data, CONFIG_DEFAULT

__version__ = "1.3.0"

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
            "--file", "-f",
            required=False, default=None,
            help="Pickled pandas.Dataframe file path")
        self.add_argument(
            "--workdir", "-w",
            required=False, default=None,
            help="Working directory path")
        self.add_argument(
            "--config-file",
            required=False, default="./config.ini",
            help="Configuration file path")
        self.add_argument(
            "--config-section",
            required=False, default="DEFAULT",
            help="Configuration section name")
        self.add_argument(
            "--deploy-result",
            action="count", default=0,
            help="Deploy results (all annotated images)")
        self.add_argument(
            "--generate-samplefile",
            action="count", default=0,
            help="Generate sample datafile (sample.pkl.xz)")

    def parse_args(self, args=None, namespace=None):
        args = super().parse_args(args=args, namespace=namespace)
        args.deploy = bool(args.deploy)
        args.register = bool(args.register)
        args.deploy_result = bool(args.deploy_result)
        args.generate_samplefile = bool(args.generate_samplefile)
        return args

def main(args=None) -> None:
    # Parse optional arguments
    args = Arguments().parse_args(args=args)

    # Load configuration file
    config = configlib.load(
        file=args.config_file,
        section=args.config_section,
        notfound_ok=True,
        default=CONFIG_DEFAULT,
        cast=True,
        strict_cast=False,
        strict_key=True)

    config["verbose"] = bool(config["verbose"] + args.verbose)
    if args.file is not None:
        config["datafile"] = args.file
    if args.workdir is not None:
        config["workdir"] = args.workdir

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

    if args.deploy_result:
        # Deploy annotated images only
        args.deploy = True
        config["n"] = 0
        config["n_example"] = None

    # Initialize 'Data' class
    data = Data(config)

    if args.generate_samplefile:
        data.generate_samplefile()
        return None

    if args.deploy and args.register:
        raise Exception("Both '--deploy' and '--register' are active")

    # Load pickle datafile
    data.load()

    if args.deploy:
        data.deploy()

    if args.register:
        data.register()

    return None
