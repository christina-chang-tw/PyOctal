#!/usr/bin/env python3

import random
from collections import deque
import matplotlib.animation as animation
from functools import partial

class RealtimePlot:
    def __init__(self, axes, max_entries: int=500):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot = self.axes.plot(self.axis_x, self.axis_y, "ro-")
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim()
        self.axes.autoscale_view() # rescale the y-axis

    def wrapper(self, callback, frame_index):
        self.add(*callback(frame_index))
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
        return self.lineplot


    def animate(self, frame_index, figure, callback, interval = 50):
        animation.FuncAnimation(figure, partial(self.wrapper, callback=callback, frame_index=frame_index), interval=interval)

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
