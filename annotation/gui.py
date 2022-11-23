import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import (
    Tk,
    ttk,
    filedialog,
    messagebox,
    Toplevel,
    Entry,
    StringVar,
    END,
    W,
)

from .messages import option_messages, config_messages
from .lib import config as configlib
from .data import Data, Config
from .info import __version__, APPNAME, GITHUB


class LabelKw(dict):
    def __init__(self, fontsize=12):
        return super().__init__(
            font = ("", fontsize),
        )

    @property
    def big(self):
        d = self.copy()
        d["font"] = ("", int(d["font"][1] * 1.5))
        return d


class GridKw(object):
    def __init__(self, maxcolumn=None, sticky=W) -> None:
        self.row = 0
        self.column = 0
        self.columnspan = 1
        self.maxcolumn = maxcolumn
        self.sticky = sticky

    def lf(self, n=1):
        self.row += n
        self.column = 0

    def next(self):
        self.column += 1
        if self.maxcolumn is None:
            pass
        elif self.column >= self.maxcolumn:
            self.lf()

    def set(self, row=None, column=None):
        if row is not None:
            self.row = row
        if column is not None:
            self.column = column

    def pull(self, fullspan=False):
        row = self.row
        column = self.column
        sticky = self.sticky
        columnspan = self.columnspan
        if fullspan:
            columnspan = self.maxcolumn
            self.lf()
        else:
            self.next()
        return dict(
            row = row,
            column = column,
            columnspan = columnspan,
            sticky = sticky,
        )


class StringVars(object):
    def __init__(self, keys: list) -> None:
        self._data = dict()
        for k in keys:
            self._data[k] = StringVar()
            self._data[k].set(k)
        return None

    def get(self, key: str):
        return self._data[key]

    def set(self, key: str , value: str) -> None:
        self._data[key].set(value)
        return None


class DatasetInfo(StringVars):
    def __init__(self) -> None:
        super().__init__(["date", "datafile", "workdir", "count_all", "count_annotated"])

    def reload(self, data) -> None:
        self.set("date", str(datetime.now().replace(microsecond=0)))
        for k in ["datafile", "workdir"]:
            self.set(k, f"{k}: {data.__getattribute__(k).resolve()}")
        for k in ["count_all", "count_annotated"]:
            # NOTE: remove 'count_'
            k_ = k[6:]
            self.set(k, f"data({k_}): {data.count(k_)}")


class GridObject(object):
    def __init__(self, frame) -> None:
        self._data = dict()
        self.frame = frame

    def add(self, object_, gridkw: GridKw, text: str = None, name: str = None, fullspan=False) -> None:
        if name is None:
            name = text
        if name in self._data:
            raise ValueError(f"Name '{name}' is always used")
        self._data[name] = object_
        self._data[name].grid(**gridkw.pull(fullspan=fullspan))


class Buttons(GridObject):
    def add(self, text: str, command, gridkw, name: str = None, fullspan=False) -> None:
        object_ = ttk.Button(self.frame, text=text, command=command)
        return super().add(object_, gridkw, text, name, fullspan)


class Labels(GridObject):
    def add(self, text, labelkw, gridkw, name: str = None, fullspan=False) -> None:
        if type(text) is str:
            object_ = ttk.Label(self.frame, text=text, **labelkw)
        else:  # TODO: elif
            object_ = ttk.Label(self.frame, textvariable=text, **labelkw)
        return super().add(object_, gridkw, text, name, fullspan)


class SubWindow(Toplevel):
    def __init__(
        self,
        title: str = "",
        resizable: bool = False,
        padding: int = 20,
        maxcolumn: int = 1,
        fontsize: int = 12,
    ) -> None:
        ret = super().__init__()

        self.title(title)
        self.resizable(resizable, resizable)
        self.grab_set()
        self.focus_set()

        self.frm = ttk.Frame(self, padding=padding)
        self.frm.grid()

        self.gridkw = GridKw(maxcolumn=maxcolumn)
        self.labelkw = LabelKw(fontsize=fontsize)

        self.buttons = Buttons(self.frm)
        self.labels = Labels(self.frm)

        return ret

    def close(self, event=None) -> None:
        self.grab_release()
        self.destroy()
        return None


