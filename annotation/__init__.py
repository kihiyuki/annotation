import sys
import argparse
import shutil
import pathlib
from warnings import warn

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from .lib import read_config, gen_randmaps, gen_randstrs
from .cmap import custom_cmaps


__version__ = "1.1.0"

# NOTE: int or float or str
CONFIG = dict(
    datafile = "./data.pkl.xz",
    workdir = "./work",
    n = 30,
    n_example = 5,
    col_filename = "id",
    col_img = "img",
    col_label = "label",
    labels = "A,B,C,none",
    label_null = "",
    random = 1,
    imgext = ".png",
    cmap = "",
    vmin = 0.,
    vmax = 1.,
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
    def __init__(self, config=dict()) -> None:
        for k in CONFIG.keys():
            if k in config:
                self.__setattr__(k, config[k])
            else:
                self.__setattr__(k, CONFIG[k])
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
        if len(self.df) != self.df[self.col_filename].nunique():
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
        label: str = None,
        sample: bool = False,
        head: int = False,
        n: int = None,
    ) -> pd.DataFrame:
        df = self.df
        if label is None:
            _df = df[df[self.col_label]==self.label_null]
        else:
            _df =  df[df[self.col_label]==label]

        if sample and head:
            warn("Both 'sample' and 'head' are selected")
        if n is None:
            n = self.n
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
    def deploy(self, figsize=(5,5)) -> None:
        def _saveimg(m, filepath) -> None:
            if self.cmap in custom_cmaps.keys():
                _cmap = LinearSegmentedColormap.from_list(
                    **custom_cmaps[self.cmap])
            else:
                _cmap = self.cmap
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            sns.heatmap(
                m,
                vmin=self.vmin, vmax=self.vmax,
                cmap=_cmap, cbar=False,
                xticklabels=[], yticklabels=[], ax=ax)
            plt.savefig(filepath)
            plt.clf()
            plt.close()

        def _saveimgs(df, dirpath: pathlib.Path) -> None:
            for _, row in df.iterrows():
                filename = str(row[self.col_filename]) + self.imgext
                filepath = dirpath / filename
                _saveimg(m=row[self.col_img], filepath=str(filepath))

        self.workdir.clear(subdirnames=self.labels)
        _df = self.get_labelled(label=None, sample=self.random, head=not self.random)
        _saveimgs(df=_df, dirpath=self.workdir)
        # Examples
        for label in self.labels:
            _df = self.get_labelled(label=label, sample=True, n=self.n_example)
            _saveimgs(df=_df, dirpath=(self.workdir / label))
        return None

    def register(self, save=True, backup=True) -> None:
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

    def save(self, backup=True) -> None:
        self._save(
            df=self.df, filepath=str(self.datafile),
            backup=backup, verbose=self.verbose)
        self.workdir.clear(subdirnames=[], verbose=self.verbose)
        return None

    def save_samplefile(
        self, filepath="./sample.pkl.xz", n=1000, backup=True) -> None:
        imgs = gen_randmaps(n=n)
        ids = gen_randstrs(n=n)

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

    config = CONFIG.copy()
    config_ = read_config(notfound_ok=True)
    for k, v in config_.items():
        if k in config:
            try:
                # cast to original type (CONFIG[k])
                config[k] = type(config[k])(v)
            except ValueError:
                config[k] = v
        else:
            warn(f"'{k}' is an invalid key")

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
        help="Datafile(Pickle)")
    parser.add_argument(
        "--workdir", "-w",
        required=False, default=None,
        help="Working directory")
    parser.add_argument(
        "--makesample",
        required=False, default=None,
        help="Make sample datafile (number)")

    pargs = parser.parse_args(args=args)
    is_deploy = bool(pargs.deploy)
    is_register = bool(pargs.register)
    config["verbose"] = bool(config["verbose"] + pargs.verbose)
    if pargs.file is not None:
        config["datafile"] = pargs.file
    if pargs.workdir is not None:
        config["workdir"] = pargs.workdir
    if pargs.makesample is not None:
        n_makesample = int(pargs.makesample)
    else:
        n_makesample = None

    # bool
    for k in ["random"]:
        config[k] = bool(config[k])
    # list(separator=",")
    for k in ["labels"]:
        if config[k] == "":
            config[k] = list()
        else:
            config[k] = config[k].split(",")
    # None
    for k in ["cmap", "vmin", "vmax"]:
        if config[k] == "":
            config[k] = None
    # Path
    for k in ["datafile"]:
        config[k] = pathlib.Path(config[k]).resolve()
    # WorkDir
    config["workdir"] = WorkDir(config["workdir"])

    data = Data(config)

    if n_makesample is not None:
        data.save_samplefile(n=n_makesample)
        return None

    if is_deploy and is_register:
        raise Exception("Both '--deploy' and '--register' are active")

    data.load()

    if is_deploy:
        data.deploy()

    if is_register:
        data.register()

    return None
