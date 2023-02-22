from math import ceil, floor, pi, sqrt
import random
from typing import Tuple
from importlib_metadata import List
import numpy as np
from matplotlib import pyplot as plt

def generate_points(randomness: float = 0, n_points: int = 10, fake_ratio: float = 0) -> Tuple[List[float]]:
    """Gererates random points on a line.
        randomness: points vary within [-randomness; randomness] in x and y direction
        n_points: number of points
        fake_ration: number of fake points (not at all in line) to correct points 
    """
    theta = random.uniform(0.0, pi)
    r = random.uniform(-10, 10)
    return generate_points_from_theta_r(theta, r, randomness, n_points, fake_ratio)

def generate_points_from_theta_r(theta: float, r: float, randomness: float = 0, n_points: int = 10, fake_ratio: float = 0) -> Tuple[List[float]]:
    n_correct_points = ceil(n_points * (1 - fake_ratio))
    if pi/4 < theta < 3*pi/4:
        x_of_y = lambda y: (r-y*np.cos(theta)) / np.sin(theta)
        ys = [random.uniform(-10, 10) + random.uniform(-randomness, randomness) for _ in range(n_correct_points)] # use np.fromiter instead pls -> np array
        xs = [x_of_y(y) + random.uniform(-randomness, randomness) for y in ys]
    else:
        y_of_x = lambda x: -(x*np.sin(theta)-r) / np.cos(theta)
        xs = [random.uniform(-10, 10) + random.uniform(-randomness, randomness) for _ in range(n_correct_points)]
        ys = [y_of_x(x) + random.uniform(-randomness, randomness) for x in xs]

    n_fake_points = floor(n_points * fake_ratio)
    xs.extend(random.uniform(-10, 10) for _ in range(n_fake_points))
    ys.extend(random.uniform(-10, 10) for _ in range(n_fake_points))
    return xs, ys


THETA_RESOLUTION = 0.1
R_RESOLUTION = 0.7
# I:    max: sqrt
#       min: -y
# II:    max: y
#       min: -sqrt
# III:    max: -y
#       min: -sqrt
# IV:    max: sqrt
#       min: y

def hough_transformation(xs, ys):
    """
    hough space has r on x-axis, theta on y-axis, hough_space[theta, r]
    """
    # it is necessary to know the max and minimum r value to prepare the hough_space 
    max_r = -np.Infinity
    min_r = np.Infinity
    for x, y in zip(xs, ys):
        if x >= 0:
            r_upper = sqrt(x*x + y*y)
            if y >= 0:
                r_lower = -y
            else:
                r_lower = y
        else:
            r_lower = -sqrt(x*x + y*y)
            if y >= 0:
                r_upper = y
            else:
                r_upper = -y
        
        if r_upper > max_r:
            max_r = r_upper 
        if r_lower < min_r:
            min_r = r_lower

    r_size = int(max_r) - int(min_r) + 1
    r_offset = -int(min_r)
    print(r_size)

    hough_space = np.zeros(shape=(int(pi / THETA_RESOLUTION) + 1, ceil(r_size / R_RESOLUTION)), dtype=np.int)
    for x, y in zip(xs, ys):
        for theta in np.arange(0, pi, THETA_RESOLUTION):
            r = x * np.sin(theta) + y * np.cos(theta)
            t_coord = int(theta / THETA_RESOLUTION)
            r_coord = int(r / R_RESOLUTION) + r_offset
            hough_space[t_coord, r_coord] += 1
        
    return hough_space, r_offset


def visual_hough_transformation(xs, ys, point_axes, space_axes, figure):
    """
    hough space has r on x-axis, theta on y-axis, hough_space[theta, r]
    """
    
    point_axes.plot(xs, ys, 'o')


    # it is necessary to know the max and minimum r value to prepare the hough_space 
    max_r = -np.Infinity
    min_r = np.Infinity
    for x, y in zip(xs, ys):
        if x >= 0:
            r_upper = sqrt(x*x + y*y)
            if y >= 0:
                r_lower = -y
            else:
                r_lower = y
        else:
            r_lower = -sqrt(x*x + y*y)
            if y >= 0:
                r_upper = y
            else:
                r_upper = -y
        
        if r_upper > max_r:
            max_r = r_upper 
        if r_lower < min_r:
            min_r = r_lower

    r_size = int(max_r) - int(min_r) + 1
    r_offset = -int(min_r)
    print(r_size)

    hough_space = np.zeros(shape=(int(pi / THETA_RESOLUTION) + 1, ceil(r_size / R_RESOLUTION)), dtype=np.int)
    plt.ion()
    plt.show()
    im_obj = space_axes.imshow(hough_space, vmin=0, vmax=20)
    for x, y in zip(xs, ys):
        for theta in np.arange(0, pi, THETA_RESOLUTION):
            r = x * np.sin(theta) + y * np.cos(theta)
            t_coord = int(theta / THETA_RESOLUTION)
            r_coord = int(r / R_RESOLUTION) + r_offset
            hough_space[t_coord, r_coord] += 1
            im_obj.set_data(hough_space)
            figure.canvas.flush_events()
            print("d")

        
    return hough_space, r_offset


if __name__ == '__main__':
    xs, ys = generate_points_from_theta_r(0, 10, .1, 10, 0.1)
    xs2, ys2 = generate_points_from_theta_r(pi, 10, .1, 10, .1)

    xs.extend(xs2)
    ys.extend(ys2) 

    import time

    # start_time = time.time()
    # hs, r_offset = hough_transformation(xs, ys)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # print(hs)


    figure, axis = plt.subplots(1, 2)

    visual_hough_transformation(xs, ys, axis[0], axis[1], figure)

    # axis[0].plot(xs, ys, 'o')

    # axis[1].imshow(hs)

    def mouse_event(event):
        if event.inaxes == axis[1]:
            r, theta = round(event.xdata), round(event.ydata)
            print(hs[theta, r])
            print(r_offset)
            r *= R_RESOLUTION
            theta *= THETA_RESOLUTION
            r -= r_offset * R_RESOLUTION

            print(theta, r)

            y_of_x = lambda x: -(x*np.sin(theta)-r) / np.cos(theta)
            
            lims = [0.7*x for x in axis[0].get_xlim()]
            axis[0].plot(lims, [y_of_x(lim) for lim in lims])
            figure.canvas.draw()


    # cid = figure.canvas.mpl_connect('button_press_event', mouse_event)

    