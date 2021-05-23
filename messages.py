from tkinter import *
from tkinter import simpledialog, filedialog, messagebox


def open_menu():
    win = Tk()

    for i in range(5):
        win.lift()

    win.mainloop()
    return win

def ask_save_nn_as(initialdir="saves"):
    Tk().withdraw()
    return filedialog.asksaveasfilename(
        title="Save NN as",
        initialdir=initialdir,
        filetypes=[("json save file", "*.json")]
    )

def ask_load_nn(initialdir="saves"):
    Tk().withdraw()
    return filedialog.askopenfilename(
        title="Load .json save file",
        initialdir=initialdir,
        filetypes=[("json save file", "*.json")]
    )

def show_error(message=""):
    Tk().withdraw()
    messagebox.showerror(title="Error", message=message)

def show_message(message=""):
    Tk().withdraw()
    messagebox.showinfo(title="Info", message=message)