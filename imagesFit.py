from PIL import Image
from PIL import ImageFilter, ImageChops, ImageStat, ImageDraw
from matplotlib import pyplot as plt
import glob
import scipy.optimize as opt
import numpy as np

fileLocation = "Y:/Slaven/Awesome Data Stuff/20200904 Video Capture Digicam/"


def find_center(im):

    matrix = np.array(im)

    x_pos, y_pos, x_sigma, y_sigma = fit2dGausian(matrix)

    draw = ImageDraw.Draw(im)
    draw.line((0, y_pos, im.size[0], y_pos), fill=128)
    draw.line((x_pos, 0, x_pos, im.size[1]), fill=128)

    draw.ellipse([(x_pos-x_sigma, y_pos-y_sigma), ( x_pos+x_sigma, y_pos+y_sigma)])



    return 5


def twoD_Gaussian(xy, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x=xy[0]
    y=xy[1]
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
    return g.ravel()


def fit2dGausian(matrix):
    x = np.arange(matrix.shape[1])
    y = np.arange(matrix.shape[0])
    xMesh, yMesh = np.meshgrid(x, y)

    offset = np.mean(matrix)
    amplitude = np.max(matrix) - offset
    theta = 0
    xy = np.unravel_index(matrix.argmax(),matrix.shape)
    x0 = x[xy[1]]
    y0 = y[xy[0]]
    sigma_x = 4
    sigma_y = 4
    initial_guess = [amplitude,x0,y0,sigma_x,sigma_y,theta,offset]

    matrix = matrix.ravel()
    popt, pconv = opt.curve_fit(twoD_Gaussian, (xMesh,yMesh), matrix, p0 = initial_guess)

    return popt[1],popt[2], popt[3], popt[4]



fileList = glob.glob(fileLocation + "m100mV*.png")

left = 370
rigth = 400
top = 240
bottom = 270


for image in fileList:
    im2 = Image.open(image)

    im2 = im2.crop((left,top,rigth,bottom))

    coord = find_center(im2)

    im2.show()