def main(config, args) -> None:
    data = Data(config)

    class AboutWindow(SubWindow):
        def __init__(self) -> None:
            ret = super().__init__(title="About")

            self.labels.add(APPNAME, self.labelkw.big, self.gridkw, name="APPNAME")
            self.labels.add(GITHUB, self.labelkw, self.gridkw, name="GITHUB")

            self.buttons.add("GitHub", self.open_github, self.gridkw)
            self.buttons.add("Close", self.close, self.gridkw)

            return ret

        def open_github(event=None) -> None:
            webbrowser.open_new(GITHUB)
            return None

    class ConfigWindow(SubWindow):
        def __init__(self) -> None:
            ret = super().__init__(title="Config", fontsize=10)

            self.entries = dict()

            def _diag(k: str, type="file") -> None:
                _initialfile = Path(self.entries[k].get()).resolve()
                _initialdir = _initialfile.parent
                if _initialdir.is_dir():
                    _initialdir = str(_initialdir)
                else:
                    _initialdir = None
                if _initialfile.is_file():
                    _initialfile = _initialfile.name
                else:
                    if _initialfile.is_dir():
                        _initialdir = _initialfile
                    _initialfile = None

                if type == "file":
                    _path = filedialog.askopenfilename(
                        title="Choose a file",
                        initialfile=_initialfile,
                        initialdir=_initialdir,
                    )
                elif type == "dir":
                    _path = filedialog.askdirectory(
                        title="Choose a directory",
                        initialdir=_initialdir,
                    )
                else:
                    raise ValueError("invalid type")

                self.entries[k].delete(0, END)
                self.entries[k].insert(END, _path)

            config = data.get_config(str=True)
            for k, v in config.items():
                self.labels.add(f"{k}: {config_messages.__getattribute__(k)}", self.labelkw, self.gridkw, name=k)
                self.entries[k] = Entry(self.frm, width=80)
                self.entries[k].insert(END, str(v))
                self.entries[k].grid(**self.gridkw.pull())
                if k == "datafile":
                    self.buttons.add("Browse", lambda: _diag("datafile", type="file"), self.gridkw, name=f"datafile_btn")
                elif k == "workdir":
                    self.buttons.add("Browse", lambda: _diag("workdir", type="dir"), self.gridkw, name=f"workdir_btn")
                elif k == "cmapfile":
                    self.buttons.add("Browse", lambda: _diag("cmapfile", type="file"), self.gridkw, name=f"cmapfile_btn")

            self.buttons.add("Save[Enter]", self.save, self.gridkw, name="save")
            self.buttons.add("Cancel[ESC]", self.close, self.gridkw, name="cancel")

            # keybind
            self.bind("<Return>", self.save)
            self.bind("<Escape>", self.close)

            return ret

        def save(self, event=None) -> None:
            config = Config()
            for k, entry in self.entries.items():
                config[k] = entry.get()
            if data.get_config(str=True) == config:
                self.close()
                messagebox.showinfo("Config", "Nothing changed.")
            else:
                r = messagebox.askyesno("Save config", f"Save to configfile and reload datafile?")
                if r:
                    # save
                    configlib.save(
                        {args.config_section: config},
                        file=args.config_file,
                        section=None,
                        mode="overwrite",
                        backup=True)

                    # reload
                    config.conv()
                    self.close()
                    _reload(config=config)
                    messagebox.showinfo("Config", "Saved.")
            return None

    def _deploy(event=None):
        r = messagebox.askyesno("Deploy", f"{option_messages.deploy}?")
        if r:
            data.deploy()

    def _register(event=None):
        r = messagebox.askyesno("Register", f"{option_messages.register}?")
        if r:
            n_success, n_failure = data.register()
            messagebox.showinfo("Register", f"{n_success} registration completed, {n_failure} failed")
            datasetinfo.reload(data)

    def _open(event=None):
        subprocess.Popen(["explorer",  data.workdir], shell=True)

    def _clear(event=None):
        r = messagebox.askyesno("Clear", f"{option_messages.clearworkdir} '{data.workdir.resolve()}'?")
        if r:
            data.workdir.clear()

    def _deploy_result(event=None):
        r = messagebox.askyesno("Register", f"{option_messages.deployresult}?")
        if r:
            config = data.get_config()
            data.n = 0
            data.n_example = None
            data.deploy()
            data.n = config["n"]
            data.n_example = config["n_example"]

    def _export(event=None):
        export_file = filedialog.asksaveasfilename(
            filetypes = [("CSV file", ".csv")],
            defaultextension = "csv",
            title="Export",
            initialfile = "{}_{}.csv".format(
                data.datafile.name,
                datetime.now().strftime("%Y%m%d%H%M%S"),
            ),
        )
        if len(export_file) == 0:
            return None
        try:
            data.export(filepath=export_file)
        except Exception as e:
            messagebox.showwarning("Export failed", e)
        else:
            messagebox.showinfo("Export", f"Successfully saved.")

    def _reload(event=None, config=None):
        if config is not None:
            data._init(config)
        try:
            data.load()
        except Exception as e:
            messagebox.showwarning("Data load failed", e)
        datasetinfo.reload(data)

    def _about(event=None):
        aw = AboutWindow()

    def _close(event=None):
        root.destroy()

    def _config(event=None):
        cw = ConfigWindow()

    root = Tk()
    root.title(APPNAME)
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    gridkw = GridKw(maxcolumn=4)
    labelkw = LabelKw()

    buttons = Buttons(frm)
    labels = Labels(frm)

    datasetinfo = DatasetInfo()
    _reload(config=config)

    labels.add(datasetinfo.get("date"), labelkw, gridkw, name="date", fullspan=True)
    labels.add("Dataset info", labelkw.big, gridkw, name="title.d", fullspan=True)
    for k in ["datafile", "workdir"]:
        labels.add(datasetinfo.get(k), labelkw, gridkw, name=k, fullspan=True)
    for k in ["count_all", "count_annotated"]:
        labels.add(datasetinfo.get(k), labelkw, gridkw, name=k, fullspan=True)

    labels.add("Annotating", labelkw.big, gridkw, name="title.a", fullspan=True)
    buttons.add("[D]eploy", _deploy, gridkw, name="deploy")
    buttons.add("[R]egister", _register, gridkw, name="register")
    gridkw.lf()

    labels.add("Working directory", labelkw.big, gridkw, name="title.w", fullspan=True)
    buttons.add("[O]pen", _open, gridkw, name="open")
    buttons.add("Clear", _clear, gridkw, name="clear")
    gridkw.lf()

    labels.add("Result", labelkw.big, gridkw, name="title.r", fullspan=True)
    buttons.add("Deploy", _deploy_result, gridkw, name="deploy_result")
    buttons.add("Export", _export, gridkw, name="export")
    gridkw.lf()

    labels.add("----", labelkw.big, gridkw, name="title.t", fullspan=True)
    buttons.add("Config", _config, gridkw, name="config")
    buttons.add("Reload[F5]", _reload, gridkw, name="reload")
    buttons.add("Quit[Esc]", _close, gridkw, name="quit")
    gridkw.lf()

    # keybind
    root.bind("d", _deploy)
    root.bind("r", _register)
    root.bind("o", _open)
    root.bind("<F1>", _about)
    root.bind("<F5>", _reload)
    root.bind("<Escape>", _close)

    root.mainloop()
