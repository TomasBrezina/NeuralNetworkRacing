from tkinter import *

class Menu:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("300x500")
        self.root.configure(bg="white")

        self.buttons = {
            "new" : Button(self.root, text="New NN"),
            "load" : Button(self.root, text="Load NN"),
            "save" : Button(self.root, text="Save NN"),
            "ok" : Button(self.root, text="Save settings")
        }
        self.widgets = {
            "friction" : (
                Label(self.root, text="Friction"),
                Spinbox(self.root, from_=0, to=5)
            ),
            "timeout_seconds" : (
                Label(self.root, text="Time to live"),
                Spinbox(self.root)
            ),
            "population" : (
                Label(self.root, text="Population"),
                Spinbox(self.root)
            ),
            "mutation_rate": (
                Label(self.root, text="Mutation rate"),
                Spinbox(self.root)
            ),
            "new_track_every_round": (
                Label(self.root, text="New track after every round"),
                Checkbutton(self.root)
            )
        }


        # grid config
        for row in range(10):
            Grid.rowconfigure(self.root, row, weight=1)
        for col in range(4):
            Grid.columnconfigure(self.root, col, weight=1)

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
        self.buttons["new"].grid(row=0, column=1, columnspan=2, sticky="WE")
        self.buttons["load"].grid(row=1, column=1, columnspan=2, sticky="WE")
        self.buttons["save"].grid(row=2, column=1, columnspan=2, sticky="WE")

        i = 3
        for key in self.widgets:
            label, widget = self.widgets[key]
            label.grid(row=i, column=1)
            widget.grid(row=i, column=2)
            i += 1

        self.buttons["ok"].grid(row=8, column=1, columnspan=2, sticky="WE")

m = Menu()
m.set_values(
    friction=0.5,
    population=10,
    mutation_rate=0.5,
    timeout_seconds=30,
    new_track_every_round=True
)
m.root.mainloop()