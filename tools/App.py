from Pi.InterpreterCI import InterpretedData
from tools import mapDrawer
from tools.mapCreator import MapCreator
from tools.LogReaderCI import LogReader
from tools.ClientCI import Client
from RMMLIB4 import Mapping
from Pi.CalibratorCI import CalibrationTarget


from tkinter import Tk, Frame, Canvas, Button, Label, Entry, END
from pathlib import Path    
import json
import inspect
from inspect import Parameter
import ast


W_WIDTH = 1280
W_HEIGHT = 720

REFRESH_RATE = 100 # milliseconds delay to call refresh functions


BACKGROUND_COLOR = '#555'
ERROR_COLOR = '#e22'

BUTTON_COLOR_ACTIVE = '#faa'
BUTTON_COLOR_INACTIVE = '#777'

BUTTON_CONFIG = {
    'bg': BUTTON_COLOR_INACTIVE,
    'activebackground': BUTTON_COLOR_ACTIVE,
    'highlightthickness': 2,
    'highlightbackground': '#669',
    'bd': 0
}

FRAME_CONFIG = {
    'bg' : BACKGROUND_COLOR
}

ENTRY_CONFIG = {
    'bg': BACKGROUND_COLOR,
    'bd': 0,
    'highlightthickness': 0
}

LABEL_CONFIG = {
    'bg': BACKGROUND_COLOR
}


class App(Tk):
    def __init__(self):
        super().__init__()

        self.geometry(f"{W_WIDTH}x{W_HEIGHT}")
        self.update_idletasks()
        self.title("Roboti App")

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.key_bindings = {}
        self.bind("<Key>", self.on_key_press)
        self.bind("<Button-1>", self.on_mouse_click)

        self.grid_rowconfigure(0, weight=3) # make module frame expand
        self.grid_columnconfigure(1, weight=3)

        self.module_selector_frame = Frame(self, FRAME_CONFIG)
        self.module_selector_frame.grid(row=0, column=0, sticky='nswe')

        self.grid_rowconfigure(0, weight=1) # module selector frame expand
        self.grid_columnconfigure(0, weight=1)

        self.module_selectors = {} # holds buttons at one of MODULES
        self.modules = {} # holds instances of MODULES

        for counter, Module in enumerate(MODULES):
            name = Module.name if hasattr(Module, 'name') else Module.__name__
            self.module_selectors[Module] = Button(self.module_selector_frame, text=name, cnf=BUTTON_CONFIG, command=lambda Module=Module: self.enable_module(Module))
            self.module_selectors[Module].grid(row=counter, column=0, sticky="nswe")
            self.module_selector_frame.grid_columnconfigure(0, weight=1)
            self.module_selector_frame.grid_rowconfigure(counter, weight=1)
            self.modules[Module] = Module(self)
            self.modules[Module].grid(row=0, column=1, sticky='nswe')

            self.key_bindings[counter + 10] = lambda m=Module: self.enable_module(m) # key '1' has keycode 49

        self.active_module = self.modules[Home]
        self.enable_module(Home)

        self.module_selectors["QUIT_BUTTON"] = Button(self.module_selector_frame, text="QUIT", cnf=BUTTON_CONFIG, command=self.on_window_close)
        self.module_selectors["QUIT_BUTTON"].grid(row=len(MODULES), column=0, sticky="nswe")

        self.update()

        for module in self.modules:
            self.modules[module].post_init()

        self.refresh()

    def enable_module(self, module):
        self.active_module.on_deactivation()
        self.module_selectors[type(self.active_module)].configure(bg=BUTTON_COLOR_INACTIVE)
        self.modules[module].tkraise()
        self.active_module = self.modules[module]
        self.module_selectors[module].configure(bg=BUTTON_COLOR_ACTIVE)
        self.active_module.on_activation()

    def refresh(self):
        self.active_module.refresh()
        self.after(REFRESH_RATE, self.refresh)

    def on_window_close(self):
        Client().request_quit()
        self.destroy()

    def on_key_press(self, event):
        self.key_bindings.get(event.keycode, lambda: None)()
        self.active_module.on_key_press(event)

    def on_mouse_click(self, event):
        self.active_module.on_mouse_click(event)

