import sys
import argparse
import shutil
import pathlib
from warnings import warn

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from . import lib
from .cmap import custom_cmaps


__version__ = "1.3.0"

# NOTE: int or float or str
CONFIG_DEFAULT = dict(
    datafile = "./data.pkl.xz",
    workdir = "./work",
    n = 30,
    n_example = 5,
    col_filename = "id",
    col_img = "img",
    col_label = "label",
    labels = "none",
    label_null = "",
    random = 1,
    imgext = ".png",
    cmap = "",
    vmin = 0.0,
    vmax = 1.0,
    figsize = "4,4",
    backup = 1,
    verbose = 0,
)


class WorkDir(type(pathlib.Path())):
    def clear(self, subdirnames: list, verbose=False) -> None:
        pathstr = str(self)
        if verbose:
            print("clear:", pathstr)
        if self.is_dir():
            shutil.rmtree(pathstr)
        self.mkdir(exist_ok=False)
        for subdirname in subdirnames:
            (self / subdirname).mkdir(exist_ok=False)
        return None


class Data(object):
    def __init__(self, config=dict(), default=CONFIG_DEFAULT) -> None:
        for k in default.keys():
            if k in config:
                self.__setattr__(k, config[k])
            else:
                self.__setattr__(k, default[k])
        if self.verbose:
            print(config)
        return None

    def load(self) -> None:
        self.df = pd.read_pickle(self.datafile)
        if self.col_label not in self.df.columns:
            self.df[self.col_label] = self.label_null
        else:
            self.df[self.col_label] = self.df[self.col_label].astype(str)
        if self.verbose:
            self.info()

        self._index_as_filename =  (self.col_filename == "index") and ("index" not in self.df.columns)
        if self._index_as_filename:
            print("Column 'index' is not found, use df.index instead")
            nunique = self.df.index.nunique()
        else:
            nunique = self.df[self.col_filename].nunique()
        if len(self.df) != nunique:
            raise ValueError(f"Each value of '{self.col_filename}' must be unique")

        for label in self.df[self.col_label].unique():
            if label == self.label_null:
                pass
            elif label not in self.labels:
                print(f"Label '{label}' found")
                self.labels.append(label)

        return None

    def info(self) -> None:
        print("len(df):", len(self.df))
        print("annotated:", (self.df[self.col_label]!=self.label_null).sum())
        return None

    def get_labelled(
        self,
        n: int,
        label: str = None,
        sample: bool = False,
        head: int = False,
    ) -> pd.DataFrame:
        df = self.df
        if label is None:
            _df = df[df[self.col_label]==self.label_null]
        else:
            _df =  df[df[self.col_label]==label]

        if sample and head:
            warn("Both 'sample' and 'head' are selected")
        if n is not None:
            if sample:
                _df = _df.sample(n=min(n,len(_df)))
            if head:
                _df = _df.head(n)
        if self.verbose:
            print("data.get_labelled({}): {}".format(
                "nolabel" if label is None else label,
                len(_df),
            ))

        return _df

    # TODO: customize figsize
    def deploy(self, figsize=None) -> None:
        if figsize is None:
            figsize = self.figsize

        def _saveimg(m, filepath) -> None:
            if self.cmap in custom_cmaps.keys():
                _cmap = LinearSegmentedColormap.from_list(
                    **custom_cmaps[self.cmap])
            else:
                _cmap = self.cmap
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            sns.heatmap(
                m, vmin=self.vmin, vmax=self.vmax, cmap=_cmap,
                cbar=False, xticklabels=[], yticklabels=[], ax=ax)
            plt.savefig(filepath)
            plt.clf()
            plt.close()

        def _saveimgs(df, dirpath: pathlib.Path) -> None:
            for idx, row in df.iterrows():
                if self._index_as_filename:
                    filename = str(idx) + self.imgext
                else:
                    filename = str(row[self.col_filename]) + self.imgext
                filepath = dirpath / filename
                _saveimg(m=row[self.col_img], filepath=str(filepath))

        self.workdir.clear(subdirnames=self.labels)
        _df = self.get_labelled(
            label=None, sample=self.random, head=not self.random, n=self.n)
        _saveimgs(df=_df, dirpath=self.workdir)
        # Examples
        for label in self.labels:
            _df = self.get_labelled(
                label=label, sample=True, n=self.n_example)
            _saveimgs(df=_df, dirpath=(self.workdir / label))
        return None

    def register(self, save=True, backup=None) -> None:
        for labeldir in self.workdir.iterdir():
            if labeldir.is_dir():
                label = labeldir.name
                if label not in self.labels:
                    print(f"Label '{label}' found")
                    self.labels.append(label)
        for label in self.labels:
            filepaths = (self.workdir / label).glob(f"*{self.imgext}")
            for filepath in filepaths:
                name = filepath.name.rstrip(self.imgext)
                if self._index_as_filename:
                    idxs = [int(name)]
                else:
                    idxs = self.df[self.df[self.col_filename]==name].index
                if self.verbose:
                    print("data.register: label={} id={} idx={}".format(
                        label, name, list(idxs)))
                self.df.loc[idxs, self.col_label] = label
        if save:
            self.save(backup=backup)
        return None

    @staticmethod
    def _save(df, filepath, backup=True, backup_suffix="~", verbose=False) -> None:
        if backup and pathlib.Path(filepath).is_file():
            filepath_str = str(filepath)
            filepath_str_back = filepath_str + backup_suffix
            print("backup:", filepath_str_back)
            shutil.copyfile(filepath_str, filepath_str_back)

        if verbose:
            print("data.save:", filepath)
        df.to_pickle(filepath)

    def save(self, backup=None) -> None:
        if backup is None:
            backup = self.backup
        self._save(
            df=self.df, filepath=str(self.datafile),
            backup=backup, verbose=self.verbose)
        self.workdir.clear(subdirnames=[], verbose=self.verbose)
        return None

    def generate_samplefile(
        self, filename="sample.pkl.xz", n=100, backup=None) -> None:
        filepath = self.datafile.parent / filename
        if backup is None:
            backup = self.backup
        imgs = lib.rand.image(n=n)
        ids = lib.rand.string(n=n)

        print(f"generate_samplefile: {filepath}")
        print(f"({n} images, col_filename={self.col_filename}, col_img={self.col_img})")
        df = pd.DataFrame()
        df[self.col_filename] = ids
        df[self.col_img] = list(iter(imgs))
        self._save(
            df=df, filepath=filepath,
            backup=backup, verbose=self.verbose)
        return None


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
    config = lib.config.load(
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
    # Path
    for k in ["datafile"]:
        config[k] = pathlib.Path(config[k]).resolve()
    # WorkDir
    config["workdir"] = WorkDir(config["workdir"])

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
