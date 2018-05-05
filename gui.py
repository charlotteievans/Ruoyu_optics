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
                       'ptetimertheta': self._app.build_thermovoltage_time_rtheta_gui}
        measurement[measurementtype]()

    def build(self):
        row = tk.Frame(self._master)
        lab = tk.Label(row, width=20, text='time scans', anchor='w')
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
        self._browse_button = tk.Button(self._master, text="Browse", command=self.onclick_browse)

    def makeform(self):
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

    def build_thermovoltage_time_gui(self):
        caption = "Thermovoltage vs. time"
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60}
        self._browse_button.pack()
        self.makeform()
        self._master.bind('<Return>', self.thermovoltage_time)
        b1 = tk.Button(self._master, text='Run', command=self.thermovoltage_time)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self._master, text='Quit', command=self._master.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def build_thermovoltage_time_rtheta_gui(self):
        caption = "R Theta Thermovoltage vs. time"
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60}
        self._browse_button.pack()
        self.makeform()
        self._master.bind('<Return>', self.thermovoltage_time_r_theta)
        b1 = tk.Button(self._master, text='Run', command=self.thermovoltage_time_r_theta)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self._master, text='Quit', command=self._master.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def build_heating_time_gui(self):
        caption = "Heating vs. time"
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60, 'bias (mV)': 5, 'oscillator amplitude (mV)': 7}
        self._browse_button.pack()
        self.makeform()
        self._master.bind('<Return>', self.heating_time)
        b1 = tk.Button(self._master, text='Run', command=self.heating_time)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self._master, text='Quit', command=self._master.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def build_heating_time_rtheta_gui(self):
        caption = "R Theta Heating vs. time"
        self._master.title(caption)
        label = tk.Label(self._master, text=caption)
        label.pack()
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'gain': 1000,
                        'rate (per second)': 3, 'max time (s)': 60, 'bias (mV)': 5, 'oscillator amplitude (mV)': 7}
        self._browse_button.pack()
        self.makeform()
        self._master.bind('<Return>', self.heating_time_r_theta)
        b1 = tk.Button(self._master, text='Run', command=self.heating_time_r_theta)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self._master, text='Quit', command=self._master.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

def main():
    with sr7270.create_endpoints_single(setup_constants.vendor, setup_constants.product) as lockin:
        root = tk.Tk()
        app = BaseGUI(root, lockin)
        app.build()
        root.mainloop()

if __name__ == '__main__':
    main()