class AbstractModule(Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

    def refresh(self):
        """Is called repetedly. REFRESH_RATE determines time between calls"""
        pass

    def post_init(self):
        """Is called once after all Modules are initialized"""
        pass

    def on_activation(self):
        pass

    def on_deactivation(self):
        pass

    def on_key_press(self, event):
        pass

    def on_mouse_click(self, event):
        pass

class Home(AbstractModule):
    def __init__(self, root):
        super().__init__(root, FRAME_CONFIG)
        self.connect_button = Button(self, text="Connect to Robot", cnf=BUTTON_CONFIG, bg='green', command=Client().connect)
        self.connect_button.pack(expand=1)


class MapVisualisation2(AbstractModule):
    name = "Live Map"
    def __init__(self, root):
        super().__init__(root, FRAME_CONFIG)
        self.canvas = Canvas(self, **ENTRY_CONFIG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas.grid(column=0, row=0, sticky='nswe')

    def refresh(self):
        mapDrawer.draw_map(self.canvas, Mapping.Map.open("./Pi/out/map.json"))

class SensorView(AbstractModule):
    name = "Sensor View"
    def __init__(self, root):
        super().__init__(root, FRAME_CONFIG)

        self.grid_rowconfigure(1, weight=40)
        self.grid_columnconfigure(0, weight=40)

        self.mode_selector_frame = Frame(self, FRAME_CONFIG)
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
        self.mode_selectors[type(self.active_mode)].configure(bg=BUTTON_COLOR_INACTIVE)
        self.modes[mode].tkraise()
        self.active_mode = self.modes[mode]
        self.mode_selectors[mode].configure(bg=BUTTON_COLOR_ACTIVE)

    def refresh(self):
        self.active_mode.refresh()


class SersorViewNumberMode(AbstractModule):
    def __init__(self, root):
        super().__init__(root, bg="yellow")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky='nswe')

    def refresh(self):
        i_data = Client().request_interpreted()
        print(i_data)
        # color = "#fff" if i_data[] > i_data[0] else "#f00"
        color = "#fff"
        self.canvas.create_rectangle(40, 40, 100, 100, fill=color)

class SensorViewGraphMode(AbstractModule):
    def __init__(self, root):
        super().__init__(root, bg="green")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 
        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nswe")
        self.map = Mapping.Map()
    
    def refresh(self):
        i_data: InterpretedData = Client().request_interpreted()
        self.map.set(0, 0, i_data.to_maze_tile(Mapping._Vctr()))
        mapDrawer.draw_map(self.canvas, self.map, width=7)


class SersorViewVisualMode(AbstractModule):
    def __init__(self, root):
        super().__init__(root, FRAME_CONFIG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas = Canvas(self, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.grid(column=0, row=0, sticky='nswe')
        self.t_height = (W_HEIGHT - 100) // 25

    def refresh(self):
        self.canvas.delete("all")
        data = Client().request_data()
        data_iterable = data.items()
        for counter, (key, value) in enumerate(data_iterable):
            if type(value) != list:
                value = round(value, 5)
                self.canvas.create_text(20, counter*self.t_height + 50, text=f"{key}: {value}", anchor='w')
                self.canvas.create_rectangle(200, counter*self.t_height + 40, 200 + value, counter*self.t_height + 60, fill="#000")

SENSOR_VIEW_MODES = (SersorViewVisualMode, SersorViewNumberMode, SensorViewGraphMode)

class CommandModule(AbstractModule):
    name = "Commands"
    def __init__(self, root):
        super().__init__(root, FRAME_CONFIG)
        self.command_frames = {}
        self.parameter_frames = {}
        self.parameter_entries = {}
        for counter, command in enumerate(COMMANDS):
            row, column = counter // 3, counter % 3
            self.grid_rowconfigure(row, weight=1)
            self.grid_columnconfigure(column, weight=1)

            # create frame for every command
            self.command_frames[command] = Frame(self, FRAME_CONFIG, highlightthickness=1, highlightbackground='#444')
            self.command_frames[command].grid(column=column, row=row, sticky='nswe')
            self.command_frames[command].grid_rowconfigure(0, weight=1)
            self.command_frames[command].grid_columnconfigure(0, weight=1)

            command_info = inspect.signature(command)
            
            self.parameter_frames[command] = {}
            self.parameter_entries[command] = {}
            for counter, (parameter_name, parameter_info) in enumerate(command_info.parameters.items()):
                self.parameter_frames[command][parameter_name] = Frame(self.command_frames[command], FRAME_CONFIG)
                self.parameter_frames[command][parameter_name].grid(column=0, row=counter+1, sticky='nswe')
                self.command_frames[command].grid_rowconfigure(counter+1, weight=1)

                self.parameter_frames[command][parameter_name].grid_rowconfigure(0, weight=1)
                self.parameter_frames[command][parameter_name].grid_columnconfigure(0, weight=1)
                self.parameter_frames[command][parameter_name].grid_columnconfigure(1, weight=1)

                Label(self.parameter_frames[command][parameter_name], LABEL_CONFIG, text=parameter_name).grid(column=0, row=0, sticky='nswe')
                self.parameter_entries[command][parameter_name] = Entry(self.parameter_frames[command][parameter_name], bg="#666", bd=0, highlightthickness=1, highlightcolor="#ff4700")
                self.parameter_entries[command][parameter_name].grid(column=1, row=0, sticky='w')

                if parameter_info.default != Parameter.empty:
                    if parameter_info.kind == Parameter.KEYWORD_ONLY:
                        self.parameter_entries[command][parameter_name].insert(0, parameter_name + "=")
                    if type(parameter_info.default) == str:
                        self.parameter_entries[command][parameter_name].insert(END, '"' + parameter_info.default + '"')
                    else:
                        self.parameter_entries[command][parameter_name].insert(END, parameter_info.default)


            Button(self.command_frames[command], text=command.__name__, command=lambda c=command: self.call_command(c), cnf=BUTTON_CONFIG).grid(column=0, row=0, sticky="nswe")

    def parse_var_parameters(self, args):
        """creates list or dict of parameters from string arguments

        Args:
            args (str): args to pass to command_frames

        Returns:
            list/dict: contains parsed values

        Throws:
            ValueError: if eval was not successful
            SyntaxError: if parse was not successful
        """
        if not args:
            return [], {}

        args = 'f({})'.format(args)
        tree = ast.parse(args)
        funccall = tree.body[0].value

        return [ast.literal_eval(arg) for arg in funccall.args], {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}

    def call_command(self, command):
        args = []
        kwargs = {}
        error = False

        def error_occured(entry):
            """indicates error on entry by changeing color for 1 second

            Args:
                entry (tkinter.Entry): entry to indicate error on

            Returns:
                bool: always returns True
            """
            entry.configure(bg=ERROR_COLOR)
            self.after(1000, lambda entry=entry: entry.configure(bg=BACKGROUND_COLOR))
            return True

        for parameter_name, parameter_info in inspect.signature(command).parameters.items():
            parameter_entry = self.parameter_entries[command][parameter_name]
            entered_value = parameter_entry.get()
            if not bool(entered_value) and parameter_info.kind != Parameter.VAR_KEYWORD and parameter_info.kind != Parameter.VAR_POSITIONAL:
                error = error_occured(parameter_entry)
                continue # can not break caus not all empty fields would get colored red
            else:
                if parameter_info.kind == Parameter.POSITIONAL_ONLY or parameter_info.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    try:
                        args.append(eval(entered_value, {}))
                    except Exception as e:
                        print("Error occured:", e)
                        error = error_occured(parameter_entry)
                elif parameter_info.kind == Parameter.VAR_POSITIONAL:
                    try:
                        [args.append(e) for e in self.parse_var_parameters(entered_value)[0]]
                    except Exception as e:
                        print("Error occured:", e)
                        error = error_occured(parameter_entry)
                elif parameter_info.kind == Parameter.KEYWORD_ONLY or parameter_info.kind == Parameter.VAR_KEYWORD:
                    try:
                        for key, value in self.parse_var_parameters(entered_value)[1].items():
                            kwargs[key] = value
                    except Exception as e:
                        print("Error occured:", e)
                        error = error_occured(parameter_entry)

        if error:
            return

        command(*args, **kwargs)


def get_interpreted():
    Client().request_interpreted()

def calibrate(value):
    Client().request_calibration(value)

def calibrate_victim():
    Client().request_calibration(CalibrationTarget.COLOR_RED)

def calibrate_white():
    Client().request_calibration(CalibrationTarget.COLOR_WHITE)

def led(r, g, b):
    Client().request_led(r, g, b)

def animation():
    Client().request_rgb_effect()

COMMANDS = [calibrate, calibrate_victim, calibrate_white, led, animation, get_interpreted]


class MapCreatorModule(AbstractModule):
    name = "Map Creator"
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.map_creator = MapCreator(self)
        self.map_creator.grid(row=0, column=0, sticky='nswe')

    def refresh(self):
        self.map_creator.refresh()

    def on_key_press(self, event):
        self.map_creator.on_key_press(event)

    def on_mouse_click(self, event):
        self.map_creator.on_mouse_click(event)


class LogReaderModule(AbstractModule):
    name = "Log Reader"
    def __init__(self, root):
        super().__init__(root)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.log_reader = LogReader(self)
        self.log_reader.grid(row=0, column=0, sticky='nswe')



MODULES = (Home, CommandModule, MapVisualisation2, SensorView, MapCreatorModule, LogReaderModule)

if __name__ == '__main__':
    a = App()
    a.mainloop()
