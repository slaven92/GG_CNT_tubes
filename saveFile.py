from time import time, sleep
import matplotlib.pyplot as plt
import random
import numpy as np
import pyvisa

## variables
variables = dict(
    BASE = "C:/Users/NOM/Documents/sem/GG_CNT_tubes/data/",
)
## spectrum settings
settings = dict(
    INIT = False,
    # NUM_OF_POINTS = 10,
    START_FREQ = 50E3,
    STOP_FREQ = 120E3,
    BW = 1,
)


rm = pyvisa.ResourceManager()
addr = rm.list_resources()
print(addr)
inst = rm.open_resource("USB0::0x0957::0x0A0B::MY48010776::INSTR")

## signal generator
def get_spectrum(square = True ,trace='1'):
    inst.write(':TRAC:DATA? TRACE' + trace)
    data = inst.read()
    spectrum = np.array(data.split(','),dtype=float)
    if square:
        out = spectrum*spectrum/get_bw()
        return out.reshape(-1,1)
    return spectrum.reshape(-1,1)

def get_x_axis():
    start_freq=get_start_freq()
    stop_freq=get_stop_freq()
    nb_points=get_nb_points()
    return np.linspace(start_freq,stop_freq,int(nb_points)).reshape(-1,1)
    # return np.linspace(settings["START_FREQ"], settings["STOP_FREQ"], settings["NUM_OF_POINTS"]).reshape(-1,1)

def get_start_freq():
    inst.write(':FREQuency:STARt?')
    start_freq=inst.read()
    start_freq = float(start_freq)
    return start_freq

def get_stop_freq():
    inst.write(':FREQuency:STOP?')
    stop_freq=inst.read()
    stop_freq=float(stop_freq)
    return stop_freq

def get_nb_points():
    inst.write(':SWEep:POINts?')
    nb_points=inst.read()
    nb_points=float(nb_points)
    return nb_points

def get_bw():
    inst.write(':BAND?')
    bwidth=inst.read()
    return float(bwidth)


## initial setup of signal analyser TODO
if settings["INIT"]:
    inst.write(':FREQuency:START '+str(settings["START_FREQ"])+'Hz')
    inst.write(':FREQuency:STOP '+str(settings["STOP_FREQ"])+'Hz')
    inst.write(':BAND '+ str(settings["BW"])+'Hz')


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
    save_spectrum(filename="TEM_B_tube1_tip")