import tkinter as tk
from tkinter.ttk import *

class SettingsMenu:

    def __init__(self):
        self.root = tk.Toplevel()
        self.root.geometry("300x400")
        self.root.configure(bg="white")

        #self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.frame = tk.Frame(self.root)
        self.frame.configure(bg="white")

        self.label = Label(self.frame, text="Settings", font=("Helvetica", 16, "bold"), background="white")

        self.buttons = {
            "new": Button(self.frame, text="New NN"),
            "load": Button(self.frame, text="Load NN"),
            "save": Button(self.frame, text="Save NN"),
            "ok": Button(self.frame, text="Save settings")
        }
        self.widgets = {
            "friction": (
                Label(self.frame, text="Friction"),
                Spinbox(self.frame, from_=0, to=5, width=8)
            ),
            "timeout_seconds": (
                Label(self.frame, text="Time to live"),
                Spinbox(self.frame, width=8)
            ),
            "population": (
                Label(self.frame, text="Population"),
                Spinbox(self.frame, width=8)
            ),
            "mutation_rate": (
                Label(self.frame, text="Mutation rate"),
                Spinbox(self.frame, width=8)
            ),
            "new_track_every_round": (
                Label(self.frame, text="New track after every round"),
                tk.Checkbutton(self.frame)
            )
        }

        # grid config
        for row in range(10):
            tk.Grid.rowconfigure(self.frame, row, weight=1)
        for col in range(2):
            tk.Grid.columnconfigure(self.frame, col, weight=2)
        tk.Grid.columnconfigure(self.frame, 2, weight=1)

        self._place_widgets()

    def set_values(self,
        friction: float,
        timeout_seconds: int,
        population: int,
        mutation_rate: float,
        new_track_every_round: bool
    ):
        self.widgets["friction"][1].insert(0, friction)
        self.widgets["timeout_seconds"][1].insert(0, timeout_seconds)
        self.widgets["population"][1].insert(0, population)
        self.widgets["mutation_rate"][1].insert(0, mutation_rate)

        if new_track_every_round:
            self.widgets["new_track_every_round"][1].select()
        else:
            self.widgets["new_track_every_round"][1].deselect()

    def _place_widgets(self):
        self.frame.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True, padx=30, pady=30)
        self.label.grid(row=0, column=0, columnspan=3)
        i = 1
        for key in ("new", "load", "save"):
            self.buttons[key].grid(row=i, column=0, columnspan=3, sticky="WE")
            i += 1
        for key in self.widgets:
            label, widget = self.widgets[key]
            label.grid(row=i, column=0, columnspan=2, sticky="W")
            widget.grid(row=i, column=2, sticky="E")
            i += 1

        self.buttons["ok"].grid(row=i, column=0, columnspan=3, sticky="WE")

    def run(self):
        self.root.wait_window()

