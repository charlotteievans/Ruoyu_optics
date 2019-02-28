import matplotlib
import time
matplotlib.use('Qt4Agg')  # this allows you to see the interactive plots!
import tkinter as tk
import numpy as np
from optics.hardware_control import pm100d, sr7270, polarizercontroller
import optics.hardware_control.hardware_addresses_and_constants as hw
from optics.thermovoltage_measurement.thermovoltage_polarization import ThermovoltagePolarization, \
    ThermovoltagePolarizationRT
from optics.thermovoltage_measurement.thermovoltage_time import ThermovoltageTime, ThermovoltageTimeRT
from optics.heating_measurement.heating_time import HeatingTime, HeatingTimeRT
from optics.heating_measurement.heating_polarization import HeatingPolarization, HeatingPolarizationRT
from contextlib import ExitStack
import datetime
import csv
import os
from os import path
from optics.gui.base_gui import BaseGUI


class BaseLockinGUI(BaseGUI):
    def __init__(self, master, sr7270_single_reference=None, powermeter=None, waveplate=None):
        self._master = master
        super().__init__(self._master)
        self._master.title('Optics setup measurements')
        self._sr7270_single_reference = sr7270_single_reference
        self._powermeter = powermeter
        self._waveplate = waveplate
        self._newWindow = None
        self._app = None

    def new_window(self, measurementtype):
        self._newWindow = tk.Toplevel(self._master)
        self._app = LockinMeasurementGUI(self._newWindow, sr7270_single_reference=self._sr7270_single_reference,
                                         powermeter=self._powermeter, waveplate=self._waveplate)
        measurement = {'heatpolarization': self._app.build_heating_polarization_gui,
                       'heatpolarizationrt': self._app.build_heating_polarization_rt_gui,
                       'ptepolarization': self._app.build_thermovoltage_polarization_gui,
                       'ptepolarizationrt': self._app.build_thermovoltage_polarization_rt_gui,
                       'heattime': self._app.build_heating_time_gui,
                       'heattimert': self._app.build_heating_time_rt_gui,
                       'ptetime': self._app.build_thermovoltage_time_gui,
                       'ptetimert': self._app.build_thermovoltage_time_rt_gui,
                       'polarization': self._app.build_change_polarization_gui,
                       'singlereference': self._app.build_single_reference_gui,
                       'measureresistance': self._app.build_measure_resistance_gui}
        measurement[measurementtype]()

    def build(self):
        row = self.makerow('polarization scans')
        if self._waveplate:
            self.make_measurement_button(row, 'thermovoltage', 'ptepolarization')
            self.make_measurement_button(row, 'thermovoltage rt', 'ptepolarizationrt')
            self.make_measurement_button(row, 'heating', 'heatpolarization')
            self.make_measurement_button(row, 'heating rt', 'heatpolarizationrt')
        else:
            self.makerow('Waveplate not connected', side=None, width=20)
        row = self.makerow('time scans')
        self.make_measurement_button(row, 'thermovoltage', 'ptetime')
        self.make_measurement_button(row, 'thermovoltage rt', 'ptetimert')
        self.make_measurement_button(row, 'heating', 'heattime')
        self.make_measurement_button(row, 'heating rt', 'heattimert')
        row = self.makerow('change parameters')
        self.make_measurement_button(row, 'polarization', 'polarization')
        row = self.makerow('measure resistance')
        self.make_measurement_button(row, 'lock in', 'measureresistance')
        row = self.makerow('single reference lock in')
        b1 = tk.Button(row, text='auto phase',
                       command=lambda lockin=self._sr7270_single_reference: self.autophase(lockin))
        b1.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.make_measurement_button(row, 'change parameters', 'singlereference')
        row = self.makerow('dual harmonic lock in')
        b12 = tk.Button(self._master, text='Quit all windows', command=self._master.quit)
        b12.pack()

    def autophase(self, lockin, event=None):
        lockin.auto_phase()


