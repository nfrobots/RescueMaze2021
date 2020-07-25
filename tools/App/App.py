from tkinter import Tk, Frame, Canvas, Button

BUTTON_CONFIG = {
    'bd': 1,
    'height': 3,
    'width': 30,
    'bg': '#fff',
    'activebackground': '#aaa',
    'relief': 'flat',
}

class App(Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1920x1080")
        self.title("Roboti App")

        self.module_selector_frame = Frame(self)
        self.module_selector_frame.grid(row=0, column=0, sticky='nswe')

        self.module_selectors = {}
        self.modules = {}

        for module in MODULES:
            self.module_selectors[module] = Button(self.module_selector_frame, text=module.__name__, cnf=BUTTON_CONFIG, command=lambda module=module: self.enable_module(module))
            self.module_selectors[module].pack()

            self.modules[module] = module(self)
            self.modules[module].grid(row=0, column=1, sticky='nswe')

    def enable_module(self, module):
        self.modules[module].tkraise()



class MapVisualisation(Frame):
    def __init__(self, root):
        super().__init__(root)
        canvas = Canvas(self)
        canvas.create_rectangle(100, 10, 60, 60, fill='#222')
        canvas.create_text(300, 50, fill="darkblue", text="MAP")
        canvas.pack(fill="both", expand=1)

class MapVisualisation2(Frame):
    def __init__(self, root):
        super().__init__(root)
        canvas = Canvas(self)
        canvas.create_rectangle(100, 10, 60, 60, fill='#222')
        canvas.create_text(300, 50, fill="yellow", text="MAP")
        canvas.pack(fill="both", expand=1)

MODULES = (MapVisualisation,MapVisualisation2)

a = App()
a.mainloop()