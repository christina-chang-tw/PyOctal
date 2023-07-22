from lib.util.plot import RealTimePlot
import random
import matplotlib.pyplot as plt

def test_realtimeplot():

    display = RealTimePlot()
    for i in range(100):
        display.add(i, random.random() * 100)
        plt.pause(0.1)
    display.show()
    

