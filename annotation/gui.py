import subprocess
from tkinter import Tk, ttk, messagebox
from .data import Data


def main(data: Data) -> None:
    def _deploy(event=None):
        r = messagebox.askyesno("Deploy", "Deploy data to working directory?")
        if r:
            data.deploy()

    def _register(event=None):
        r = messagebox.askyesno("Register", "Register annotation result to datafile?")
        if r:
            data.register()

    def _open(event=None):
        subprocess.Popen(["explorer",  data.workdir], shell=True)

    root = Tk()
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    row = 0
    ttk.Label(frm, text="Annotation tool").grid(column=0, row=row, columnspan=2)

    for k in ["datafile", "workdir"]:
        row += 1
        ttk.Label(frm, text=f"{k}: {data.__getattribute__(k)}").grid(column=0, row=row, columnspan=2)

    row += 1
    ttk.Label(frm, text=f"data: {data.count('all')}").grid(column=0, row=row, columnspan=3)

    row += 1
    ttk.Label(frm, text=f"annotated: {data.count('annotated')}").grid(column=0, row=row, columnspan=3)

    row += 1
    ttk.Button(frm, text="[D]eploy", command=_deploy).grid(column=0, row=row)
    ttk.Button(frm, text="[R]egister", command=_register).grid(column=1, row=row)

    row += 1
    ttk.Button(frm, text="[O]pen", command=_open).grid(column=0, row=row)

    row += 1
    ttk.Button(frm, text="Config", command=None).grid(column=0, row=row)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=row)

    # keybind
    root.bind("d", _deploy)
    root.bind("r", _register)
    root.bind("o", _open)

    root.mainloop()
