import matplotlib
matplotlib.use('TkAgg')
from optics.misc_utility import conversions
from optics.measurements.base_time import TimeMeasurement
import time
from optics.misc_utility.tkinter_utilities import tk_sleep


class ThermovoltageTime(TimeMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, rate, maxtime,
                 sr7270_single_reference, powermeter, waveplate):
        super().__init__(master, filepath, notes, device, scan, rate, maxtime,
                         sr7270_single_reference=sr7270_single_reference, powermeter=powermeter, gain=gain,
                         waveplate=waveplate)
        self._voltages = []

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'x_raw', 'y_raw', 'x_v', 'y_v'])

    def setup_plots(self):
        self._ax1.title.set_text('X_1')
        self._ax2.title.set_text('Y_1')
        self._ax1.set_ylabel('voltage (uV)')
        self._ax2.set_ylabel('voltage (uV)')
        self._ax1.set_xlabel('time (s)')
        self._ax2.set_xlabel('time (s)')
        self._canvas.draw()

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        self._voltages = [conversions.convert_x_to_iphoto(x, self._gain) for x in raw]
        tk_sleep(self._master, self._sleep)
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, raw[0], raw[1], self._voltages[0], self._voltages[1]])
        self._ax1.plot(time_now, self._voltages[0] * 1000000, linestyle='', color='blue', marker='o', markersize=2)
        self._ax2.plot(time_now, self._voltages[1] * 1000000, linestyle='', color='blue', marker='o', markersize=2)
        self._fig.tight_layout()
        self._fig.canvas.draw()


class ThermovoltageTimeRT(TimeMeasurement):
    def __init__(self, master, filepath, notes, device, scan, gain, rate, maxtime,
                 sr7270_single_reference, powermeter, waveplate):
        super().__init__(master, filepath, notes, device, scan, rate, maxtime,
                         sr7270_single_reference=sr7270_single_reference, powermeter=powermeter, gain=gain,
                         waveplate=waveplate)
        self._voltages = []

    def end_header(self, writer):
        writer.writerow(['end:', 'end of header'])
        writer.writerow(['time', 'r_raw', 'theta_raw', 'r_v', 'theta'])

    def setup_plots(self):
        self._ax1.title.set_text('R')
        self._ax2.title.set_text('Theta')
        self._ax1.set_ylabel('voltage (uV)')
        self._ax2.set_ylabel('degrees')
        self._ax1.set_xlabel('time (s)')
        self._ax2.set_xlabel('time (s)')
        self._canvas.draw()

    def do_measurement(self):
        raw = self._sr7270_single_reference.read_xy()
        self._voltage = conversions.convert_x_to_iphoto(raw[0], self._gain)
        tk_sleep(self._master, self._sleep)
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, raw[0], raw[1], self._voltage, raw[1] / self._gain])
        self._ax1.plot(time_now, self._voltage * 1000000, linestyle='', color='blue', marker='o', markersize=2)
        self._ax2.plot(time_now, raw[1] / self._gain, linestyle='', color='blue', marker='o', markersize=2)
        self._fig.tight_layout()
        self._fig.canvas.draw()