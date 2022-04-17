import subprocess

from tkinter import (
    Tk,
    ttk,
    messagebox,
    Toplevel,
    Entry,
    END,
    W,
)

from . import message
from .lib import config as configlib
from .data import Data, Config


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
    def add(self, text: str, labelkw, gridkw, name: str = None, fullspan=False) -> None:
        object_ = ttk.Label(self.frame, text=text, **labelkw)
        return super().add(object_, gridkw, text, name, fullspan)


def main(data: Data, args, config: dict) -> None:
    def _deploy(event=None):
        r = messagebox.askyesno("Deploy", f"{message.DEPLOY}?")
        if r:
            data.deploy()

    def _register(event=None):
        r = messagebox.askyesno("Register", f"{message.REGISTER}?")
        if r:
            data.register()

    def _open(event=None):
        subprocess.Popen(["explorer",  data.workdir], shell=True)

    def _clear(event=None):
        r = messagebox.askyesno("Clear", f"Clear working directory '{data.workdir.resolve()}'?")
        if r:
            data.workdir.clear()

    def _deploy_result(event=None):
        r = messagebox.askyesno("Register", f"{message.DEPROYRESULT}?")
        if r:
            data.n = 0
            data.n_example = None
            data.deploy()
            data.n = config["n"]
            data.n_example = config["n_example"]

    def _config(event=None):
        def _save(event=None):
            r = messagebox.askyesno("Save config", f"Save to configfile and reload datafile?")
            if r:
                # config_ = Config()
                # for k, entry in entries.items():
                #     config_[k] = entry.get()
                # configlib.save(
                #     {args.config_section: config_},
                #     file=args.config_file,
                #     section=None,
                #     mode="overwrite")
                # config_.conv()
                # data = Data(config_)
                # data.load()
                cw.destroy()

        def _close(event=None):
            cw.destroy()

        cw = Toplevel()
        cw.title("Config")
        cw.resizable(False, False)
        frm = ttk.Frame(cw, padding=20)
        frm.grid()

        gridkw = GridKw(maxcolumn=1)
        labelkw = LabelKw(fontsize=10)

        buttons = Buttons(frm)
        labels = Labels(frm)
        entries = dict()

        config_ = Config(config)
        config_.conv_to_str()
        for k, v in config_.items():
            # ttk.Label(frm, text=).grid(**gridkw.pull())
            labels.add(f"{k}: {message.CONFIG[k]}", labelkw, gridkw, name=k)
            entries[k] = Entry(frm, width=50)
            entries[k].insert(END, str(v))
            entries[k].grid(**gridkw.pull())
        buttons.add("Save", _save, gridkw)
        buttons.add("Cancel", _close, gridkw)

    data.load()

    root = Tk()
    root.title("Annotation tool")
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    gridkw = GridKw(maxcolumn=4)
    labelkw = LabelKw()

    buttons = Buttons(frm)
    labels = Labels(frm)

    for k in ["datafile", "workdir"]:
        labels.add(f"{k}: {data.__getattribute__(k).resolve()}", labelkw, gridkw, name=k, fullspan=True)
    for k in ["all", "annotated"]:
        labels.add(f"data({k}): {data.count(k)}", labelkw, gridkw, name=k, fullspan=True)

    labels.add("Annotation", labelkw.big, gridkw, name="title.annotation", fullspan=True)
    buttons.add("[D]eploy", _deploy, gridkw, name="deploy")
    buttons.add("[R]egister", _register, gridkw, name="register")
    gridkw.lf()

    labels.add("Working directory", labelkw.big, gridkw, name="title.workdir", fullspan=True)
    buttons.add("[O]pen", _open, gridkw, name="open")
    buttons.add("Clear", _clear, gridkw, name="clear")
    gridkw.lf()

    labels.add("Result", labelkw.big, gridkw, name="title.result", fullspan=True)
    buttons.add("Deploy", _deploy_result, gridkw, name="deploy_result")
    gridkw.lf()

    labels.add("----", labelkw.big, gridkw, name="title.tail", fullspan=True)
    buttons.add("Config", _config, gridkw, name="config")
    buttons.add("[Q]uit", root.destroy, gridkw, name="quit")
    gridkw.lf()

    # keybind
    root.bind("d", _deploy)
    root.bind("r", _register)
    root.bind("o", _open)
    root.bind("q", lambda e: root.destroy())

    root.mainloop()
