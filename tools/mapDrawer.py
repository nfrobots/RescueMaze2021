import tkinter
import json
from PIL import Image, ImageTk
from pathlib import Path

GLOBAL_IMAGES = {}

W_WIDTH = 1300
W_HEIGHT = 800

linewidth = 3
pad = 7
wallColor = "#000"
emptyColor = "#bbb"

def drawMap(mapData, mapCanvas):
    global GLOBAL_IMAGES
    tileSize = (min(W_WIDTH - 50, W_HEIGHT - 50) - (pad * 2)) / max(mapData["sizeX"], mapData["sizeY"])
    lineLen = tileSize - pad

    roboImg = Image.open(Path(__file__).parent / "images/Robot.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)

    GLOBAL_IMAGES = {
        "VICTIM": ImageTk.PhotoImage(Image.open(Path(__file__).parent / "images/Victim.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "BLACK": ImageTk.PhotoImage(Image.open(Path(__file__).parent / "images/Black.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "RAMP": ImageTk.PhotoImage(Image.open(Path(__file__).parent / "images/Ramp.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "ROBOT": {
            "Direction.NORTH": ImageTk.PhotoImage(roboImg),
            "Direction.SOUTH": ImageTk.PhotoImage(roboImg.rotate(180, Image.BILINEAR)),
            "Direction.WEST": ImageTk.PhotoImage(roboImg.rotate(90, Image.BILINEAR)),
            "Direction.EAST": ImageTk.PhotoImage(roboImg.rotate(270, Image.BILINEAR)),
        }
    }

    mapCanvas.delete("all")

    for posStr in mapData["Map"]:
        x, y = [int(a) for a in posStr.split(',')]

        if mapData["Map"][posStr]["Direction.NORTH"] == True:
            northColor = wallColor
        else:
            northColor = emptyColor
        if mapData["Map"][posStr]["Direction.SOUTH"] == True:
            southColor = wallColor
        else:
            southColor = emptyColor
        if mapData["Map"][posStr]["Direction.EAST"] == True:
            eastColor = wallColor
        else:
            eastColor = emptyColor
        if mapData["Map"][posStr]["Direction.WEST"] == True:
            westColor = wallColor
        else:
            westColor = emptyColor

        px = x * tileSize + pad
        py = y * tileSize + pad

        mapCanvas.create_line(px, py, px + lineLen, py, width=linewidth, fill=northColor)                     #NORTH
        mapCanvas.create_line(px, py + lineLen, px + lineLen, py + lineLen, width=linewidth, fill=southColor) #SOUTH
        mapCanvas.create_line(px + lineLen, py, px + lineLen, py + lineLen, width=linewidth, fill=eastColor)  #EAST
        mapCanvas.create_line(px, py, px, py + lineLen, width=linewidth, fill=westColor)                      #WEST

        if mapData["Map"][posStr]["VICTIM"] == True:
            mapCanvas.create_image(px, py, anchor=tkinter.NW, image=GLOBAL_IMAGES["VICTIM"])

        if mapData["Map"][posStr]["BLACK"] == True:
            mapCanvas.create_image(px, py, anchor=tkinter.NW, image=GLOBAL_IMAGES["BLACK"])

        if mapData["Map"][posStr]["RAMP"] == True:
            mapCanvas.create_image(px, py, anchor=tkinter.NW, image=GLOBAL_IMAGES["RAMP"])

    px = mapData["robotX"] * tileSize + pad
    py = mapData["robotY"] * tileSize + pad
    mapCanvas.create_image(px, py, anchor=tkinter.NW, image=GLOBAL_IMAGES["ROBOT"][mapData["robotDirection"]])


if __name__ == "__main__":
    window = tkinter.Tk()
    window.geometry("{}x{}".format(W_WIDTH, W_HEIGHT))
    window.resizable(0, 0)
    window.configure(bg="white")

    frm = tkinter.Frame(window, relief='flat', borderwidth=4)
    frm.pack(fill=tkinter.BOTH, expand=1)
    cv = tkinter.Canvas(frm)
    cv.pack(fill=tkinter.BOTH, expand=1)

    with open(Path(__file__).parent.parent / "Pi/out/map.json") as f:
        data = json.load(f)

    drawMap(data, cv)

    window.mainloop()