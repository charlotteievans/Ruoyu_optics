import matplotlib
matplotlib.use('TkAgg')
from optics.misc_utility import conversions
import time  # DO NOT USE TIME.SLEEP IN TKINTER MAINLOOP
from optics.measurements.base_polarization import PolarizationMeasurement


class ThermovoltagePolarization(PolarizationMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, sr7270_single_reference, powermeter,
                 waveplate, steps):
        super().__init__(master, filepath, notes, device, scan, steps, gain=gain,
                         sr7270_single_reference=sr7270_single_reference,
                         powermeter=powermeter, waveplate=waveplate)

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'polarization', 'x_raw', 'y_raw', 'x_v', 'y_v'])

    def setup_plots(self):
        self._ax1.title.set_text('|X_1| (uV)')
        self._ax2.title.set_text('|Y_1| (uV)')

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        voltages = [conversions.convert_x_to_iphoto(x, self._gain) for x in raw]
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, self._polarization, raw[0], raw[1], voltages[0], voltages[1]])
        self._ax1.plot(conversions.degrees_to_radians(self._polarization), abs(voltages[0]) * 1000000,
                       linestyle='', color='blue', marker='o', markersize=2)
        self._ax2.plot(conversions.degrees_to_radians(self._polarization), abs(voltages[1]) * 1000000,
                       linestyle='', color='blue', marker='o', markersize=2)


class ThermovoltagePolarizationRT(PolarizationMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, sr7270_single_reference, powermeter,
                 waveplate, steps):
        super().__init__(master, filepath, notes, device, scan, steps, gain=gain,
                         sr7270_single_reference=sr7270_single_reference,
                         powermeter=powermeter, waveplate=waveplate)

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'polarization', 'r_raw', 'theta_raw', 'r_v', 'theta'])

    def setup_plots(self):
        self._ax1.title.set_text('|R| (uV)')
        self._ax2.title.set_text('Theta')

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        voltage = conversions.convert_x_to_iphoto(raw[0], self._gain)
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, self._polarization, raw[0], raw[1], voltage, raw[1] / self._gain])
        self._ax1.plot(conversions.degrees_to_radians(self._polarization), abs(voltage) * 1000000,
                       linestyle='', color='blue', marker='o', markersize=2)
        self._ax2.plot(conversions.degrees_to_radians(self._polarization), abs(raw[1])/self._gain,
                       linestyle='', color='blue', marker='o', markersize=2)
