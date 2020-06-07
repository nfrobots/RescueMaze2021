import tkinter
import json
from PIL import Image, ImageTk

W_WIDTH = 1000
W_HEIGHT = 1000

window = tkinter.Tk()
window.geometry("{}x{}".format(W_WIDTH, W_HEIGHT))
window.resizable(0, 0)
window.configure(bg="white")

mapFrame = tkinter.Frame(window, relief='flat', borderwidth=4)
mapFrame.pack(fill=tkinter.BOTH, expand=1)
mapCanvas = tkinter.Canvas(mapFrame)

with open("tools/map.json") as f:
    mapData = json.load(f)


linewidth = 3
pad = 7
tileSize = (min(W_WIDTH, W_HEIGHT) - (pad * 2)) / max(mapData["sizeX"], mapData["sizeY"])
lineLen = tileSize - pad
wallColor = "#000"
emptyColor = "#bbb"
images = {
    "VICTIM": ImageTk.PhotoImage(Image.open("tools/images/Victim.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
    "BLACK": ImageTk.PhotoImage(Image.open("tools/images/Black.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR)),
    "RAMP":ImageTk.PhotoImage(Image.open("tools/images/Ramp.png").resize((int(lineLen), int(lineLen)), Image.BILINEAR))
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
        easthColor = wallColor
    else:
        eastColor = emptyColor
    if mapData["Map"][posStr]["Direction.WEST"] == True:
        westColor = wallColor
    else:
        westColor = emptyColor

    px = x * tileSize + pad
    py = y * tileSize + pad

    mapCanvas.create_line(px, py, px + lineLen, py, width=linewidth, fill=northColor) #NORTH
    mapCanvas.create_line(px, py + lineLen, px + lineLen, py + lineLen, width=linewidth, fill=southColor) #SOUTH
    mapCanvas.create_line(px + lineLen, py, px + lineLen, py + lineLen, width=linewidth, fill=eastColor) #EAST
    mapCanvas.create_line(px, py, px, py + lineLen, width=linewidth, fill=westColor) #WEST

    if mapData["Map"][posStr]["VICTIM"] == True:
        mapCanvas.create_image(px, py, anchor=tkinter.NW, image=images["VICTIM"])

    if mapData["Map"][posStr]["BLACK"] == True:
        mapCanvas.create_image(px, py, anchor=tkinter.NW, image=images["BLACK"])

    if mapData["Map"][posStr]["RAMP"] == True:
        mapCanvas.create_image(px, py, anchor=tkinter.NW, image=images["RAMP"])


robotSize = 0.2 * lineLen

px = mapData["robotX"] * tileSize + pad + (lineLen - robotSize) / 2
py = mapData["robotX"] * tileSize + pad + (lineLen - robotSize) / 2
mapCanvas.create_rectangle(px, py, px + robotSize, py + robotSize, fill="#f0f", outline="")

mapCanvas.pack(fill=tkinter.BOTH, expand=1)

window.mainloop()