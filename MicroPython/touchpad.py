# Give stdevs away 

import machine
from rollingaverage import RollingStats

class TouchPad:
    def __init__(self, pin_num, trigger, buffersize=300):
        self.sensor    = machine.TouchPad(machine.Pin(pin_num))
        self.readings  = RollingStats(n=buffersize, init_val=self.sensor.read())
        self.threshold = trigger
        
    def calibrate_step(self):
        self.readings.update(self.sensor.read())

    def read(self):
        sensor_val    = self.sensor.read()
        dist_mean     = self.readings.avg - sensor_val
        z_score       = 0
        stdev_vals    = self.readings.pseudo_std_dev()
        if stdev_vals != 0:
            z_score = dist_mean / abs(self.readings.pseudo_std_dev()) # z-score
        if z_score < self.threshold:
            self.readings.update(sensor_val)
        return z_score