class LockinMeasurementGUI(BaseGUI):
    def __init__(self, master, sr7270_single_reference=None, powermeter=None, waveplate=None):
        self._master = master
        super().__init__(self._master)
        self._sr7270_single_reference = sr7270_single_reference
        self._powermeter = powermeter
        self._waveplate = waveplate
        self._direction = tk.StringVar()
        self._direction.set('Forward')
        self._axis = tk.StringVar()
        self._axis.set('y')
        self._current_gain = tk.StringVar()
        self._current_gain.set('1 mA/V')
        self._voltage_gain = tk.StringVar()
        self._voltage_gain.set(1000)
        self._tc = tk.StringVar()
        self._sen = tk.StringVar()
        self._tc1 = tk.StringVar()
        self._tc2 = tk.StringVar()
        self._sen1 = tk.StringVar()
        self._sen2 = tk.StringVar()
        self._abort = tk.StringVar()
        self._increase = tk.StringVar()

    def thermovoltage_time(self, event=None):
        self.fetch(event)
        run = ThermovoltageTime(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                self._inputs['device'], int(self._inputs['scan']), float(self._voltage_gain.get()),
                                float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                                self._sr7270_single_reference, self._powermeter, self._waveplate)
        run.main()

    def thermovoltage_time_rt(self, event=None):
        self.fetch(event)
        run = ThermovoltageTimeRT(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                self._inputs['device'], int(self._inputs['scan']), float(self._voltage_gain.get()),
                                float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                                self._sr7270_single_reference, self._powermeter, self._waveplate)
        run.main()

    def heating_time(self, event=None):
        self.fetch(event)
        run = HeatingTime(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                          self._inputs['device'], int(self._inputs['scan']),
                          float(self._current_amplifier_gain_options[self._current_gain.get()]),
                          float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                          float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                          self._sr7270_single_reference, self._powermeter, self._waveplate)
        run.main()

    def heating_time_rt(self, event=None):
        self.fetch(event)
        run = HeatingTimeRT(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                          self._inputs['device'], int(self._inputs['scan']),
                          float(self._current_amplifier_gain_options[self._current_gain.get()]),
                          float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                          float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                          self._sr7270_single_reference, self._powermeter, self._waveplate)
        run.main()

    def changepolarization(self):
        self.fetch()
        self._waveplate.move_nearest(float(float(self._inputs['desired polarization']) / 2))
        self.readpolarization()

    def readpolarization(self):
        self._textbox.delete(1.0, tk.END)
        self._textbox.insert(tk.END, self._waveplate.read_polarization())
        self._textbox.pack()
        self._textbox2.delete(1.0, tk.END)
        self._textbox2.insert(tk.END, (self._waveplate.read_position() % 180) * 2)
        self._textbox2.pack()

    def homewaveplate(self):
        self._waveplate.home()

    def thermovoltage_polarization(self, event=None):
        self.fetch(event)
        run = ThermovoltagePolarization(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                        self._inputs['device'], int(self._inputs['scan']),
                                        float(self._voltage_gain.get()), self._sr7270_single_reference,
                                        self._powermeter, self._waveplate, int(self._inputs['polarization steps']))
        run.main()

    def heating_polarization(self, event=None):
        self.fetch(event)
        run = HeatingPolarization(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                  self._inputs['device'], int(self._inputs['scan']),
                                  float(self._current_amplifier_gain_options[self._current_gain.get()]),
                                  float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                                  self._sr7270_single_reference, self._powermeter, self._waveplate,
                                  int(self._inputs['polarization steps']))
        run.main()

    def thermovoltage_polarization_rt(self, event=None):
        self.fetch(event)
        run = ThermovoltagePolarizationRT(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                        self._inputs['device'], int(self._inputs['scan']),
                                        float(self._voltage_gain.get()), self._sr7270_single_reference,
                                        self._powermeter, self._waveplate, int(self._inputs['polarization steps']))
        run.main()

    def heating_polarization_rt(self, event=None):
        self.fetch(event)
        run = HeatingPolarizationRT(tk.Toplevel(self._master), self._inputs['file path'], self._inputs['notes'],
                                  self._inputs['device'], int(self._inputs['scan']),
                                  float(self._current_amplifier_gain_options[self._current_gain.get()]),
                                  float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                                  self._sr7270_single_reference, self._powermeter, self._waveplate,
                                  int(self._inputs['polarization steps']))
        run.main()

    def change_single_reference_lockin_parameters(self, event=None):
        self.fetch(event)
        if self._tc.get() != '':
            self._sr7270_single_reference.change_tc(float(self._tc.get()))
        if self._sen.get() != '':
            self._sr7270_single_reference.change_sensitivity(float(self._sen.get()))
        print('lock in parameters: \ntime constant: {} ms\nsensitivity: {} '
              'mV'.format(self._sr7270_single_reference.read_tc() * 1000,
                          self._sr7270_single_reference.read_sensitivity() * 1000))

    def build_thermovoltage_time_gui(self):
        caption = "Thermovoltage vs. time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'rate (per second)': 3,
                        'max time (s)': 300}
        self.beginform(caption)
        self.make_option_menu('gain', self._voltage_gain, self._voltage_gain_options)
        self.endform(self.thermovoltage_time)

    def build_thermovoltage_time_rt_gui(self):
        caption = "Thermovoltage vs. time R Theta"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'rate (per second)': 3,
                        'max time (s)': 300}
        self.beginform(caption)
        self.make_option_menu('gain', self._voltage_gain, self._voltage_gain_options)
        self.endform(self.thermovoltage_time_rt)

    def build_change_polarization_gui(self):  # TODO fix this
        caption = "Change laser polarization"
        self._fields = {'desired polarization': 90}
        self.beginform(caption, False)
        self.maketextbox('current position', self._waveplate.read_polarization())
        self.maketextbox2('modulus polarization', (self._waveplate.read_position() % 90) * 2)
        self.makebutton('Change polarization', self.changepolarization)
        self.makebutton('Read polarization', self.readpolarization)
        self.makebutton('Home', self.homewaveplate)
        self.makebutton('Quit', self._master.destroy)

    def build_thermovoltage_polarization_gui(self):
        caption = "Thermovoltage vs. polarization"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'polarization steps': 5}
        self.beginform(caption)
        self.make_option_menu('gain', self._voltage_gain, self._voltage_gain_options)
        self.endform(self.thermovoltage_polarization)

    def build_thermovoltage_polarization_rt_gui(self):
        caption = "Thermovoltage vs. polarization R vs theta"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'polarization steps': 5}
        self.beginform(caption)
        self.make_option_menu('gain', self._voltage_gain, self._voltage_gain_options)
        self.endform(self.thermovoltage_polarization_rt)

    def build_heating_polarization_gui(self):
        caption = "Heating vs. polarization"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'bias (mV)': 5,
                        'oscillator amplitude (mV)': 7, 'polarization steps': 5}
        self.beginform(caption)
        self.make_option_menu('gain', self._current_gain, self._current_amplifier_gain_options.keys())
        self.endform(self.heating_polarization)

    def build_heating_polarization_rt_gui(self):
        caption = "Heating vs. polarization R vs Theta"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'bias (mV)': 5,
                        'oscillator amplitude (mV)': 7, 'polarization steps': 5}
        self.beginform(caption)
        self.make_option_menu('gain', self._current_gain, self._current_amplifier_gain_options.keys())
        self.endform(self.heating_polarization_rt)

    def build_heating_time_gui(self):
        caption = "Heating vs. time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'rate (per second)': 3,
                        'max time (s)': 300, 'bias (mV)': 5, 'oscillator amplitude (mV)': 7}
        self.beginform(caption)
        self.make_option_menu('gain', self._current_gain, self._current_amplifier_gain_options.keys())
        self.endform(self.heating_time)

    def build_heating_time_rt_gui(self):
        caption = "Heating vs. time R vs Theta"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'rate (per second)': 3,
                        'max time (s)': 300, 'bias (mV)': 5, 'oscillator amplitude (mV)': 7}
        self.beginform(caption)
        self.make_option_menu('gain', self._current_gain, self._current_amplifier_gain_options.keys())
        self.endform(self.heating_time_rt)

    def build_single_reference_gui(self):
        caption = "Change single reference lock in parameters"
        self.beginform(caption, False)
        self.make_option_menu('time constant (s)', self._tc, self._time_constant_options)
        self.make_option_menu('sensitivity (mV)', self._sen, self._lockin_sensitivity_options)
        self.endform(self.change_single_reference_lockin_parameters)

    def build_measure_resistance_gui(self):
        caption = 'Measure lock in resistance'
        self._fields = {'file path': '', 'file name': str(datetime.date.today()) + ' resistance measurements',
                        'device': '', 'notes': ''}
        self.beginform(caption, True)
        self.make_option_menu('Current amplifier gain', self._current_gain, self._current_amplifier_gain_options)
        self.maketextbox('Resistance (ohms)', str(''))
        self.maketextbox2('Corrected resistance (ohms)', str(''))
        self.endform(self.resistance)

    def resistance(self, event=None):
        self.fetch(event)
        gain = float(self._current_amplifier_gain_options[self._current_gain.get()])
        osc = self._sr7270_single_reference.read_oscillator_amplitude()
        x, y = self._sr7270_single_reference.read_xy()
        resistance = osc / x * gain
        self._textbox.delete(1.0, tk.END)
        self._textbox.insert(tk.END, resistance)
        self._textbox2.delete(1.0, tk.END)
        self._textbox2.insert(tk.END, resistance - 51)
        self._textbox.pack()
        if path.exists(path.join(self._inputs['file path'], self._inputs['file name'] + '.csv')):
            file_type = 'a'
        else:
            file_type = 'w'
        with open(path.join(self._inputs['file path'], self._inputs['file name'] + '.csv'), file_type, newline='') as q:
            writer = csv.writer(q)
            if file_type == 'w':
                writer.writerow(['device', 'notes', 'total resistance (ohms)', 'corrected resistance (ohms)',
                                 'osc. amplitude (V)', 'gain', 'raw x', 'raw y'])
            writer.writerow([self._inputs['device'], self._inputs['notes'], resistance,
                             resistance - 51, osc, gain, x, y])

    def build_coming_soon(self):
        caption = "Coming soon"
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        self.makebutton('Quit', self._master.destroy)


