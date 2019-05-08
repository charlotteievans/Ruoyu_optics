import matplotlib
matplotlib.use('TkAgg')
from optics.misc_utility import conversions
from optics.measurements.base_map import MapScan
import numpy as np
from optics.misc_utility.tkinter_utilities import tk_sleep
from optics.heating_plot import heating_plot
import matplotlib.pyplot as plt

class HeatingMapScan(MapScan):
    def __init__(self, master, filepath, notes, device, scan, gain, xd, yd, xr, yr, xc, yc, bias, osc,
                 bsc102_x, bsc102_y, sr7270_single_reference, powermeter, waveplate, direction, axis):
        super().__init__(master, filepath, notes, device, scan, gain, xd, yd, xr, yr, xc, yc,
                         bsc102_x, bsc102_y, sr7270_single_reference, powermeter=powermeter, waveplate=waveplate,
                         direction=direction, axis=axis)
        self._bias = bias
        self._osc = osc

    def start(self):
        self._sr7270_single_reference.change_applied_voltage(self._bias)
        tk_sleep(self._master, 300)
        self._sr7270_single_reference.change_oscillator_amplitude(self._osc)
        self._im1 = self._ax1.imshow(self._z1.T, cmap=plt.cm.coolwarm, interpolation='nearest', origin='lower')
        self._im2 = self._ax2.imshow(self._z2.T, cmap=plt.cm.coolwarm, interpolation='nearest', origin='lower')
        self._clb1 = self._fig.colorbar(self._im1, ax=self._ax1)
        self._clb2 = self._fig.colorbar(self._im2, ax=self._ax2)

    def stop2(self):
        self._sr7270_single_reference.change_applied_voltage(0)

    def end_header(self, writer):
        writer.writerow(['x scan density:', self._xd])
        writer.writerow(['y scan density:', self._yd])
        writer.writerow(['x scan range:', self._xr])
        writer.writerow(['y scan range:', self._yr])
        writer.writerow(['x center:', self._xc])
        writer.writerow(['y center:', self._yc])
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['x_raw', 'y_raw', 'x_iphoto', 'y_iphoto', 'x_pixel', 'y_pixel'])

    def setup_plots(self):
        self._clb1.set_label('current (mA)', rotation=270, labelpad=20)
        self._clb2.set_label('current (mA)', rotation=270, labelpad=20)
        self._ax1.title.set_text('iphoto X')
        self._ax2.title.set_text('iphoto Y')
        self._ax3.title.set_text('iphoto X max signal cut through')
        self._ax4.title.set_text('iphoto Y max signal cut through')
        self._ax3.set_xlabel('pixel')
        self._ax4.set_xlabel('pixel')
        self._ax3.set_ylabel('current (mA)')
        self._ax4.set_ylabel('current (mA)')
        if self._axis == 'y':
            self._ax3.set_xlim(0, self._yd - 1, 1)
            self._ax4.set_xlim(0, self._yd - 1, 1)
        else:
            self._ax3.set_xlim(0, self._xd - 1, 1)
            self._ax4.set_xlim(0, self._xd - 1, 1)

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        currents = [conversions.convert_x_to_iphoto(x, self._gain) for x in raw]
        self._v.append(currents)
        self._writer.writerow([raw[0], raw[1], currents[0], currents[1], self._x_ind, self._y_ind])
        self._z1[self._x_ind][self._y_ind] = currents[0] * 1000
        self._z2[self._x_ind][self._y_ind] = currents[1] * 1000
        self.update_plot(self._im1, self._z1, np.amin(self._z1), np.amax(self._z1))
        self.update_plot(self._im2, self._z2, np.amin(self._z2), np.amax(self._z2))

    def do_cut_measurement(self):
        v_x_cut = np.mean(sorted([i[0] for i in self._v], key=abs)[-3:-1])
        v_y_cut = np.mean(sorted([i[1] for i in self._v], key=abs)[-3:-1])
        if self._axis == 'y':
            self._ax3.plot(self._y_ind, v_x_cut * 1000,
                           linestyle='', color='blue', marker='o', markersize=2)
            self._ax4.plot(self._y_ind, v_y_cut * 1000,
                           linestyle='', color='blue', marker='o', markersize=2)
            self._cut_writer.writerow([self._y_ind, v_x_cut, v_y_cut])
        else:
            self._cut_writer.writerow([self._x_ind, v_x_cut, v_y_cut])
            self._ax3.plot(self._x_ind, v_x_cut * 1000,
                           linestyle='', color='blue', marker='o', markersize=2)
            self._ax4.plot(self._x_ind, v_y_cut * 1000,
                           linestyle='', color='blue', marker='o', markersize=2)

    @staticmethod
    def update_plot(im, data, min_val, max_val):
        im.set_data(data.T)
        im.set_clim(vmin=min_val)
        im.set_clim(vmax=max_val)

    def plot_final(self):
        heating_plot.plot(self._ax1, self._im1, self._z1, np.amax(self._z1), np.amin(self._z1))
        heating_plot.plot(self._ax2, self._im2, self._z2, np.amax(self._z2), np.amin(self._z2))