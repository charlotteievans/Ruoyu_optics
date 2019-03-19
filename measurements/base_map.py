import matplotlib

matplotlib.use('Qt4Agg')  # this allows you to see the interactive plots!
from optics.misc_utility import scanner
import numpy as np
from optics.thermovoltage_plot import thermovoltage_plot
import warnings
import matplotlib.pyplot as plt
from optics.measurements.base_measurement import LockinBaseMeasurement
from optics.misc_utility.tkinter_utilities import tk_sleep
import csv


class MapScan(LockinBaseMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, xd, yd, xr, yr, xc, yc,
                 bsc102_x, bsc102_y, sr7270_single_reference, powermeter=None, waveplate=None, direction=True,
                 axis='y'):
        super().__init__(master=master, filepath=filepath, device=device,
                         sr7270_single_reference=sr7270_single_reference, powermeter=powermeter, waveplate=waveplate,
                         notes=notes, gain=gain, bsc102_x=bsc102_x, bsc102_y=bsc102_y, scan=scan)
        self._xd = xd  # x pixel density
        self._yd = yd  # y pixel density
        self._yr = yr  # y range
        self._xr = xr  # x range
        self._xc = xc  # x center position
        self._yc = yc  # y center position
        self._x_ind = 0
        self._y_ind = 0
        self._z1 = np.zeros((self._xd, self._yd))
        self._z2 = np.zeros((self._xd, self._yd))
        self._axis = axis
        self._norm = thermovoltage_plot.MidpointNormalize(midpoint=0)
        self._x_val, self._y_val = scanner.find_scan_values(self._xc, self._yc, self._xr, self._yr, self._xd, self._yd)
        self._direction = direction
        if not self._direction:
            self._y_val = self._y_val[::-1]
        self._time_constant = self._sr7270_single_reference.read_tc()
        self._v = []
        self._cut_writer = None

    def load(self):
        self._ax1 = self._fig.add_subplot(221)
        self._ax2 = self._fig.add_subplot(223)
        self._ax3 = self._fig.add_subplot(222)
        self._ax4 = self._fig.add_subplot(224)
        self._im1 = self._ax1.imshow(self._z1.T, norm=self._norm, cmap=plt.cm.coolwarm, interpolation='nearest',
                                     origin='lower')
        self._im2 = self._ax2.imshow(self._z2.T, norm=self._norm, cmap=plt.cm.coolwarm, interpolation='nearest',
                                     origin='lower')
        self._clb1 = self._fig.colorbar(self._im1, ax=self._ax1)
        self._clb2 = self._fig.colorbar(self._im2, ax=self._ax2)

    def onclick(self, event):
        try:
            points = [int(np.ceil(event.xdata - 0.5)), int(np.ceil(event.ydata - 0.5))]
            if not self._direction:
                points = [int(np.ceil(event.xdata - 0.5)), int(np.ceil(self._yd - event.ydata - 0.5 - 1))]
            self._bsc102_x.move(self._x_val[points[0]])
            self._bsc102_y.move(self._y_val[points[1]])
            print('pixel: ' + str(points))
            print('position: ' + str(self._x_val[points[0]]) + ', ' + str(self._y_val[points[1]]))
        except:
            print('invalid position')

    def plot_final(self):
        pass

    def measure(self):
        cutfilename = self._filename.split('.csv')[0] + '_cut.csv'
        with open(cutfilename, 'w', newline='') as cutinputfile:
            self._cut_writer = csv.writer(cutinputfile)
            if self._axis == 'y':
                for self._y_ind, i in enumerate(self._y_val):
                    self._master.update()
                    if self._abort:
                        self._bsc102_x.move(0)
                        self._bsc102_y.move(0)
                        break
                    if not self._direction:
                        self._y_ind = len(self._y_val) - self._y_ind - 1
                    self._bsc102_y.move(i)
                    self._v = []
                    for self._x_ind, j in enumerate(self._x_val):
                        self._bsc102_x.move(j)
                        tk_sleep(self._master, self._time_constant * 1000 * 3)  # DO NOT USE TIME.SLEEP IN TKINTER LOOP
                        self.do_measurement()
                        self._fig.set_tight_layout(True)
                        self._canvas.draw()  # dynamically plots the data and closes automatically after completing the scan
                        self._master.update()
                        if self._abort:
                            self._bsc102_x.move(0)
                            self._bsc102_y.move(0)
                            break
                    self.do_cut_measurement()
                    self._fig.set_tight_layout(True)
                    self._canvas.draw()
                self._bsc102_x.move(0)
                self._bsc102_y.move(0)  # returns piezo controller position to 0,0
            else:
                for self._x_ind, i in enumerate(self._x_val):
                    self._master.update()
                    if self._abort:
                        self._bsc102_x.move(0)
                        self._bsc102_y.move(0)
                        break
                    if not self._direction:
                        self._x_ind = len(self._x_val) - self._x_ind - 1
                    self._bsc102_x.move(i)
                    self._v = []
                    for self._y_ind, j in enumerate(self._y_val):
                        self._bsc102_y.move(j)
                        self.do_measurement()
                        self._fig.set_tight_layout(True)
                        self._canvas.draw()  # dynamically plots the data and closes automatically after completing the scan
                        self._master.update()
                        if self._abort:
                            self._bsc102_x.move(0)
                            self._bsc102_y.move(0)
                            break
                    self.do_cut_measurement()
                    self._fig.set_tight_layout(True)
                    self._canvas.draw()
                self._bsc102_x.move(0)
                self._bsc102_y.move(0)  # returns piezo controller position to 0,0
            self.plot_final()

    def stop(self):
        self.plot_final()
        self._canvas.draw()
        warnings.filterwarnings("ignore", ".*GUI is implemented.*")  # this warning relates to code \
        # that was never written
        cid = self._fig.canvas.mpl_connect('button_press_event',
                                           self.onclick)  # click on pixel to move laser position there

    def do_cut_measurement(self):
        pass

    def main(self):
        self.main2('map scan', abort_button=True, center_beam=True)