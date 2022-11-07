import shutil
from pathlib import Path
from typing import Optional
from warnings import warn

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from .cmap import custom_cmaps
from .lib import random as randomlib


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


class Config(dict):
    def conv(self) -> None:
        # bool
        for k in ["random", "backup", "verbose"]:
            self[k] = bool(self[k])
        # int/None
        for k in ["n", "n_example"]:
            if self[k] == "":
                self[k] = None
            else:
                self[k] = int(self[k])
        # float/None
        for k in ["vmin", "vmax"]:
            if self[k] == "":
                self[k] = None
            else:
                self[k] = float(self[k])
        # list(separator=",")
        for k in ["labels", "figsize"]:
            if self[k] == "":
                self[k] = list()
            else:
                self[k] = self[k].split(",")
        # list[float]
        for k in ["figsize"]:
            self[k] = [float(x) for x in self[k]]
        # Path
        for k in ["datafile"]:
            self[k] = Path(self[k])
        # _WorkDir
        self["workdir"] = _WorkDir(self["workdir"])
        # None
        for k in ["cmap"]:
            if self[k] == "":
                self[k] = None
        return None

    def conv_to_str(self) -> None:
        for k, v in self.items():
            if v is None:
                self[k] = ""
            elif type(v) is bool:
                self[k] = str(int(v))
            elif type(v) is list:
                self[k] = ",".join([str(x) for x in v])
            else:
                self[k] = str(v)
        return None


class _WorkDir(type(Path())):
    def clear(
        self,
        subdirnames: Optional[list] = None,
        verbose: bool = False
    ) -> None:
        pathstr = str(self)
        if subdirnames is None:
            subdirnames = list()
        if verbose:
            print("clear:", pathstr)
        if self.is_dir():
            shutil.rmtree(pathstr)
        self.mkdir(exist_ok=False)
        for subdirname in subdirnames:
            (self / subdirname).mkdir(exist_ok=False)
        return None


class Data(object):
    def __init__(self, config: dict = dict(), default: dict = None) -> None:
        self._init(config=config, default=default)
        return None

    def __len__(self) -> int:
        if not self.loaded:
            l = 0
        else:
            l = len(self.df)
        return l

    def _init(self, config: dict, default: dict = None) -> None:
        if default is None:
            default = CONFIG_DEFAULT
        self.loaded = False
        self.df = pd.DataFrame()
        self.__configkeys = list(default.keys())
        for k in self.__configkeys:
            if k in config:
                self.__setattr__(k, config[k])
            else:
                self.__setattr__(k, default[k])

        if self.verbose:
            print(config)
        return None

    def get_config(self, str_=False) -> Config:
        c = Config()
        for k in self.__configkeys:
            c[k] = self.__getattribute__(k)
        if str_:
            c.conv_to_str()
        return c

    def count(self, type: str = "all") -> int:
        type = type.lower()
        if not self.loaded:
            l = 0
        elif type.lower() == "all":
            l =  len(self)
        elif type.lower() == "annotated":
            l =  (self.df[self.col_label]!=self.label_null).sum()
        else:
            raise ValueError(f"Type '{type}' is not defined")
        return l

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
                if self.verbose:
                    print(f"Label '{label}' found")
                self.labels.append(label)

        self.loaded = True
        return None

    def info(self) -> None:
        print("data:", self.count("all"))
        print("annotated:", self.count("annotated"))
        return None

    def get_labelled(
        self,
        n: int,
        label: str = None,
        sample: bool = False,
        head: int = False,
    ) -> pd.DataFrame:
        if not self.loaded:
            warn("Data is not loaded")
            return None

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
        if not self.loaded:
            warn("Data is not loaded")
            return None

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

        def _saveimgs(df, dirpath: Path) -> None:
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

    def register(self, save=True, backup=None) -> tuple:
        if not self.loaded:
            warn("Data is not loaded")
            return None

        n_success = 0
        n_failure = 0
        for labeldir in self.workdir.iterdir():
            if labeldir.is_dir():
                label = labeldir.name
                if label not in self.labels:
                    if self.verbose:
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
                if len(idxs) == 0:
                    warn(f"name '{name}' is not found")
                    n_failure += 1
                    continue

                if self.verbose:
                    print("data.register: label={} id={} idx={}".format(
                        label, name, list(idxs)))
                try:
                    _ = self.df.loc[idxs, self.col_label]
                except KeyError:
                    warn(f"KeyError: idxs = {idxs}")
                    n_failure += 1
                    continue

                n_success += 1
                self.df.loc[idxs, self.col_label] = label

        if save:
            self.save(backup=backup)

        if self.verbose:
            print(f"data.register: n_success={n_success} n_failure={n_failure}")
        return (n_success, n_failure)

    @staticmethod
    def _save(df, filepath, backup=True, backup_suffix="~", verbose=False) -> None:
        if backup and Path(filepath).is_file():
            filepath_str = str(filepath)
            filepath_str_back = filepath_str + backup_suffix
            print("backup:", filepath_str_back)
            shutil.copyfile(filepath_str, filepath_str_back)

        if verbose:
            print("data.save:", filepath)

        df.to_pickle(filepath)
        return None

    def save(self, backup=None) -> None:
        if not self.loaded:
            warn("Data is not loaded")
            return None

        if backup is None:
            backup = self.backup
        self._save(
            df=self.df, filepath=str(self.datafile),
            backup=backup, verbose=self.verbose)
        self.workdir.clear(subdirnames=[], verbose=self.verbose)
        return None

    def create_sample_datafile(
        self,
        filename: str = "sample.pkl.xz",
        n: int = 100,
        backup: Optional[bool] = None
    ) -> None:
        filepath = self.datafile.parent / filename
        if backup is None:
            backup = self.backup
        imgs = randomlib.image(n=n)
        ids = randomlib.string(n=n)

        print(f"create_sample_datafile: {filepath}")
        print(f"({n} images, col_filename={self.col_filename}, col_img={self.col_img})")
        df = pd.DataFrame()
        df[self.col_filename] = ids
        df[self.col_img] = list(iter(imgs))
        self._save(
            df=df, filepath=filepath,
            backup=backup, verbose=self.verbose)
        return None
