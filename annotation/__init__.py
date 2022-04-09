import sys
import argparse
import shutil
from pathlib import Path
from warnings import warn

# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .lib import read_config


__version__ = "0.1.1"

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
)


def _cleardir(dirpath: Path, subdirnames: list, verbose=False) -> None:
    dirpath_str = str(dirpath)
    if verbose:
        print("clear:", dirpath_str)
    if dirpath.is_dir():
        shutil.rmtree(dirpath_str)
    dirpath.mkdir(exist_ok=False)
    for subdirname in subdirnames:
        (dirpath / subdirname).mkdir(exist_ok=False)
    return None


def _print_count(df, col_label, label_null) -> None:
    print("len(df):", len(df))
    # if label_null is None:
    #     print("annotated:", len(df) - df[col_label].isna().sum())
    print("annotated:", (df[col_label]!=label_null).sum())


def _read_pickle(
    datafile, workdir, n, n_example, col_filename, col_img, col_label,
    labels, label_null, random, imgext, vmin, vmax, verbose,
) -> pd.DataFrame:
    df = pd.read_pickle(datafile)
    if col_label not in df.columns:
        df[col_label] = label_null
    else:
        df[col_label] = df[col_label].astype(str)
    if verbose:
        _print_count(df=df, col_label=col_label, label_null=label_null)
    if len(df) != df[col_filename].nunique():
        raise ValueError(f"Each value of '{col_filename}' must be unique")
    return df


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

    def _saveimgs(df, dirpath: Path) -> None:
        for _, row in df.iterrows():
            filename = str(row[col_filename]) + imgext
            filepath = dirpath / filename
            _saveimg(m=row[col_img], filepath=str(filepath))

    _cleardir(dirpath=workdir, subdirnames=labels)
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
    if verbose:
        _print_count(df=df, col_label=col_label, label_null=label_null)
    if backup:
        datafile_str_back = datafile_str + "~"
        if verbose:
            print("backup:", datafile_str_back)
        shutil.copyfile(datafile_str, datafile_str_back)
    if verbose:
        print("to_pickle:", datafile_str)
    df.to_pickle(datafile_str)
    _cleardir(dirpath=workdir, subdirnames=[], verbose=verbose)


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

    pargs = parser.parse_args(args=args)
    is_deploy = bool(pargs.deploy)
    is_register = bool(pargs.register)
    config["verbose"] = bool(pargs.verbose)
    if pargs.file is not None:
        config["datafile"] = pargs.file
    if pargs.workdir is not None:
        config["workdir"] = pargs.workdir

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
    for k in ["datafile", "workdir"]:
        config[k] = Path(config[k]).resolve()
    # None
    # for k in ["label_null"]:
    #     if config[k] == "None":
    #         config[k] = None

    if is_deploy and is_register:
        raise Exception("Both '--deploy' and '--register' are active")

    if config["verbose"]:
        print(config)

    df = _read_pickle(**config)
    for label in df[config["col_label"]].unique():
        if label == config["label_null"]:
            pass
        elif label not in config["labels"]:
            print(f"Label '{label}' found")
            config["labels"].append(label)

    if is_deploy:
        deploy(df=df, **config)

    if is_register:
        register(df=df, **config)

    return None
