from time import time, sleep
import random
import numpy as np

import sys
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters


import pyvisa




## signal generator simulator
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






## variables
variables = dict(
    TIMEOUT = 10, # in s
    TRESHOLD = 2e-12, # in dbs or v
    BASE = "C:/Users/NOM/Documents/sem/GG_CNT_tubes/data/",
)
## spectrum settings
settings = dict(
    INIT = False,
    NUM_OF_POINTS = 1001,
    START_FREQ = get_start_freq(),
    STOP_FREQ = get_stop_freq(),
    GOAL_FREQ = 25e3,
    FILENAME = "N3_tube1_H20_anneal2",
    BW = 1,
)


## initial setup of signal analyser TODO
if settings["INIT"]:
    inst.write(':FREQuency:START '+str(settings["START_FREQ"])+'Hz')
    inst.write(':FREQuency:STOP '+str(settings["STOP_FREQ"])+'Hz')
    inst.write(':BAND '+ str(settings["BW"])+'Hz')



class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        # self.view = self.canvas.addViewBox()
        self.pi = pg.PlotItem(labels = {'left': "freq [Hz]", 'bottom': "spectrum number"})
        self.view = self.canvas.addItem(self.pi)

        #  image plot
        self.img = pg.ImageItem(border='w')
        self.pi.addItem(self.img)
        self.y = get_x_axis()
    

        self.pen = pg.mkPen({'color': "F00", "width": 1})
        self.pi.addLine(y=settings["GOAL_FREQ"], pen=self.pen)
        self.pi.addLine(y=settings["GOAL_FREQ"]*2, pen=self.pen)
        self.pi.addLine(y=settings["GOAL_FREQ"]*3, pen=self.pen)

        self.t0 = time()
        self.t_timeout = time()
        self.time_vector = []
        #### Start  #####################
        self.run_loop()

    def set_data(self, x=[], y=[], data=[]):
        if len(x):
            self.x = x
        if len(y):
            self.y = y 
        if len(data):
            self.data = data

    def _update(self):
        if hasattr(self, "data"):
            self.img.setImage(self.data.T)
        self.run_loop()


    def save_data(self, filename = "allData" + str(time())):
        out = np.hstack((self.y,self.spectrum_matrix))
        np.savetxt(variables["BASE"] + filename + ".csv", out)
        np.savetxt(variables["BASE"] + "time_" + filename + ".csv", self.time_vector.reshape((-1,1)))
        exporter = pg.exporters.ImageExporter(self.pi)
        exporter.export(variables["BASE"] + filename + ".png")

    ## main measurement loop
    def run_loop(self):

        y_vector = get_spectrum()
        sleep(0.5)
        th = np.median(y_vector)

        print(th)
        ## pause if it is smaller than th
        if th < variables["TRESHOLD"]:
            if ((time() - self.t_timeout) > variables["TIMEOUT"]):
                self.save_data()
                return
        ## continue if it is bigger than th
        else:
            self.t_timeout = time()

            ## handle first vector
            if len(self.time_vector)==0:
                self.time_vector = np.array([self.t_timeout - self.t0])
                self.spectrum_matrix = y_vector
                self.img.translate(self.time_vector.min(),self.y.min())
                self.img.scale(2, (settings["STOP_FREQ"] - settings["START_FREQ"]) / settings["NUM_OF_POINTS"])
            else: ##normal append
                self.time_vector = np.append(self.time_vector, self.t_timeout - self.t0)
                self.spectrum_matrix = np.hstack((self.spectrum_matrix, y_vector))
            

            self.set_data(x=self.time_vector, data=self.spectrum_matrix)
            self.t_timeout = time()

        QtCore.QTimer.singleShot(1, self._update)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    # sys.exit(app.exec_())
    app.exec_()
    rm.close()
    thisapp.save_data(filename=settings["FILENAME"])