import subprocess
from tkinter import Tk, ttk, messagebox

from . import message
from .data import Data


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
            n = data.n
            n_example = data.n_example

            data.n = 0
            data.n_example = None
            data.deploy()

            data.n = n
            data.n_example = n_example

    data.load()

    root = Tk()
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    row = 0
    ttk.Label(frm, text="Annotation tool").grid(column=0, row=row, columnspan=2)
    row += 1
    ttk.Label(frm, text=f"------------------").grid(column=0, row=row, columnspan=2)

    row += 1
    for k in ["datafile", "workdir"]:
        row += 1
        ttk.Label(frm, text=f"{k}: {data.__getattribute__(k)}").grid(column=0, row=row, columnspan=2)

    for t in ["all", "annotated"]:
        row += 1
        ttk.Label(frm, text=f"{t}: {data.count(t)}").grid(column=0, row=row, columnspan=2)

    row += 1
    row += 1
    ttk.Label(frm, text=f"--- Annotation ---").grid(column=0, row=row, columnspan=2)
    row += 1
    ttk.Button(frm, text="[D]eploy", command=_deploy).grid(column=0, row=row)
    ttk.Button(frm, text="[R]egister", command=_register).grid(column=1, row=row)
    row += 1
    ttk.Button(frm, text="[O]pen", command=_open).grid(column=0, row=row)

    row += 1
    row += 1
    ttk.Label(frm, text=f"----- Result -----").grid(column=0, row=row, columnspan=2)
    row += 1
    ttk.Button(frm, text="Deploy", command=_deploy_result).grid(column=0, row=row)

    row += 1
    row += 1
    ttk.Label(frm, text=f"------------------").grid(column=0, row=row, columnspan=2)
    row += 1
    ttk.Button(frm, text="Config", command=None).grid(column=0, row=row)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=row)

    # keybind
    root.bind("d", _deploy)
    root.bind("r", _register)
    root.bind("o", _open)

    root.mainloop()
