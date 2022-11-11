import shutil
from pathlib import Path
from typing import Union, Optional, List, Tuple
from warnings import warn

from tqdm import tqdm
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from .cmap import custom_cmaps
from .lib import random as randomlib


Figsize = Union[List[Union[int, float]], Tuple[Union[int, float]], float, int]
CONFIG_DEFAULT = dict(
    # NOTE: values must be int or float or str
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
    imgext: str = ""
    verbose: bool = False
    labels: List[str] = list()

    def clear(
        self,
        make_labeldirs: bool = True,
    ) -> None:
        if self.verbose:
            print(f"clear: {str(self)}")

        self.mkdir(exist_ok=True, parents=True)

        filepaths = list(self.glob(f"**/*{self.imgext}"))
        if len(filepaths) > 0:
            for filepath in tqdm(filepaths):
                if filepath.is_file():
                    filepath.unlink()
        for dirpath in self.iterdir():
            if dirpath.is_dir():
                try:
                    dirpath.rmdir()
                except Exception:
                    pass

        # make subdirs
        if make_labeldirs:
            for label in self.labels:
                (self / label).mkdir(exist_ok=False)
        return None


class Data(object):
    def __init__(
        self,
        config: dict = dict(),
        default: Optional[dict] = None,
    ) -> None:
        self._init(config=config, default=default)
        return None

    def __len__(self) -> int:
        if not self.loaded:
            l = 0
        else:
            l = len(self.df)
        return l

    def _init(
        self,
        config: dict = dict(),
        default: Optional[dict] = None,
    ) -> None:
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

        # init workdir
        self.workdir = _WorkDir(self.workdir)
        self.workdir.imgext = self.imgext
        self.workdir.verbose = self.verbose
        self.workdir.labels = self.labels

        if self.verbose:
            print(config)
        return None

    def get_config(self, str: bool = False) -> Config:
        c = Config()
        for k in self.__configkeys:
            c[k] = self.__getattribute__(k)
        if str:
            c.conv_to_str()
        return c

    def count(self, type: str = "all") -> int:
        """
        Args:
            type: ['all', 'annotated']
        """
        type = type.lower()
        if not self.loaded:
            l = 0
        elif type == "all":
            l =  len(self)
        elif type == "annotated":
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
            print(self.info())

        self._index_as_filename = (self.col_filename == "index") and ("index" not in self.df.columns)
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
        label: Optional[str] = None,
        sample: bool = False,
        head: int = 0,
    ) -> pd.DataFrame:
        if not self.loaded:
            warn("Data is not loaded")
            return None

        df = self.df
        if label is None:
            _df = df[df[self.col_label]==self.label_null]
        else:
            _df = df[df[self.col_label]==label]

        if sample and (head > 0):
            warn("Both 'sample' and 'head' are selected")
        if n is not None:
            if sample:
                _df = _df.sample(n=min(n,len(_df)))
            if head > 0:
                _df = _df.head(n)
        if self.verbose:
            print("data.get_labelled({}): {}".format(
                "nolabel" if label is None else label,
                len(_df),
            ))

        return _df

    def deploy(
        self,
        figsize: Optional[Figsize] = None
    ) -> None:
        if not self.loaded:
            warn("Data is not loaded")
            return None

        if figsize is None:
            figsize = self.figsize
        if type(figsize) in (tuple, list):
            if len(figsize) == 1:
                figsize = (figsize[0], figsize[0])
            elif len(figsize) == 2:
                pass
            else:
                raise ValueError("len(figsize) must be 2")
        else:  # float or int
            figsize = (figsize, figsize)

        def _save_img(m, filepath) -> None:
            if self.cmap in custom_cmaps.keys():
                _cmap = LinearSegmentedColormap.from_list(
                    **custom_cmaps[self.cmap]
                )
            else:
                _cmap = self.cmap

            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            sns.heatmap(
                m, vmin=self.vmin, vmax=self.vmax, cmap=_cmap,
                cbar=False, xticklabels=[], yticklabels=[], ax=ax)
            fig.savefig(filepath)
            fig.clf()
            plt.close()

        def _save_imgs(df, dirpath: Path) -> None:
            # sort
            if self._index_as_filename:
                _idxs = df.index.sort_values()
            else:
                _idxs = df.sort_values(self.col_filename).index
            if len(_idxs) == 0:
                return None

            # draw and save
            for idx in tqdm(_idxs):
                row = df.loc[idx]
                if self._index_as_filename:
                    filename = str(idx) + self.imgext
                else:
                    filename = str(row[self.col_filename]) + self.imgext
                filepath = dirpath / filename
                _save_img(m=row[self.col_img], filepath=str(filepath))
            return None

        self.workdir.clear()
        _df = self.get_labelled(
            label=None, sample=self.random, head=not self.random, n=self.n)
        _save_imgs(df=_df, dirpath=self.workdir)
        # Examples
        for label in self.labels:
            _df = self.get_labelled(
                label=label, sample=True, n=self.n_example)
            _save_imgs(df=_df, dirpath=(self.workdir / label))
        return None

    def register(
        self,
        save: bool = True,
        backup: Optional[bool] = None,
    ) -> tuple:
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

    def export(
        self,
        filepath: Union[Path, str],
        filetype: str = "csv",
        verbose: bool = False,
    ) -> None:
        _df = pd.DataFrame(index=self.df.index)
        if self._index_as_filename:
            _df["id"] = self.df.index
        else:
            _df["id"] = self.df[self.col_filename]
        _df["label"] = self.df[self.col_label]

        if filetype == "csv":
            _df.to_csv(filepath, index=True)
        else:
            raise ValueError("filetype must be in ['csv']")
        if verbose:
            print(f"data.export: {filepath}")
        return None

    @staticmethod
    def _save_pickle(
        df: pd.DataFrame,
        filepath: Union[Path, str],
        backup: bool = True,
        backup_suffix: str = "~",
        verbose: bool = False,
    ) -> None:
        if backup and Path(filepath).is_file():
            s_filepath = str(filepath)
            s_filepath_back = s_filepath + backup_suffix
            if verbose:
                print(f"backup: {s_filepath_back}")
            shutil.copyfile(s_filepath, s_filepath_back)

        if verbose:
            print(f"data.save: {s_filepath}")

        df.to_pickle(filepath)
        return None

    def save(self, backup: Optional[bool] = None) -> None:
        if not self.loaded:
            warn("Data is not loaded")
            return None

        if backup is None:
            backup = self.backup
        self._save_pickle(
            df=self.df,
            filepath=self.datafile,
            backup=backup,
            verbose=self.verbose
        )
        self.workdir.clear(make_labeldirs=False)
        return None

    def create_sample_datafile(
        self,
        filename: str = "sample.pkl.xz",
        n: int = 100,
        backup: Optional[bool] = None,
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
        self._save_pickle(
            df=df,
            filepath=filepath,
            backup=backup,
            verbose=self.verbose,
        )
        return None
