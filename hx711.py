import time
from machine import Pin

class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.dout = Pin(dout_pin, Pin.IN, pull=Pin.PULL_UP)
        self.pd_sck = Pin(pd_sck_pin, Pin.OUT)
        self.pd_sck.value(0)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.set_gain(gain)

    def is_ready(self):
        return self.dout.value() == 0

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        else:
            raise ValueError('Gain must be 128, 64, or 32')

        self.read_raw()  # Appel pour valider le gain

    def read_raw(self):
        # Attendre que le capteur soit prêt
        while not self.is_ready():
            time.sleep_us(10)

        data = 0
        for _ in range(24):
            self.pd_sck.value(1)
            time.sleep_us(1)
            data = (data << 1) | self.dout.value()
            self.pd_sck.value(0)
            time.sleep_us(1)

        # Bits supplémentaires pour le gain
        for _ in range(self.GAIN):
            self.pd_sck.value(1)
            time.sleep_us(1)
            self.pd_sck.value(0)
            time.sleep_us(1)

        # Convertir les données en nombre signé
        if data & 0x800000:
            data -= 0x1000000

        return data

    def read_average(self, times=10):
        total = 0
        for _ in range(times):
            total += self.read_raw()
        return total // times

    def tare(self, times=15):
        self.OFFSET = self.read_average(times)

    def set_scale(self, scale):
        self.SCALE = scale

    def get_value(self, times=3):
        return self.read_average(times) - self.OFFSET

    def get_weight(self, times=3):
        return self.get_value(times) / self.SCALE

