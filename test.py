#!/usr/bin/env python3

import time, random
import math
from collections import deque

class RealtimePlot:
    def __init__(self, axes, max_entries = 500):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries

        self.lineplot, = axes.plot([], [], "ro-")
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

def main():
    from matplotlib import pyplot as plt

    # fig, axes = plt.subplots()
    # display = RealtimePlot(axes)
    # #plt.show()

    fig, axes = plt.subplots()
    display = RealtimePlot(axes)
    for i in range(100):
        display.add(i, random.random() * 100)
        plt.pause(0.01)

    plt.show()
    # while True:
    # #for i in range(5):
    #     display.add(time.time() - start, random.random() * 100)
        # plt.pause(0.001)

if __name__ == "__main__": main()