def main():
    sr7270_single_reference = None
    print('connecting hardware')
    try:
        with ExitStack() as cm:
            lock_in = cm.enter_context(sr7270.create_endpoints_single(hw.vendor, hw.product))
            mode = lock_in.check_reference_mode()
            if mode == 0.0:
                sr7270_single_reference = lock_in
            if not sr7270_single_reference:
                print('Lock in amplifier not configured correctly. Be sure to be in the single reference mode')
                raise ValueError
            try:
                powermeter = cm.enter_context(pm100d.connect(hw.pm100d_address))
            except Exception as err:
                if 'NFOUND' in str(err):
                    print('Warning: PM100D power detector not connected')
                else:
                    print('Warning: {}'.format(err))
                powermeter = None
            try:
                waveplate = cm.enter_context(polarizercontroller.connect_tdc001(hw.tdc001_serial_number,
                                                                                waveplate=True))
            except Exception:
                waveplate = None
                print('Warning: Waveplate controller not connected')
            print('hardware connection complete')
            root = tk.Tk()
            app = BaseLockinGUI(root, sr7270_single_reference=sr7270_single_reference,
                                powermeter=powermeter, waveplate=waveplate)
            app.build()
            root.mainloop()
    except Exception as err:
        print(err)
        input('Press enter to exit')



if __name__ == '__main__':
    main()