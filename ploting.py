import glob
from matplotlib import pylab as plt
import numpy as np

names = glob.glob("./GG_CNT_tubes/data/tube*.csv")


for name in names:
    my_data = np.genfromtxt(name)
    line, = plt.plot(my_data[:,0],my_data[:,1], label=name[28:-4])
    plt.legend()

plt.show()