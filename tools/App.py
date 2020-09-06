try:
    import mapDrawer
except ImportError:
    from tools import mapDrawer

from tkinter import Tk, Frame, Canvas, Button, Label, Entry
from pathlib import Path
import json
import inspect

REFRESH_RATE = 500 # milliseconds delay to call refresh functions

ACTIVE_BUTTON_COLOR = '#faa'
INACTIVE_BUTTON_COLOR = '#fff'

BUTTON_CONFIG = {
    'bd': 1,
    'bg': INACTIVE_BUTTON_COLOR,
    'activebackground': '#faf'
}

class App(Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1920x1080")
        self.update_idletasks()
        self.title("Roboti App")
        self.grid_rowconfigure(0, weight=3) # make module frame expand
        self.grid_columnconfigure(1, weight=3)

        self.module_selector_frame = Frame(self)
        self.module_selector_frame.grid(row=0, column=0, sticky='nswe')

        self.grid_rowconfigure(0, weight=1) # module selector frame expand
        self.grid_columnconfigure(0, weight=1)

        self.module_selectors = {} # holds buttons at one of MODULES
        self.modules = {} # holds instances of MODULES

        for counter, Module in enumerate(MODULES):
            self.module_selectors[Module] = Button(self.module_selector_frame, text=Module.__name__, cnf=BUTTON_CONFIG, command=lambda Module=Module: self.enable_module(Module))
            self.module_selectors[Module].grid(row=counter, column=0, sticky="nswe")
            self.module_selector_frame.grid_columnconfigure(0, weight=1)
            self.module_selector_frame.grid_rowconfigure(counter, weight=1)

            self.modules[Module] = Module(self)
            self.modules[Module].grid(row=0, column=1, sticky='nswe')

        self.active_module = self.modules[Home]
        self.enable_module(Home)

        self.refresh()
        self.after(REFRESH_RATE, self.update)

    def enable_module(self, module):
        self.module_selectors[type(self.active_module)].configure(bg=INACTIVE_BUTTON_COLOR)
        self.modules[module].tkraise()
        self.active_module = self.modules[module]
        self.module_selectors[module].configure(bg=ACTIVE_BUTTON_COLOR)

    def refresh(self):
        self.active_module.refresh()
        self.after(REFRESH_RATE, self.refresh)


class Home(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.text = Label(self, text="w: {}; h: {}".format(self.master.winfo_width(), self.master.winfo_height()))
        self.text.pack()

    def refresh(self):
        self.text.configure(text="w: {}; h: {}".format(self.master.winfo_width(), self.master.winfo_height()))


class MapVisualisation2(Frame):
    def __init__(self, root):
        super().__init__(root)
        canvas = Canvas(self)
        canvas.pack(fill="both", expand=1)
        with open(Path(__file__).parent.parent / "Pi/out/map.json") as f:
            data = json.load(f)
        mapDrawer.drawMap(data, canvas)

    def refresh(self):
        pass


class SensorView(Frame):
    def __init__(self, root):
        super().__init__(root)

        self.grid_rowconfigure(1, weight=40)
        self.grid_columnconfigure(0, weight=40)

        self.mode_selector_frame = Frame(self)
        self.mode_selector_frame.grid(row=0, column=0, sticky='nswe')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.mode_selectors = {} # holds buttons at one of SENSOR_VIEW_MODES
        self.modes = {} # holds instances of SENSOR_VIEW_MODES

        for counter, Mode in enumerate(SENSOR_VIEW_MODES):
            self.mode_selectors[Mode] = Button(self.mode_selector_frame, text=Mode.__name__, cnf=BUTTON_CONFIG, command=lambda Mode=Mode: self.enable_mode(Mode))
            self.mode_selectors[Mode].grid(row=0, column=counter, sticky='nswe')
            self.mode_selector_frame.grid_columnconfigure(counter, weight=1)
            self.mode_selector_frame.grid_rowconfigure(0, weight=1)

            self.modes[Mode] = Mode(self)
            self.modes[Mode].grid(row=1, column=0, sticky='nswe')

        self.active_mode = self.modes[SENSOR_VIEW_MODES[0]]
        self.enable_mode(SENSOR_VIEW_MODES[0])

    def enable_mode(self, mode):
        self.mode_selectors[type(self.active_mode)].configure(bg=INACTIVE_BUTTON_COLOR)
        self.modes[mode].tkraise()
        self.active_mode = self.modes[mode]
        self.mode_selectors[mode].configure(bg=ACTIVE_BUTTON_COLOR)

    def refresh(self):
        self.active_mode.refresh()


class SersorViewNumberMode(Frame):
    def __init__(self, root):
        super().__init__(root, bg="yellow")

    def refresh(self):
        pass


class SensorViewGraphMode(Frame):
    def __init__(self, root):
        super().__init__(root, bg="green")

    def refresh(self):
        pass


# should have ratio of about 1.4: eg 28 and 20
N_TILE_WIDHT = 28
N_TILE_HEIGHT = 20

class SersorViewVisualMode(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.width = 0
        self.height = 0
        self.grid_tile_size = 0
        self.pad = 0
        self.figure_ids = []

    def refresh(self):
        self.canvas.delete(*self.figure_ids) # only delete necessary parts, to imporve test performance
        self.figure_ids = []
        new_width, new_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if new_width != self.width or new_height != self.height:
            self.canvas.delete("all")

            self.pad = int(min(new_width, new_height) / 100)
            self.grid_tile_size = int(min((new_height - (2 * self.pad)) / N_TILE_HEIGHT, (new_width - (2 * self.pad)) / N_TILE_WIDHT))
            self.width = new_width
            self.height = new_height
            
            for i in range(N_TILE_WIDHT):
                for j in range(N_TILE_HEIGHT):
                    self.canvas.create_rectangle(self.coord_helper(i, j, i + 1, j + 1), outline="#aaa")

        figure_id = self.canvas.create_rectangle(self.coord_helper(1, 2, 2, 8), fill="#555")
        self.figure_ids.append(figure_id)

    def coord_helper(self, *args):
        return [arg * self.grid_tile_size + self.pad for arg in args]


SENSOR_VIEW_MODES = (SersorViewVisualMode, SersorViewNumberMode, SensorViewGraphMode)


class CommandModule(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.command_frames = {}
        self.parameter_frames = {}
        for counter, command in enumerate(COMMANDS):
            row, column = counter // 3, counter % 3
            self.grid_rowconfigure(row, weight=1)
            self.grid_columnconfigure(column, weight=1)

            # create frame for every command
            self.command_frames[command] = Frame(self)
            self.command_frames[command].grid(column=column, row=row, sticky='nswe')
            self.command_frames[command].grid_rowconfigure(0, weight=1)
            self.command_frames[command].grid_columnconfigure(0, weight=1)

            command_info = inspect.signature(command)
            command_has_parameters = bool(command_info.parameters)

            if command_has_parameters:
                self.parameter_frames[command] = {}
                for counter, (parameter_name, parameter_info) in enumerate(command_info.parameters.items()):
                    self.parameter_frames[command][parameter_name] = Frame(self.command_frames[command])
                    self.parameter_frames[command][parameter_name].grid(column=0, row=counter+1, sticky='nswe')
                    self.command_frames[command].grid_rowconfigure(counter+1, weight=1)

                    self.parameter_frames[command][parameter_name].grid_rowconfigure(0, weight=1)
                    self.parameter_frames[command][parameter_name].grid_columnconfigure(0, weight=1)
                    self.parameter_frames[command][parameter_name].grid_columnconfigure(1, weight=1)

                    Label(self.parameter_frames[command][parameter_name], text=parameter_name).grid(column=0, row=0, sticky='nswe')
                    Entry(self.parameter_frames[command][parameter_name]).grid(column=1, row=0, sticky='nswe')
                

            Button(self.command_frames[command], text=command.__name__, command=lambda c=command: c(), cnf=BUTTON_CONFIG).grid(column=0, row=0, sticky="nswe")

    def refresh(self):
        pass

def say_hello():
    print("hello")

def say_hello2(value, val):
    print("hello"*value)

def moiiin_meister2(a, b=3, *args):
    pass

def moiiin_meister(a, b=3, *args):
    pass

COMMANDS = [say_hello,say_hello2,moiiin_meister,moiiin_meister2]

MODULES = (Home, MapVisualisation2, SensorView, CommandModule)

if __name__ == '__main__':
    a = App()
    a.mainloop()
