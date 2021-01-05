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
root.geometry("{}x{}".format(500, 500))
frm = tkinter.Frame(root, relief='flat', borderwidth=4)
frm.pack(fill=tkinter.BOTH, expand=1)
cv = tkinter.Canvas(frm)
cv.pack(fill=tkinter.BOTH, expand=1)

m = Mapping.Map()

mapDrawer.draw_map(cv, m)

index = 0
def step():
    global index
    instruction = instructions[index].rstrip()
    if instruction == "" or instruction == "\n":
        index += 1 if index < len(instructions)-1 else 0
        return
    print(instruction)
    fmtInstruction = instruction.split(";")
    function = fmtInstruction[0]
    args = [convertArgs(a) for a in fmtInstruction[1].replace(")", "").split(", ")[1::]]
    getattr(m, function)(*args)
    index += 1
    mapDrawer.draw_map(cv, m)

auto_step_enabled = False

def auto_step_enable():
    global auto_step_enabled
    auto_step_enabled = not auto_step_enabled

def auto_step():
    if auto_step_enabled:
        step()
    root.after(50, auto_step)

button = tkinter.Button(frm, width=10, height=2, bg="green", border="0", command=auto_step_enable)
button.pack()

button2 = tkinter.Button(frm, width=10, height=2, bg="blue", border="0", command=step)
button2.pack()

auto_step()

root.mainloop()