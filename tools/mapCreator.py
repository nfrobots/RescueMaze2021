from RMMLIB4 import Mapping, Constants
from tools import mapDrawer
from tkinter import Tk, Canvas, Frame, Button, Checkbutton, BooleanVar, filedialog

from math import floor
import json

REFRESH_TIME = 100


class mapCreator(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x1000")
        self.map = Mapping.Map(neighbours=True)
        self.active_x = 0
        self.active_y = 0

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=10)
        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky='nswe')

        self.grid_columnconfigure(1, weight=1)
        self.edit_frame = Frame(self, bg='#bbb')
        self.edit_frame.grid(row=0, column=1, sticky="nswe")

        self.edit_frame.grid_rowconfigure(0, weight=1)
        self.edit_frame.grid_columnconfigure(0, weight=1)
        self.expand_frame = Frame(self.edit_frame, bg='#ccc')
        self.expand_frame.grid(row=0, column=0, sticky='nswe')
        self.expand_frame.grid_rowconfigure(0, weight=1)
        self.expand_frame.grid_rowconfigure(1, weight=1)
        self.expand_frame.grid_columnconfigure(0, weight=1)
        self.expand_frame.grid_columnconfigure(1, weight=1)
        Button(self.expand_frame, text='expand north', command=lambda: self.map._expand(Constants.Direction.NORTH)).grid(column=0, row=0, sticky="nwse")
        Button(self.expand_frame, text='expand south', command=lambda: self.map._expand(Constants.Direction.SOUTH)).grid(column=1, row=0, sticky="nswe")
        Button(self.expand_frame, text='expand west', command=lambda: self.map._expand(Constants.Direction.WEST)).grid(column=0, row=1, sticky="nswe")
        Button(self.expand_frame, text='expand east', command=lambda: self.map._expand(Constants.Direction.EAST)).grid(column=1, row=1, sticky="nswe")

        self.edit_frame.grid_rowconfigure(1, weight=10)
        self.properties_frame = Frame(self.edit_frame, bg='#aaa')
        self.properties_frame.grid(row=1, column=0, sticky='nswe')
        self.properties_frame.columnconfigure(0, weight=1)

        self.checkbuttons = {}
        self.checkbutton_values = {}
        for counter, property in enumerate(Mapping.MAZE_TILE_TEMPLATE):
            self.checkbutton_values[property] = BooleanVar()
            self.checkbuttons[property] = Checkbutton(self.properties_frame, text=property, variable=self.checkbutton_values[property], command=self.apply_properties, anchor="w", bg="#ccc")
            self.checkbuttons[property].grid(row=counter, column=0, sticky='nswe')

        self.file_frame = Frame(self.edit_frame, bg="#a00")
        self.file_frame.grid(row=2, column=0, sticky='nswe')
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(1, weight=1)
        self.open_file_button = Button(self.file_frame, text="Open", command=self.open_file)
        self.open_file_button.grid(row=0, column=0, sticky='nswe')
        self.save_file_button = Button(self.file_frame, text="Save", command=self.save_file)
        self.save_file_button.grid(row=0, column=1, sticky='nswe')

        self.canvas.update()
        self._rf()
        self.bind("<Button-1>", self.on_mouse_click)
        self.bind("<Key>", self.on_keyboard_press)

    def apply_properties(self):
        for property in Mapping.MAZE_TILE_TEMPLATE:
            if self.map.get(self.active_x, self.active_y)[property] != self.checkbutton_values[property].get():
                self.map.setAttribute(self.active_x, self.active_y, property, self.checkbutton_values[property].get())

    def load_properties(self, x, y):
        for property in Mapping.MAZE_TILE_TEMPLATE:
            self.checkbutton_values[property].set(self.map.get(x, y)[property])

    def open_file(self):
        f = filedialog.askopenfile()
        if f == None:
            return
        self.map = Mapping.Map._restore(json.load(f))
        self.map.apply_to_neighbours = True

    def save_file(self):
        f = filedialog.asksaveasfile()
        if f == None:
            return
        json.dump(self.map._store(), f)

    def _rf(self):
        self.refresh()
        self.after(REFRESH_TIME, self._rf)

    def refresh(self):
        mapDrawer.draw_map(self.canvas, self.map)

    def on_mouse_click(self, event):
        if event.widget == self.canvas:
            tile_size = mapDrawer.calculate_tile_size(self.canvas, self.map)
            self.active_x = min(floor((event.x - mapDrawer.PAD) / tile_size), self.map.sizeX - 1)
            self.active_y = min(floor((event.y - mapDrawer.PAD) / tile_size), self.map.sizeY - 1)
            print(self.active_x, self.active_y)
            self.load_properties(self.active_x, self.active_y)

    def on_keyboard_press(self, event):
        var = None
        if event.char == "8":
            var = self.checkbutton_values[Constants.Direction.NORTH]
        elif event.char == "2":
            var = self.checkbutton_values[Constants.Direction.SOUTH]
        elif event.char == "4":
            var = self.checkbutton_values[Constants.Direction.WEST]
        elif event.char == "6":
            var = self.checkbutton_values[Constants.Direction.EAST]
        if var != None:    
            var.set(not var.get())
            self.apply_properties()


if __name__ == "__main__":
    main = mapCreator()
    main.mainloop()