import serial
from collections import deque
from tkinter import Tk, Canvas, Scale
from math import sin, cos, pi, tanh, log

ser = serial.Serial("COM3", 9600)
ser.read(1024)

data = deque([(0, 0, 0, 0) for x in range(52)])


POINT_SIZE = 5
SCALE = 0.5
CENTER = (500, 500)
RB_SCALING = 300
D_CORR = 0

def update_data():
    raw_data = ser.readline().decode().rstrip()
    
    angle, distance = 0, 0
    try:
        angle, distance = [int(x) for x in raw_data.split(" ")]
        angle = 360 - angle + 110
        distance += D_CORR
        if distance > 1000:
            distance = 1000
    except ValueError:
        pass
    data.popleft() 
    data.append((cos(angle*pi/180) * distance * SCALE, sin(angle*pi/180) * distance * SCALE, angle, distance * SCALE))

def get_full():
    while data[-1][2] < data[-2][2]:
        update_data()
    update_data()
    return data

def draw_data(canvas):
    canvas.delete("all")
    for i in range(len(data)):
        x = data[i][0] + CENTER[0]
        y = data[i][1] + CENTER[1]
        blueness = max(0, int(tanh(data[i][3] / RB_SCALING) * 15))
        color = "#{}0{}".format(hex(15-blueness)[2], hex(blueness)[2])
        # canvas.create_line(data[i][0] + CENTER[0], data[i][1] + CENTER[1], data[(i+1)%len(data)][0] + CENTER[0], data[(i+1)%len(data)][1] + CENTER[1], width=4, fill="#666")
        canvas.create_oval(x - POINT_SIZE, y - POINT_SIZE, x + POINT_SIZE, y + POINT_SIZE, fill=color)
        canvas.create_line(CENTER[0], CENTER[1], x, y, width=3, fill=color)
    canvas.create_oval(CENTER[0] - 10, CENTER[1] - 10, CENTER[0] + 10, CENTER[1] + 10, fill="green")


if __name__ == "__main__":
    root = Tk()
    root.geometry("1000x1000")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    canvas = Canvas(root, bg="#ddd")
    canvas.grid(column=0, row=0, sticky='nswe')

    def loop():
        update_data()
        draw_data(canvas)
        root.after(10, loop)

    loop()

    root.mainloop()