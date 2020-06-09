import Mapping
from Constants import *
import Logger
import mapDrawer
import tkinter

Logger.ACTIVE = False

with open("out/log.txt") as f:
    instructions = f.read().split('\n')

def convertArgs(string):
    if string == "<RelDirection.FORWARD: 0>":
        return RelDirection.FORWARD
    elif string == "<RelDirection.RIGHT: 1>":
        return RelDirection.RIGHT
    elif string == "<RelDirection.BACKWARD: 2>":
        return RelDirection.BACKWARD
    elif string == "<RelDirection.LEFT: 3>":
        return RelDirection.LEFT
    elif string == "<Direction.NORTH: 0>":
        return Direction.NORTH
    elif string == "<Direction.EAST: 1>":
        return Direction.EAST
    elif string == "<Direction.SOUTH: 2>":
        return Direction.SOUTH
    elif string == "<Direction.WEST: 3>":
        return Direction.WEST
    elif string == "'BLACK'":
        return BLACK
    elif string == "'RAMP'":
        return RAMP
    elif string == "'VICTIM'":
        return VICTIM
    elif string == "True":
        return True
    elif string == "False":
        return False
    else:
        try:
            return int(string)
        except ValueError:
            return string


root = tkinter.Tk()
root.geometry("{}x{}".format(mapDrawer.W_WIDTH, mapDrawer.W_HEIGHT))
frm = tkinter.Frame(root, relief='flat', borderwidth=4)
frm.pack(fill=tkinter.BOTH, expand=1)
cv = tkinter.Canvas(frm)
cv.pack(fill=tkinter.BOTH, expand=1)

m = Mapping.Map()

index = 0
def step():
    global index
    instruction = instructions[index]
    if instruction == "":
        print("moin")
        return
    fmt = instruction.split(";")
    function = fmt[0]
    args = [convertArgs(a) for a in fmt[1].replace(")", "").split(", ")[1::]]
    getattr(m, function)(*args)
    mapDrawer.drawMap(m._store(), cv)
    index += 1

button = tkinter.Button(frm, width=10, height=2, bg="green", command=step)
button.pack()

root.mainloop()
