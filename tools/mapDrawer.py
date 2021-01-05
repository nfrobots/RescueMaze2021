from tkinter import Tk, Canvas, Label
from RMMLIB4 import Mapping, Constants
from PIL import ImageTk, Image

PAD = 10
TILE_DISTANCE = 10

LINE_CONFIG = {
    "width": 4
}

WALL_ACTIVE_COLOR = "#000"
WALL_INACTIVE_COLOR = "#999"

CACHED_IMAGES = None
CACHED_IMAGES_SIZE = None

def load_images(size):
    global CACHED_IMAGES, CACHED_IMAGES_SIZE
    if CACHED_IMAGES_SIZE != size:
        CACHED_IMAGES = {
            Constants.BLACK:  ImageTk.PhotoImage(Image.open("./tools/images/Black.png").resize((size, size))),
            Constants.VICTIM: ImageTk.PhotoImage(Image.open("./tools/images/Victim.png").resize((size, size))),
            Constants.RAMP:   ImageTk.PhotoImage(Image.open("./tools/images/Ramp.png").resize((size, size))),
            "Robot": {
                Constants.Direction.NORTH: ImageTk.PhotoImage(Image.open("./tools/images/Robot.png").resize((size, size))),
                Constants.Direction.WEST:  ImageTk.PhotoImage(Image.open("./tools/images/Robot.png").resize((size, size)).rotate(90)),
                Constants.Direction.SOUTH: ImageTk.PhotoImage(Image.open("./tools/images/Robot.png").resize((size, size)).rotate(180)),
                Constants.Direction.EAST:  ImageTk.PhotoImage(Image.open("./tools/images/Robot.png").resize((size, size)).rotate(270)),
            }
        }
        CACHED_IMAGES_SIZE = size
    return CACHED_IMAGES

def calculate_tile_size(canvas, map):
    canvas_height = max(canvas.winfo_height(), 100)
    canvas_width  = max(canvas.winfo_width(), 100)

    tile_size = min((canvas_height - 2*PAD) // map.sizeY, (canvas_width - 2*PAD) // map.sizeX)
    return tile_size

def draw_map(canvas, map):
    """draw a map on given tk canvas

    Args:
        canvas (tkinter.Canvas): canvas to draw the map on
        map (RMMLIB4.Mapping.Map): map to draw
    """
    canvas.delete("all")

    tile_size = calculate_tile_size(canvas, map)
    D = TILE_DISTANCE // 2
    image_size = tile_size - PAD

    images = load_images(image_size)
    
    for y in range(map.sizeY):
        for x in range(map.sizeX):
            data: Mapping.MazeTile = map.map[y,x]._data

            canvas.create_line(x*tile_size + PAD + D, y*tile_size + PAD + D, x*tile_size + PAD + D, (y+1)*tile_size + PAD - D, **LINE_CONFIG,\
                fill=WALL_ACTIVE_COLOR if data[Constants.Direction.WEST] else WALL_INACTIVE_COLOR)
            canvas.create_line(x*tile_size + PAD + D, y*tile_size + PAD + D, (x+1)*tile_size + PAD - D, y*tile_size + PAD + D, **LINE_CONFIG,\
                fill=WALL_ACTIVE_COLOR if data[Constants.Direction.NORTH] else WALL_INACTIVE_COLOR)
            canvas.create_line(x*tile_size + PAD + D, (y+1)*tile_size + PAD - D, (x+1)*tile_size + PAD - D, (y+1)*tile_size + PAD - D, **LINE_CONFIG,\
                fill=WALL_ACTIVE_COLOR if data[Constants.Direction.SOUTH] else WALL_INACTIVE_COLOR)
            canvas.create_line((x+1)*tile_size + PAD - D, y*tile_size + PAD + D, (x+1)*tile_size + PAD - D, (y+1)*tile_size + PAD - D, **LINE_CONFIG,\
                fill=WALL_ACTIVE_COLOR if data[Constants.Direction.EAST] else WALL_INACTIVE_COLOR)

            if data[Constants.BLACK]:
                canvas.create_image(x*tile_size + PAD + D, y*tile_size + PAD + D, image=images[Constants.BLACK], anchor='nw')
            if data[Constants.VICTIM]:
                canvas.create_image(x*tile_size + PAD + D, y*tile_size + PAD + D, image=images[Constants.VICTIM], anchor='nw')
            if data[Constants.RAMP]:
                canvas.create_image(x*tile_size + PAD + D, y*tile_size + PAD + D, image=images[Constants.RAMP], anchor='nw')

    canvas.create_image(map.robot.x*tile_size + PAD + D, map.robot.y*tile_size + PAD + D, image=images["Robot"][map.robot.direction], anchor='nw')


if __name__ == "__main__":
    root = Tk()
    root.geometry("600x600")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    canvas = Canvas(root)
    canvas.grid(row=0, column=0, sticky='nswe')
    root.update()
    map = Mapping.Map.open("./Pi/out/testmap.json")
    draw_map(canvas, map)

    def updater():
        draw_map(canvas, map)
        root.after(1000, updater)

    root.after(1000, updater)


    root.mainloop()