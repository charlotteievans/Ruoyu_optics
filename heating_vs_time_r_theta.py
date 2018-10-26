import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import time
import csv
from optics import conversions
import os
from os import path


class HeatingTimeRTheta:
    def __init__(self, filepath, notes, device, scan, gain, rate, maxtime, bias, osc, lockin):
        self._filepath = filepath
        self._notes = notes
        self._device = device
        self._scan = scan
        self._gain = gain
        self._lockin = lockin
        self._rate = rate
        self._maxtime = maxtime
        self._writer = None
        self._fig, (self._ax1, self._ax2) = plt.subplots(2)
        self._max_iphoto_x = 0
        self._min_iphoto_x = 0
        self._start_time = None
        self._iphoto = None
        self._sleep = 1 / self._rate
        self._bias = bias
        self._osc = osc
        self._file = None
        self._imagefile = None

    def write_header(self):
        self._writer.writerow(['device:', self._device])
        self._writer.writerow(['scan:', self._scan])
        self._writer.writerow(['gain:', self._gain])
        self._writer.writerow(['applied voltage (V):', self._lockin.read_applied_voltage()])
        self._writer.writerow(['osc amplitude (V):', self._lockin.read_oscillator_amplitude()])
        self._writer.writerow(['osc frequency:', self._lockin.read_oscillator_frequency()])
        self._writer.writerow(['time constant:', self._lockin.read_tc()])
        self._writer.writerow(['notes:', self._notes])
        self._writer.writerow(['end:', 'end of header'])
        self._writer.writerow(['time', 'r_raw', 'iphoto_r', 'theta'])

    def makefile(self):
        os.makedirs(self._filepath, exist_ok=True)
        index = self._scan
        self._file = path.join(self._filepath, '{}_{}{}'.format(self._device, index, '.csv'))
        self._imagefile = path.join(self._filepath, '{}_{}{}'.format(self._device, index, '.png'))
        while path.exists(self._file):
            index += 1
            self._file = path.join(self._filepath, '{}_{}{}'.format(self._device, index, '.csv'))
            self._imagefile = path.join(self._filepath, '{}_{}{}'.format(self._device, index, '.png'))

    def setup_plots(self):
        self._ax1.title.set_text('R')
        self._ax2.title.set_text('Theta')
        self._ax1.set_ylabel('current (mA)')
        self._ax2.set_ylabel('degrees')
        self._ax1.set_xlabel('time (s)')
        self._ax2.set_xlabel('time (s)')
        self._fig.show()

    def set_limits(self):
        if self._iphoto > self._max_iphoto_x:
            self._max_iphoto_x = self._iphoto
        if self._iphoto < self._min_iphoto_x:
            self._min_iphoto_x = self._iphoto
        if 0 < self._min_iphoto_x < self._max_iphoto_x:
            self._ax1.set_ylim(self._min_iphoto_x * 1000 / 1.3, self._max_iphoto_x * 1.3 * 1000)
        if self._min_iphoto_x < 0 < self._max_iphoto_x:
            self._ax1.set_ylim(self._min_iphoto_x * 1.3 * 1000, self._max_iphoto_x * 1.3 * 1000)
        if self._min_iphoto_x < self._max_iphoto_x < 0:
            self._ax1.set_ylim(self._min_iphoto_x * 1.3 * 1000, self._max_iphoto_x * 1 / 1.3 * 1000)

    def measure(self):
        raw = self._lockin.read_r_theta()
        self._iphoto = conversions.convert_x_to_iphoto(raw[0], self._gain)
        time.sleep(self._sleep)
        time_now = time.time() - self._start_time
        self._writer.writerow([time_now, raw[0], self._iphoto, raw[1]/self._gain])
        self._ax1.scatter(time_now, self._iphoto * 1000, c='c', s=2)
        self._ax2.scatter(time_now, raw[1]/self._gain, c='c', s=2)
        self.set_limits()
        plt.tight_layout()
        self._fig.canvas.draw()

    def main(self):
        self.makefile()
        with open(self._file, 'w', newline='') as inputfile:
            try:
                self._lockin.change_applied_voltage(self._bias)
                time.sleep(0.3)
                self._lockin.change_oscillator_amplitude(self._osc)
                time.sleep(0.3)
                self._start_time = time.time()
                self._writer = csv.writer(inputfile)
                self.write_header()
                self.setup_plots()
                while time.time() - self._start_time < self._maxtime:
                    self.measure()
                plt.savefig(self._imagefile, format='png', bbox_inches='tight')
                self._lockin.change_applied_voltage(0)
            except KeyboardInterrupt:
                plt.savefig(self._imagefile, format='png', bbox_inches='tight')  # saves an image of the completed data
                self._lockin.change_applied_voltage(0)