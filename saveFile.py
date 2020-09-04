from time import time, sleep
import matplotlib.pyplot as plt
import random
import numpy as np


## variables
variables = dict(
    BASE = "./data/",
)
## spectrum settings
settings = dict(
    NUM_OF_POINTS = 10,
    START_FREQ = 50E3,
    STOP_FREQ = 120E3,
    BW = 1,
)

## signal generator simulator
def get_spectrum():
    return np.random.uniform(0, 1, (settings["NUM_OF_POINTS"], 1))
def get_x_axis():
    return np.linspace(settings["START_FREQ"], settings["STOP_FREQ"], settings["NUM_OF_POINTS"]).reshape(-1,1)


## initial setup of signal analyser TODO


## save spectrum
def save_spectrum(filename = "singleSpectrum" + str(time()), doPlot = True):
    x_vector = get_x_axis()
    y_vector = get_spectrum()
    c = np.hstack((x_vector, y_vector))
    np.savetxt(variables["BASE"] + filename + ".csv", c)

    if doPlot:
        plt.figure()
        plt.yscale("log")
        plt.plot(x_vector, y_vector)
        plt.xlabel("frequency [Hz]")
        plt.ylabel("signal [V]")
        plt.savefig(variables["BASE"] + filename + ".png")
        plt.show()


if __name__ == '__main__':
    save_spectrum()