from optics.measurements.base_measurement import LockinBaseMeasurement
import time


class TimeMeasurement(LockinBaseMeasurement):
    def __init__(self, master, filepath, notes, device, scan, rate, maxtime, npc3sg_input=None,
                 sr7270_single_reference=None, powermeter=None, waveplate=None, sr7270_dual_harmonic=None, gain=None,
                 daq_input=None, ccd=None, mono=None):
        super().__init__(master=master, filepath=filepath, device=device, npc3sg_input=npc3sg_input,
                         sr7270_dual_harmonic=sr7270_dual_harmonic, sr7270_single_reference=sr7270_single_reference,
                         powermeter=powermeter, waveplate=waveplate, notes=notes, gain=gain, daq_input=daq_input,
                         ccd=ccd, mono=mono)
        self._maxtime = maxtime
        self._scan = scan
        self._sleep = 1 / rate * 1000

    def load(self):
        self._ax1 = self._fig.add_subplot(211)
        self._ax2 = self._fig.add_subplot(212)

    def measure(self):
        self._master.update()
        self.do_measurement()
        self._master.update()
        if not self._abort and time.time() - self._start_time < self._maxtime:
            self.measure()

    def main(self):
        self.main2('intensity scan', record_power=False)
