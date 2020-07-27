from tools import mapDrawer

from tkinter import Tk, Frame, Canvas, Button, Label
from pathlib import Path
import json

BUTTON_CONFIG = {
    'bd': 1,
    'bg': '#fff',
    'activebackground': '#aaa'
}

class App(Tk):
    def __init__(self):
        super().__init__()

        self.state("zoomed")
        self.title("Roboti App")
        self.grid_rowconfigure(0, weight=3) # make module frame expand
        self.grid_columnconfigure(1, weight=3)

        self.module_selector_frame = Frame(self)
        self.module_selector_frame.grid(row=0, column=0, sticky='nswe')

        self.grid_rowconfigure(0, weight=1) # module selector frame expand
        self.grid_columnconfigure(0, weight=1)

        self.module_selectors = {}
        self.modules = {}

        for counter, Module in enumerate(MODULES):
            self.module_selectors[Module] = Button(self.module_selector_frame, text=Module.__name__, cnf=BUTTON_CONFIG, command=lambda Module=Module: self.enable_module(Module))
            self.module_selectors[Module].grid(row=counter, column=0, sticky="nswe")
            self.module_selector_frame.grid_columnconfigure(0, weight=1)
            self.module_selector_frame.grid_rowconfigure(counter, weight=1)

            self.modules[Module] = Module(self)
            self.modules[Module].grid(row=0, column=1, sticky='nswe')

        self.enable_module(Home)
        
        self.update()
        self.after(1000, self.update)

    def enable_module(self, module):
        self.modules[module].tkraise()
        self.active_module = self.modules[module]

    def update(self):
        self.active_module.update()
        self.after(1000, self.update)


class Home(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.text = Label(self, text="w: {}; h: {}".format(self.master.winfo_width(), self.master.winfo_height()))
        self.text.pack()

    def update(self):
        print("update")
        self.text.configure(text="w: {}; h: {}".format(self.master.winfo_width(), self.master.winfo_height()))

class MapVisualisation2(Frame):
    def __init__(self, root):
        super().__init__(root)
        canvas = Canvas(self)
        canvas.pack(fill="both", expand=1)
        with open(Path(__file__).parent.parent / "Pi/out/map.json") as f:
            data = json.load(f)
        mapDrawer.drawMap(data, canvas)

    def update(self):
        pass

class SensorView(Frame):
    def __init__(self, root):
        super().__init__(root)

        self.grid_rowconfigure(1, weight=40)
        self.grid_columnconfigure(0, weight=40)

        self.mode_selector_frame = Frame(self, bg="green")
        self.mode_selector_frame.grid(row=0, column=0, sticky='nswe')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.mode_selectors = {}
        self.modes = {}

        for counter, Mode in enumerate(SENSOR_VIEW_MODES):
            self.mode_selectors[Mode] = Button(self.mode_selector_frame, text=Mode.__name__, command=lambda Mode=Mode: self.enable_mode(Mode))
            self.mode_selectors[Mode].grid(row=0, column=counter, sticky='nswe')
            self.mode_selector_frame.grid_columnconfigure(counter, weight=1)
            self.mode_selector_frame.grid_rowconfigure(0, weight=1)

            self.modes[Mode] = Mode(self)
            self.modes[Mode].grid(row=1, column=0, sticky='nswe')

        self.enable_mode(SENSOR_VIEW_MODES[0])

    def enable_mode(self, mode):
        self.modes[mode].tkraise()
        self.active_mode = self.modes[mode]

    def update(self):
        self.active_mode.update()



class SersorViewNumberMode(Frame):
    def __init__(self, root):
        super().__init__(root, bg="yellow")

    def update(self):
        pass

class SersorViewNumberMode2(Frame):
    def __init__(self, root):
        super().__init__(root, bg="green")

    def update(self):
        pass

SENSOR_VIEW_MODES = (SersorViewNumberMode,SersorViewNumberMode2)

MODULES = (Home, MapVisualisation2, SensorView)

a = App()
a.mainloop()