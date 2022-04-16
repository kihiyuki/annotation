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
from .data import Data


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

    def set(self, row=None, column=None, fullspan=None):
        if row is not None:
            self.row = row
        if column is not None:
            self.column = column
        if (fullspan is not None) and (self.maxcolumn is not None):
            if fullspan:
                self.columnspan = self.maxcolumn
            else:
                self.columnspan = 1

    def pull(self):
        row = self.row
        column = self.column
        columnspan = self.columnspan
        sticky = self.sticky
        self.next()
        return dict(
            row = row,
            column = column,
            columnspan = columnspan,
            sticky = sticky,
        )


def main(data: Data, config: dict) -> None:
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

    def _deploy_result(event=None):
        r = messagebox.askyesno("Register", f"{message.DEPROYRESULT}?")
        if r:
            data.n = 0
            data.n_example = None
            data.deploy()
            data.n = config["n"]
            data.n_example = config["n_example"]

    def _config(event=None):
        cw = Toplevel()
        cw.title("Config")
        cw.resizable(False, False)
        frm = ttk.Frame(cw, padding=20)
        frm.grid()
        gridkw = GridKw(maxcolumn=1)
        entries = dict()
        for k, v in config.items():
            ttk.Label(frm, text=f"{k}: {message.CONFIG[k]}").grid(**gridkw.pull())
            entries[k] = Entry(frm, width=50)
            if v is None:
                v = ""
            elif type(v) is bool:
                v = int(v)
            elif type(v) is list:
                v = ",".join([str(x) for x in v])
            entries[k].insert(END, str(v))
            entries[k].grid(**gridkw.pull())
        ttk.Button(frm, text="Save", command=None).grid(**gridkw.pull())
        ttk.Button(frm, text="Cancel", command=cw.destroy).grid(**gridkw.pull())

    data.load()

    root = Tk()
    root.title("Annotation tool")
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    gridkw = GridKw(maxcolumn=2)
    gridkw.set(fullspan=True)
    for k in ["datafile", "workdir"]:
        gridkw.lf()
        ttk.Label(frm, text=f"{k}: {data.__getattribute__(k)}").grid(**gridkw.pull())

    for t in ["all", "annotated"]:
        gridkw.lf()
        ttk.Label(frm, text=f"{t}: {data.count(t)}").grid(**gridkw.pull())

    gridkw.lf(2)
    ttk.Label(frm, text=f"--- Annotation ---").grid(**gridkw.pull())

    gridkw.set(fullspan=False)
    gridkw.lf()
    ttk.Button(frm, text="[D]eploy", command=_deploy).grid(**gridkw.pull())
    ttk.Button(frm, text="[R]egister", command=_register).grid(**gridkw.pull())
    gridkw.lf()
    ttk.Button(frm, text="[O]pen", command=_open).grid(**gridkw.pull())

    gridkw.set(fullspan=True)
    gridkw.lf(2)
    ttk.Label(frm, text=f"----- Result -----").grid(**gridkw.pull())

    gridkw.set(fullspan=False)
    gridkw.lf()
    ttk.Button(frm, text="Deploy", command=_deploy_result).grid(**gridkw.pull())

    gridkw.set(fullspan=True)
    gridkw.lf(2)
    ttk.Label(frm, text=f"------------------").grid(**gridkw.pull())

    gridkw.set(fullspan=False)
    gridkw.lf()
    ttk.Button(frm, text="Config", command=_config).grid(**gridkw.pull())
    ttk.Button(frm, text="[Q]uit", command=root.destroy).grid(**gridkw.pull())

    # keybind
    root.bind("d", _deploy)
    root.bind("r", _register)
    root.bind("o", _open)
    root.bind("q", lambda e: root.destroy())

    root.mainloop()
