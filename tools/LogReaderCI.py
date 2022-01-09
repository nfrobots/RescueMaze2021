from RMMLIB4 import Mapping, Constants
from RMMLIB4.Constants import *
from tools import mapDrawer

from tkinter import Frame, Button, filedialog, Canvas


class LogReader(Frame):
    def __init__(self, root):
        super().__init__(root)

        self.map = Mapping.Map(path_pre_expand=True)
        self.instructions = None
        self.index = 0
        self.auto_step = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=5)

        self.button_frame = Frame(self)
        self.button_frame.grid(row=0, column=0, sticky='nswe')
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)

        self.open_button = Button(self.button_frame, text="open file", command=self.open_file)
        self.open_button.grid(row=0, column=0, sticky='nswe')

        self.manual_step_button = Button(self.button_frame, text="step manual", command=self.step)
        self.manual_step_button.grid(row=0, column=1, sticky='nswe')

        self.auto_step_button = Button(self.button_frame, text="step automatically", command=self.toggle_auto_step)
        self.auto_step_button.grid(row=0, column=2, sticky='nswe')

        self.map_canvas = Canvas(self)
        self.map_canvas.grid(row=1, column=0, sticky='nswe')

    def open_file(self):
        file = filedialog.askopenfile()
        if file == None:
            return
        self.instructions = file.readlines()

    def toggle_auto_step(self):
        self.auto_step = not self.auto_step
        self.do_auto_step()

    def do_auto_step(self):
        if self.auto_step == True:
            self.step()
            self.after(300, self.do_auto_step)
    
    def eval_argument(self, argument: str):
        if argument[0] != "<":
            return eval(argument)
        elif argument[0:10] == "<MazeTile:":
            tile = Mapping.MazeTile()
            rawAttributes = argument[11:].replace(">", "").split("\t")
            for rawAttribute in rawAttributes:
                attribute_string, value = rawAttribute.split(": ")
                tile[eval(attribute_string)] = eval(value)
            return tile
        elif argument[0:13] == "<RelDirection":
            rawRelDirection = argument[1:].split(": ")
            return eval(rawRelDirection[0])
        elif argument[0:10] == "<Direction":
            rawDirection = argument[1:].split(": ")
            return eval(rawDirection[0])

    def step(self):
        if self.instructions == None:
            print("[WARGNING] tried to step but no instructions were found")
            return
        instruction = self.instructions[self.index].rstrip()
        self.index = self.index + 1
        print(instruction)

        split_instruction = instruction.split(';')
        function = split_instruction[0]
        raw_args = split_instruction[1][1:-1].split(", ")[1:] # remove first and last char, split args and discard first
        args = [self.eval_argument(a) for a in raw_args]
        return_value = getattr(self.map, function)(*args)

        mapDrawer.draw_map(self.map_canvas, self.map)

        if function == "findPath":
            mapDrawer.draw_path(self.map_canvas, self.map, return_value)
        


    def refresh():
        pass