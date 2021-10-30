import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage.feature import peak_local_max
# from scipy import ndimage

from tools import LidarReader2

lr = LidarReader2.LidarReader()

THETA_STEP = np.pi/180
THETA_MULT = 20
R_MULT = 0.2
THRESHOLD = 0.5
MIN_D = 5

root = tk.Tk()
cframe = tk.Frame(root)
cframe.grid(row=0, column=1, sticky="nswe")
s1 = tk.Scale(cframe, from_=0, to=30) #TETHA_STEP
s1.pack()
s1.set(THETA_STEP*1000)
s2 = tk.Scale(cframe, from_=0, to=5000) # THETA_MULT
s2.pack()
s2.set(THETA_MULT*100)
s3 = tk.Scale(cframe, from_=0, to=100) # R_MULT
s3.pack()
s3.set(R_MULT*100)
s4 = tk.Scale(cframe, from_=0, to=100) #THRESHOLD
s4.pack()
s4.set(THRESHOLD*100)
s5 = tk.Scale(cframe, from_=0, to=1000) #MIN_D
s5.pack()
s5.set(MIN_D*10)



figure = plt.figure(figsize=(9, 4))
chart_type = FigureCanvasTkAgg(figure, root)
chart_type.get_tk_widget().grid(column=0, row=0, sticky="nswe")

ax1 = plt.subplot(1, 2, 1)
ax2 = plt.subplot(1, 2, 2)


