import contextlib

import visa
from ThorlabsPM100 import ThorlabsPM100


@contextlib.contextmanager
def connect(address):
    rm = visa.ResourceManager()
    inst = rm.open_resource(address)
    try:
        yield PowerMeter(ThorlabsPM100(inst=inst))
    finally:
        inst.close()


class PowerMeter:
    def __init__(self, power_meter):
        self._power_meter = power_meter

    def read_power(self):
        return self._power_meter.read

