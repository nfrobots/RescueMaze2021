import tkinter
import json
from PIL import Image, ImageTk

GLOBAL_IMAGES = {}

W_WIDTH = 1000
W_HEIGHT = 1000

def drawMap(mapData, mapCanvas):
    global GLOBAL_IMAGES
    linewidth = 3
    pad = 7
    tileSize = (min(W_WIDTH, W_HEIGHT) - (pad * 2)) / max(mapData["sizeX"], mapData["sizeY"])
    lineLen = tileSize - pad
    wallColor = "#000"
    emptyColor = "#bbb"
    GLOBAL_IMAGES = {
        "VICTIM": ImageTk.PhotoImage(Image.open("tools/images/Victim.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "BLACK": ImageTk.PhotoImage(Image.open("tools/images/Black.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "RAMP": ImageTk.PhotoImage(Image.open("tools/images/Ramp.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
        "ROBOT": {
            "Direction.NORTH": ImageTk.PhotoImage(Image.open("tools/images/Robot.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
            "Direction.SOUTH": ImageTk.PhotoImage(Image.open("tools/images/Robot.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR).rotate(180, Image.BILINEAR)),
            "Direction.WEST": ImageTk.PhotoImage(Image.open("tools/images/Robot.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR).rotate(90, Image.BILINEAR)),
            "Direction.EAST": ImageTk.PhotoImage(Image.open("tools/images/Robot.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR).rotate(270, Image.BILINEAR)),
        }
    }

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



window = tkinter.Tk()
window.geometry("{}x{}".format(W_WIDTH, W_HEIGHT))
window.resizable(0, 0)
window.configure(bg="white")

frm = tkinter.Frame(window, relief='flat', borderwidth=4)
frm.pack(fill=tkinter.BOTH, expand=1)
cv = tkinter.Canvas(frm)
cv.pack(fill=tkinter.BOTH, expand=1)

with open("Pi/out/map.json") as f:
    data = json.load(f)

drawMap(data, cv)

window.mainloop()