def update():
    lr.update()
    if lr.full_ready:
        global THETA_STEP, THETA_MULT, R_MULT, THRESHOLD, MIN_D
        print(THETA_STEP, THETA_MULT, R_MULT, THRESHOLD)
        # points = [(10.663567547950421, -86.84778826861567, 277, 87.5), (-1.5889792218936908e-14, -86.5, 270, 86.5), (-12.316819434965748, -87.63872408362897, 262, 88.5), (-23.681942626880637, -88.38221310544975, 255, 91.5), (-36.336839561343496, -89.93683389297837, 248, 97.0), (-48.72336683475685, -87.89928056750928, 241, 100.5), (-67.4032825930294, -89.4471771252968, 233, 112.0), (-86.83229630737469, -89.91747504233136, 226, 125.0), (-108.80043460397592, -88.10485474697727, 219, 140.0), (-135.8610171612848, -81.63353487324359, 211, 158.5), (-195.04195520669532, -86.83827329668325, 204, 213.5), (-234.43543126675536, -76.17268911342461, 198, 246.5), (-245.40679586191598, -47.70224884413618, 191, 250.0), (-249.39101256495607, -17.439118436031208, 184, 250.0), (-253.88005079112526, 17.753022567879945, 176, 254.5), (-244.91598227019216, 47.60684434644797, 169, 249.5), (-200.19739668012983, 65.04807731592645, 162, 210.5), (-127.17935755133213, 62.02951727065444, 154, 141.5), (-114.05919724057769, 74.07090876204366, 147, 136.0), (-125.63128867151238, 105.41716798859247, 140, 164.0), (-190.6185416374683, 204.4133596025582, 133, 279.5), (-158.59388465106417, 226.49554024590628, 125, 276.5), (-123.00154944990332, 231.3322693290389, 118, 262.0), (-88.24119697802236, 242.44069616276443, 470, 258.0), (-62.63420891480988, 233.75404996195456, 465, 242.0), (-29.065838402127692, 236.72225716645528, 457, 238.5), (7.256032284948068e-14, 237.0, 450, 237.0), (29.004903730425266, 236.22598409063463, 443, 238.0), (56.609723570322494, 227.04919994858312, 436, 234.0), (72.92787773246854, 189.98361679218058, 429, 203.5), (69.01231972952596, 129.79329615026225, 422, 147.0), (70.83668988935425, 101.16527746969045, 415, 123.5), (72.93523609311562, 81.00278597703591, 408, 109.0), (72.82947449149752, 63.30969629758393, 401, 96.5), (72.96433941125193, 47.38359604630732, 393, 87.0), (74.59990584283086, 36.38480518349342, 386, 83.0), (74.69596747234604, 25.719884202115345, 379, 79.0), (73.85014385540234, 15.697332656740768, 372, 75.5), (73.22031030974328, 6.405947091952915, 365, 73.5), (74.45461661292263, -2.6000125043363114, 358, 74.5), (75.06431388523046, -11.889019343057562, 351, 76.0), (74.97841228318886, -21.49971375372598, 344, 78.0), (74.56089312964764, -31.649221407631252, 337, 81.0), (76.6432482349228, -44.25000000000004, 330, 88.5), (73.07514916932729, -55.066074618412415, 323, 91.5), (74.81133923521969, -72.24447052773574, 316, 104.0), (67.65194203785754, -83.54319085662436, 309, 107.5), (52.462007159087264, -83.95676151948618, 302, 99.0), (39.30349834188506, -84.28662419440843, 295, 93.0)]
        points = [p for p in lr.get_full() if p[1] < 1000]

        hough_space = {} # (accumulator, ((point1X, point1Y), ...))

        hs_max = -np.Infinity
        theta_max = int(np.pi*THETA_MULT)
        r_max = -np.Infinity
        r_min = np.Infinity
        px_min = np.Infinity
        px_max = -np.Infinity
        py_min = np.Infinity
        py_max = -np.Infinity

        for point in points:
            for theta in np.arange(0, np.pi, THETA_STEP):
                if point[2] > px_max:
                    px_max = point[2]
                elif point[2] < px_min:
                    px_min = point[2]

                if point[3] > py_max:
                    py_max = point[3]
                elif point[3] < py_min:
                    py_min = point[3]

                r = point[2] * np.sin(theta) + point[3] * np.cos(theta)

                ntheta = int(theta * THETA_MULT)
                nr = int(r * R_MULT)
                hough_space_position = (ntheta, nr)

                if nr > r_max:
                    r_max = nr
                elif nr < r_min:
                    r_min = nr

                if hough_space_position in hough_space:
                    current = hough_space[hough_space_position]
                    hough_space[hough_space_position] = (current[0]+1, (*current[1], point))
                    if current[0]+1 > hs_max:
                        hs_max = current[0]*1.4
                else:
                    hough_space[hough_space_position] = (1, (point,))

        print(f"INFO:\nhs_max: {hs_max}\ntheta_max: {theta_max}\nr_max: {r_max}\nr_min: {r_min}")

        ax1.cla()
        ax2.cla()

        ax1.set_xlim([-500, 500])
        ax1.set_ylim([-500, 500])

        xs = []
        ys = []
        for point in points:
            xs.append(point[2])
            ys.append(point[3])
        ax1.plot(xs, ys, "b^")

        image = np.zeros((np.round(theta_max) + 1, np.round(r_max - r_min) + 1))

        for point in hough_space:
            image[np.round(point[0]), np.round(point[1] - r_min)] = hough_space[point][0]

        ax2.imshow(image)


        maxima = [[maximum[0], maximum[1] + r_min] for maximum in peak_local_max(image, threshold_rel=THRESHOLD, min_distance=int(MIN_D), exclude_border=False)]

        # maxima = [point for point in hough_space if hough_space[point] > hs_max*THRESHOLD]


        y_of_x = lambda x, theta, r: (((r)/R_MULT) - np.sin((theta)/THETA_MULT)*x)/np.cos((theta)/THETA_MULT)
        x_of_y = lambda y, theta, r: (((r)/R_MULT) - np.cos((theta)/THETA_MULT)*y)/np.sin((theta)/THETA_MULT)

        for maximum in maxima:
            theta, r = maximum[0], maximum[1]

            _xs = []
            _ys = []
            for contrib_point in hough_space[theta, r][1]:
                _xs.append(contrib_point[2])
                _ys.append(contrib_point[3])
            ax1.plot(_xs, _ys, 'o')

            ax1.plot([-500, 500], [y_of_x(-500, theta, r), y_of_x(500, theta, r)])

        figure.canvas.draw()


    THETA_STEP = s1.get()/1000
    THETA_MULT = s2.get()/100
    R_MULT = s3.get()/100
    THRESHOLD = s4.get()/100
    MIN_D = s5.get()/10


    root.after(10, update)

def on_closing():
    exit()

root.protocol("WM_DELETE_WINDOW", on_closing)


root.after(100, update)
root.mainloop()