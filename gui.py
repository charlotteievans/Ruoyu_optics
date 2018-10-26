import tkinter as tk
import tkinter.filedialog
from optics.thermovoltage_vs_time import ThermovoltageTime
from optics.heating_vs_time import HeatingTime
from optics.thermovoltage_vs_time_r_theta import ThermovoltageTimeRTheta
from optics.heating_vs_time_r_theta import HeatingTimeRTheta
from optics import setup_constants, sr7270


class BaseGUI:
    def __init__(self, master, lockin=None):
        self._master = master
        self._master.title('Optics setup measurement')
        self._app = None
        self._new_window = None
        self._lockin = lockin

    def new_window(self, measurementtype):
        self._new_window = tk.Toplevel(self._master)
        self._app = MeasurementGUI(self._new_window, self._lockin)
        measurement = {'heattime': self._app.build_heating_time_gui, 'ptetime': self._app.build_thermovoltage_time_gui,
                       'heattimertheta': self._app.build_heating_time_rtheta_gui,
                       'ptetimertheta': self._app.build_thermovoltage_time_rtheta_gui,
                       'changelockinparams': self._app.build_change_lockin_parameters_gui}
        measurement[measurementtype]()

    def build(self):
        row = tk.Frame(self._master)
        lab = tk.Label(row, width=20, text='Time scans', anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        b1 = tk.Button(row, text='thermovoltage',
                       command=lambda measurementtype='ptetime': self.new_window(measurementtype))
        b1.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b2 = tk.Button(row, text='heating',
                       command=lambda measurementtype='heattime': self.new_window(measurementtype))
        b2.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        row = tk.Frame(self._master)
        lab = tk.Label(row, width=20, text='R Theta time scans', anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        b3 = tk.Button(row, text='thermovoltage',
                       command=lambda measurementtype='ptetimertheta': self.new_window(measurementtype))
        b3.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b4 = tk.Button(row, text='heating',
                       command=lambda measurementtype='heattimertheta': self.new_window(measurementtype))
        b4.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        row = tk.Frame(self._master)
        lab = tk.Label(row, width=20, text='Change parameters', anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        b3 = tk.Button(row, text='lock in',
                       command=lambda measurementtype='changelockinparams': self.new_window(measurementtype))
        b3.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        b5 = tk.Button(self._master, text='Quit all windows', command=self._master.quit)
        b5.pack()


class MeasurementGUI:
    def __init__(self, master, lockin=None):
        self._master = master
        self._fields = {}
        self._entries = []
        self._inputs = {}
        self._lockin = lockin
        self._textbox = None
        self._textbox2 = None
        self._filepath = tk.StringVar()
        self._sensitivity = tk.StringVar()
        self._reference = tk.StringVar()
        self._sensitivity.set(5)
        self._reference.set('internal')
        self._time_constant = tk.StringVar()
        self._time_constant.set(1)
        self._browse_button = tk.Button(self._master, text="Browse", command=self.onclick_browse)

    def beginform(self, caption, browse_button=True):
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        if browse_button:
            self._browse_button.pack()
        for key in self._fields:
            row = tk.Frame(self._master)
            lab = tk.Label(row, width=15, text=key, anchor='w')
            if key == 'file path':
                ent = tk.Entry(row, textvariable=self._filepath)
            else:
                ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            ent.insert(0, str(self._fields[key]))
            self._entries.append((key, ent))
        return self._entries

    def endform(self, run_command):
        self._master.bind('<Return>', run_command)
        b1 = tk.Button(self._master, text='Run', command=run_command)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self._master, text='Quit', command=self._master.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def make_option_menu(self, label, parameter, option_list):
        row = tk.Frame(self._master)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab = tk.Label(row, width=15, text=label, anchor='w')
        lab.pack(side=tk.LEFT)
        t = tk.OptionMenu(row, parameter, *option_list)
        t.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

    def fetch(self, event=None):  # stop trying to make fetch happen. It's not going to happen. -Regina, Mean Girls
        for entry in self._entries:
            field = entry[0]
            text = entry[1].get()
            self._inputs[field] = text

    def onclick_browse(self):
        self._filepath.set(tkinter.filedialog.askdirectory())

    def thermovoltage_time(self, event=None):
        self.fetch(event)
        run = ThermovoltageTime(self._inputs['file path'], self._inputs['notes'], self._inputs['device'],
                                int(self._inputs['scan']), float(self._inputs['gain']),
                                float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                                self._lockin)
        run.main()

    def thermovoltage_time_r_theta(self, event=None):
        self.fetch(event)
        run = ThermovoltageTimeRTheta(self._inputs['file path'], self._inputs['notes'], self._inputs['device'],
                                int(self._inputs['scan']), float(self._inputs['gain']),
                                float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                                self._lockin)
        run.main()

    def heating_time(self, event=None):
        self.fetch(event)
        run = HeatingTime(self._inputs['file path'], self._inputs['notes'], self._inputs['device'],
                          int(self._inputs['scan']), float(self._inputs['gain']),
                          float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                          float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                          self._lockin)
        run.main()

    def heating_time_r_theta(self, event=None):
        self.fetch(event)
        run = HeatingTimeRTheta(self._inputs['file path'], self._inputs['notes'], self._inputs['device'],
                          int(self._inputs['scan']), float(self._inputs['gain']),
                          float(self._inputs['rate (per second)']), float(self._inputs['max time (s)']),
                          float(self._inputs['bias (mV)']), float(self._inputs['oscillator amplitude (mV)']),
                          self._lockin)
        run.main()

    def change_lockin_parameters(self, event=None):
        self.fetch(event)
        self._lockin.change_applied_voltage(float(self._inputs['bias (mV)']))
        self._lockin.change_tc(float(self._time_constant.get()))
        self._lockin.change_sensitivity(float(self._sensitivity.get()))
        self._lockin.change_reference_source(self._reference.get())
        if self._reference.get() == 'internal':
            self._lockin.change_oscillator_amplitude(float(self._inputs['oscillator amplitude (mV)']))
            self._lockin.change_oscillator_frequency(float(self._inputs['oscillator frequency (Hz)']))

    def build_thermovoltage_time_gui(self):
        caption = "Thermovoltage vs. time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60}
        self.beginform(caption)
        self.endform(self.thermovoltage_time)

    def build_thermovoltage_time_rtheta_gui(self):
        caption = "R Theta Thermovoltage vs. Time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60}
        self.beginform(caption)
        self.endform(self.thermovoltage_time_r_theta)

    def build_heating_time_gui(self):
        caption = "Heating vs. time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60, 'bias (mV)': 0, 'oscillator amplitude (mV)': 3}
        self.beginform(caption)
        self.endform(self.heating_time)

    def build_heating_time_rtheta_gui(self):
        caption = "R Theta Heating vs. time"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60, 'bias (mV)': 0, 'oscillator amplitude (mV)': 3}
        self.beginform(caption)
        self.endform(self.heating_time_r_theta)
        self._master.bind('<Return>', self.heating_time_r_theta)

    def autophase(self, lockin, event=None):
        lockin.auto_phase()

    def build_change_lockin_parameters_gui(self):
        caption = "Change lock in parameters"
        self._fields = {'bias (mV)': '', 'oscillator amplitude (mV)': '',
                        'oscillator frequency (Hz)': ''}
        self.beginform(caption, False)
        self.make_option_menu('time constant (s)', self._time_constant,
                              [1e-3, 2e-3, 5e-3, 10e-03, 20e-03, 50e-03, 100e-03, 200e-03, 500e-03, 1, 2, 5, 10])
        self.make_option_menu('sensitivity (mV)', self._sensitivity, [1e-2, 2e-2, 5e-2, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20,
                                                                      50])
        self.make_option_menu('reference source', self._reference, ['internal', 'external - rear panel',
                                                                    'external - front panel'])
        row = tk.Frame(self._master)
        lab = tk.Label(row, width=20, text='Auto phase', anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        b1 = tk.Button(row, text='Auto phase', command=lambda lockin=self._lockin: self.autophase(lockin))
        b1.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.endform(self.change_lockin_parameters)


def main():
    with sr7270.create_endpoints_single(setup_constants.vendor, setup_constants.product) as lockin:
        root = tk.Tk()
        app = BaseGUI(root, lockin)
        app.build()
        root.mainloop()

if __name__ == '__main__':
    main()






