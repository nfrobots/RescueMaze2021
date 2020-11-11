from RMMLIB4 import Mapping, Constants
from RMMLIB4.Constants import *
from tools import mapDrawer

import tkinter
from pathlib import Path

with open(Path(__file__).parent.parent / "Pi/out/log.txt") as f:
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
            return eval(string)
        except ValueError:
            return string


root = tkinter.Tk()
root.geometry("{}x{}".format(mapDrawer.W_WIDTH, mapDrawer.W_HEIGHT))
frm = tkinter.Frame(root, relief='flat', borderwidth=4)
frm.pack(fill=tkinter.BOTH, expand=1)
cv = tkinter.Canvas(frm)
cv.pack(fill=tkinter.BOTH, expand=1)

m = Mapping.Map()

mapDrawer.drawMap(m._store(), cv)

index = 0
def step():
    global index
    instruction = instructions[index]
    if instruction == "":
        return
    print(instruction)
    fmtInstruction = instruction.split(";")
    function = fmtInstruction[0]
    args = [convertArgs(a) for a in fmtInstruction[1].replace(")", "").split(", ")[1::]]
    getattr(m, function)(*args)
    index += 1
    mapDrawer.drawMap(m._store(), cv)

button = tkinter.Button(frm, width=10, height=2, bg="green", border="0", command=step)
button.pack()

root.mainloop()