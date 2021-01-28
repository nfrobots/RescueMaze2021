from RMMLIB4 import Mapping, Constants
from RMMLIB4.Constants import *
from tools import mapDrawer

import tkinter
from pathlib import Path

with open(Path(__file__).parent.parent / "Pi/out/log.txt") as f:
    instructions = f.read().split('\n')

def evalArg(string):
    if string[0] != "<":
        return eval(string)
    elif string[0:10] == "<MazeTile:":
        tile = Mapping.MazeTile()
        rawAttributes = string[11:].replace(">", "").split("\t")
        for rawAttribute in rawAttributes:
            attribute_string, value = rawAttribute.split(": ")
            tile[eval(attribute_string)] = eval(value)
        return tile
    elif string[0:13] == "<RelDirection":
        rawRelDirection = string[1:].split(": ")
        return eval(rawRelDirection[0])


root = tkinter.Tk()
root.geometry("{}x{}".format(500, 500))
frm = tkinter.Frame(root, relief='flat', borderwidth=4)
frm.pack(fill=tkinter.BOTH, expand=1)
cv = tkinter.Canvas(frm)
cv.pack(fill=tkinter.BOTH, expand=1)

m = Mapping.Map(path_pre_expand=True)

mapDrawer.draw_map(cv, m)

index = 0
def step():
    global index
    instruction = instructions[index].rstrip()
    if instruction == "" or instruction == "\n":
        index += 1 if index < len(instructions) - 1 else 0
        return
    index += 1
    
    fmtInstruction = instruction.split(";")
    function = fmtInstruction[0]
    rawArgs = fmtInstruction[1].replace(")", "").split(", ")[1:]
    args = [evalArg(a) for a in rawArgs]
    getattr(m, function)(*args)
    mapDrawer.draw_map(cv, m)

auto_step_enabled = False

def auto_step_enable():
    global auto_step_enabled
    auto_step_enabled = not auto_step_enabled

def auto_step():
    if auto_step_enabled:
        step()
    root.after(100, auto_step)

button = tkinter.Button(frm, width=10, height=2, bg="green", border="0", command=auto_step_enable)
button.pack()

button2 = tkinter.Button(frm, width=10, height=2, bg="blue", border="0", command=step)
button2.pack()

auto_step()

root.mainloop()