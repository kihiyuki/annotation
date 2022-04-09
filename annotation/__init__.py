import sys
import argparse
import shutil
import pathlib
from warnings import warn

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .lib import read_config, gen_randmaps, gen_randstrs


__version__ = "0.2.0"

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
    vmin = 0.,
    vmax = 2.,
    # figsize = "5,5",
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


def _backupfile(filepath, suffix="~") -> None:
    filepath_str = str(filepath)
    filepath_str_back = filepath_str + suffix
    print("backup:", filepath_str_back)
    shutil.copyfile(filepath_str, filepath_str_back)


class Data(object):
    def __init__(self, config: dict) -> None:
        for k in CONFIG.keys():
            self.__setattr__(k, config[k])
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


def deploy(
    df,
    datafile, workdir, n, n_example, col_filename, col_img, col_label,
    labels, label_null, random, imgext, vmin, vmax, verbose,
    figsize=(5,5),
) -> None:
    def _saveimg(m, filepath) -> None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        sns.heatmap(
            m,
            vmin=vmin, vmax=vmax, cbar=False,
            xticklabels=[], yticklabels=[], ax=ax)
        plt.savefig(filepath)
        plt.clf()
        plt.close()

    def _saveimgs(df, dirpath: pathlib.Path) -> None:
        for _, row in df.iterrows():
            filename = str(row[col_filename]) + imgext
            filepath = dirpath / filename
            _saveimg(m=row[col_img], filepath=str(filepath))

    workdir.clear(subdirnames=labels)
    _df = df[df[col_label]==label_null]
    if random:
        _df = _df.sample(n=min(n,len(_df)))
    else:
        _df = _df.head(n)
    if verbose:
        print("_saveimgs: nolabel", len(_df))
    _saveimgs(df=_df, dirpath=workdir)
    # Examples
    for label in labels:
        _df = df[df[col_label]==label]
        _df = _df.sample(n=min(n_example,len(_df)))
        if verbose:
            print("_saveimgs:", label, len(_df))
        _saveimgs(df=_df, dirpath=(workdir / label))
    return None


def register(
    df,
    datafile, workdir, n, n_example, col_filename, col_img, col_label,
    labels, label_null, random, imgext, vmin, vmax, verbose,
    backup=False,
) -> None:
    for labeldir in workdir.iterdir():
        if labeldir.is_dir():
            label = labeldir.name
            if label not in labels:
                print(f"Label '{label}' found")
                labels.append(label)

    for label in labels:
        filepaths = (workdir / label).glob(f"*{imgext}")
        for filepath in filepaths:
            name = filepath.name.rstrip(imgext)
            idxs = df[df[col_filename]==name].index
            if verbose:
                print("register:", label, name, idxs)
            df.loc[idxs, col_label] = label

    datafile_str = str(datafile)
    # if verbose:
    #     _print_count(df=df, col_label=col_label, label_null=label_null)
    if backup:
        _backupfile(datafile_str, verbose=verbose)
    if verbose:
        print("to_pickle:", datafile_str)
    df.to_pickle(datafile_str)
    workdir.clear(subdirnames=[], verbose=verbose)


def make_sample_datafile(
    datafile, workdir, n, n_example, col_filename, col_img, col_label,
    labels, label_null, random, imgext, vmin, vmax, verbose,
    n_make=1000, backup=False,
) -> None:
    datafile_str = "./sample.pkl.xz"
    imgs = gen_randmaps(n=n_make)
    ids = gen_randstrs(n=n_make)

    df = pd.DataFrame()
    df[col_filename] = ids
    df[col_img] = list(iter(imgs))
    if pathlib.Path(datafile_str).is_file() and backup:
        _backupfile(datafile_str, verbose=verbose)

    # save
    print("to_pickle:", datafile_str)
    df.to_pickle(datafile_str)

    return None


def main(args=None) -> None:
    if args is None:
        args = sys.argv[1:]

    config = CONFIG.copy()
    config_ = read_config(notfound_ok=True)
    for k, v in config_.items():
        if k in config:
            config[k] = type(config[k])(v)
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
    # Path
    for k in ["datafile"]:
        config[k] = pathlib.Path(config[k]).resolve()
    # WorkDir
    config["workdir"] = WorkDir(config["workdir"])
    # None
    # for k in ["label_null"]:
    #     if config[k] == "None":
    #         config[k] = None

    if n_makesample is not None:
        make_sample_datafile(n_make=n_makesample, **config)
        return None

    if is_deploy and is_register:
        raise Exception("Both '--deploy' and '--register' are active")

    if config["verbose"]:
        print(config)

    data = Data(config)
    data.load()

    if is_deploy:
        deploy(df=data.df, **config)

    if is_register:
        register(df=data.df, **config)

    return None
