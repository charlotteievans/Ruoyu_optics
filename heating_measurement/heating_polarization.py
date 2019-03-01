import matplotlib
matplotlib.use('TkAgg')
from optics.misc_utility.tkinter_utilities import tk_sleep
from optics.misc_utility import conversions
import time  # DO NOT USE TIME.SLEEP IN TKINTER MAINLOOP
from optics.measurements.base_polarization import PolarizationMeasurement


class HeatingPolarization(PolarizationMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, bias, osc,
                 sr7270_single_reference, powermeter, waveplate, steps):
        super().__init__(master, filepath, notes, device, scan, steps, gain=gain,
                         sr7270_single_reference=sr7270_single_reference,
                         powermeter=powermeter, waveplate=waveplate)
        self._bias = bias
        self._osc = osc

    def start(self):
        self._sr7270_single_reference.change_applied_voltage(self._bias)
        tk_sleep(self._master, 300)
        self._sr7270_single_reference.change_oscillator_amplitude(self._osc)
        tk_sleep(self._master, 300)

    def stop(self):
        self._sr7270_single_reference.change_applied_voltage(0)

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'polarization', 'x_raw', 'y_raw', 'iphoto_x', 'iphoto_y'])

    def setup_plots(self):
        self._ax1.title.set_text('|iphoto_X| (mA)')
        self._ax2.title.set_text('|iphoto_Y| (mA)')

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        iphoto = [conversions.convert_x_to_iphoto(x, self._gain) for x in raw]
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, self._polarization, raw[0], raw[1], iphoto[0], iphoto[1]])
        self._ax1.plot(conversions.degrees_to_radians(self._polarization), abs(iphoto[0]) * 1000, linestyle='',
                       color='blue', marker='o', markersize=2)
        self._ax2.plot(conversions.degrees_to_radians(self._polarization), abs(iphoto[1]) * 1000, linestyle='',
                       color='blue', marker='o', markersize=2)


class HeatingPolarizationRT(PolarizationMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, bias, osc,
                 sr7270_single_reference, powermeter, waveplate, steps):
        super().__init__(master, filepath, notes, device, scan, steps, gain=gain,
                         sr7270_single_reference=sr7270_single_reference,
                         powermeter=powermeter, waveplate=waveplate)
        self._bias = bias
        self._osc = osc

    def start(self):
        self._sr7270_single_reference.change_applied_voltage(self._bias)
        tk_sleep(self._master, 300)
        self._sr7270_single_reference.change_oscillator_amplitude(self._osc)
        tk_sleep(self._master, 300)

    def stop(self):
        self._sr7270_single_reference.change_applied_voltage(0)

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'polarization', 'r_raw', 'theta_raw', 'iphoto', 'theta'])

    def setup_plots(self):
        self._ax1.title.set_text('|R| (mA)')
        self._ax2.title.set_text('theta')

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_r_theta()
        iphoto = conversions.convert_x_to_iphoto(raw[0], self._gain)
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, self._polarization, raw[0], raw[1], iphoto, raw[1] / self._gain])
        self._ax1.plot(conversions.degrees_to_radians(self._polarization), abs(iphoto) * 1000, linestyle='',
                       color='blue', marker='o', markersize=2)
        self._ax2.plot(conversions.degrees_to_radians(self._polarization), abs(raw[1]) / self._gain, linestyle='',
                       color='blue', marker='o', markersize=2)
