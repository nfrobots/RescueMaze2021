import serial
from collections import deque
import numpy as np
import time
from tkinter import *

class LidarReader():
    def __init__(self, port="COM3", baud=9600, angle_correction=75):
        self.angle_correction = angle_correction

        self._ser = serial.Serial(port, baud)
        time.sleep(0.4)
        print(self._ser.in_waiting)
        self._ser.read(self._ser.in_waiting)

        self.data = deque([(0, 0, 0, 0)]) # data element: (angle, distance, xcoord, ycoord)
        self.data_len = 0
        self.last_fall_index = None

        self.full_ready = False

        while not self._ser.in_waiting:
            time.sleep(0.2)
            print("waiting for LIDAR to wake up")
        self.update()

    def update(self):
        self.full_ready = False
        while self._ser.in_waiting:
            try:
                data_string = self._ser.readline().decode().rstrip()
            except UnicodeDecodeError:
                print("UnicodeDecodeError in LidarReader.update()")
                return
            
            angle, distance = 0, 0
            try:
                angle, distance = [int(st) for st in data_string.split(" ")]
                angle += self.angle_correction
            except ValueError:
                print("Value error while converting string to int in LidarReader.update()")

            if distance > 1000:
                distance = 1000

            if angle < self.data[-1][0]: # angle got lower
                self.full_ready = True
                self.data_len = len(self.data) - (self.last_fall_index + 1 if not self.last_fall_index is None else 0)
                self.last_fall_index = len(self.data)

            if not self.data_len is None and not self.last_fall_index is None:
                while len(self.data) > self.data_len:
                    self.data.popleft()
                    self.last_fall_index -= 1

            self.data.append((angle, distance, np.cos(np.radians(angle)) * distance, np.sin(np.radians(angle)) * distance))

    def get_data(self):
        return self.data

    def get_full(self, blocking=True):
        while not self.full_ready:
            self.update()
        self.full_ready = False
        return self.data


POINT_SIZE = 5
CENTER = (500, 500)
RB_SCALING = 300

def draw_data(canvas, data):
    canvas.delete("all")
    for i in range(len(data)):
        x = data[i][2] + CENTER[0]
        y = data[i][3] + CENTER[1]
        blueness = max(0, int(np.tanh(data[i][3] / RB_SCALING) * 15))
        color = "#{}0{}".format(hex(15-blueness)[2], hex(blueness)[2])
        # canvas.create_line(data[i][0] + CENTER[0], data[i][1] + CENTER[1], data[(i+1)%len(data)][0] + CENTER[0], data[(i+1)%len(data)][1] + CENTER[1], width=4, fill="#666")
        canvas.create_oval(x - POINT_SIZE, y - POINT_SIZE, x + POINT_SIZE, y + POINT_SIZE, fill=color)
        canvas.create_line(CENTER[0], CENTER[1], x, y, width=3, fill=color)
    canvas.create_oval(CENTER[0] - 10, CENTER[1] - 10, CENTER[0] + 10, CENTER[1] + 10, fill="green")


if __name__ == "__main__":
    lr = LidarReader()

    root = Tk()
    root.geometry("1000x1000")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    canvas = Canvas(root, bg="#ddd")
    canvas.grid(column=0, row=0, sticky='nswe')

    def loop():
        lr.update()
        if lr.full_ready:
            draw_data(canvas, lr.get_full())
        root.after(10, loop)

    loop()

    root.mainloop()