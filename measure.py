from time import time, sleep
import random
import numpy as np

import sys
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters



## variables
variables = dict(
    TIMEOUT = 10, # in s
    TRESHOLD = 0.8, # in dbs or v
    BASE = "./data/",
)
## spectrum settings
settings = dict(
    NUM_OF_POINTS = 10,
    START_FREQ = 10E3,
    STOP_FREQ = 500E3,
    GOAL_FREQ = 20E3,
    BW = 1,
)

## signal generator simulator
def get_spectrum():
    return np.random.uniform(0, 1, (settings["NUM_OF_POINTS"], 1))
def get_x_axis():
    return np.linspace(settings["START_FREQ"], settings["STOP_FREQ"], settings["NUM_OF_POINTS"]).reshape(-1,1)


## initial setup of signal analyser TODO


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
    

        self.pen = pg.mkPen({'color': "F00", "width": 3})
        self.pi.addLine(y=settings["GOAL_FREQ"], pen=self.pen)
        self.pi.addLine(y=settings["GOAL_FREQ"]*2, pen=self.pen)

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
        sleep(1)
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
    # thisapp.save_data()