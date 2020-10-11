from tkinter import Canvas


class ResizingCanvas(Canvas):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.width, self.height = self.winfo_reqwidth(), self.winfo_reqheight()

    def refresh(self):
        new_width, new_height = self.winfo_width(), self.winfo_height()
        scale_width, scale_height = new_width / self.width, new_height / self.height
        self.width, self.height = new_width, new_height
        print(scale_width, scale_height)

        self.scale("all", 0, 0, scale_width, scale_height)

if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()
    root.geometry("400x400")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    cnv = ResizingCanvas(root, bg="#aaa")
    cnv.grid(row=0, column=0, sticky='nswe')

    cnv.create_line(0, 0, 400, 400)

    root.mainloop()