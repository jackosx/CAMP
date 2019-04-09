import machine
import time
import struct
from micropython import const

class CapSensor:

    _CAP1188_MID                = const(0x5D)
    _CAP1188_PID                = const(0x50)
    _CAP1188_MAIN_CONTROL       = const(0x00)
    _CAP1188_GENERAL_STATUS     = const(0x02)
    _CAP1188_INPUT_STATUS       = const(0x03)
    _CAP1188_LED_STATUS         = const(0x04)
    _CAP1188_NOISE_FLAGS        = const(0x0A)
    _CAP1188_DELTA_COUNT        =(const(0x10),
                                  const(0x11),
                                  const(0x12),
                                  const(0x13),
                                  const(0x14),
                                  const(0x15),
                                  const(0x16),
                                  const(0x17))
    _CAP1188_SENSITIVTY         = const(0x1F)
    _CAP1188_CAL_ACTIVATE       = const(0x26)
    _CAP1188_MULTI_TOUCH_CFG    = const(0x2A)
    _CAP1188_THESHOLD_1         = const(0x30)
    _CAP1188_STANDBY_CFG        = const(0x41)
    _CAP1188_LED_LINKING        = const(0x72)
    _CAP1188_PRODUCT_ID         = const(0xFD)
    _CAP1188_MANU_ID            = const(0xFE)
    _CAP1188_REVISION           = const(0xFF)
    # pylint: enable=bad-whitespace

    _SENSITIVITY = (128, 64, 32, 16, 8, 4, 2, 1)

    def __init__(self, scl=21, sda=22):
        self.six_byte_buffer = bytearray(6)
        self.one_byte_buffer = bytearray(1)
        self.i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
        self.address = 41#self.i2c.scan()[0]
        print("Reset and wait for chip to be ready.")
        mid = self._read_register(_CAP1188_MANU_ID)
        if mid != _CAP1188_MID:
            raise RuntimeError('Failed to find CAP1188! Manufacturer ID: 0x{:02x}'.format(mid))
        pid = self._read_register(_CAP1188_PRODUCT_ID)
        if pid != _CAP1188_PID:
            raise RuntimeError('Failed to find CAP1188! Product ID: 0x{:02x}'.format(pid))
        self._channels = [None]*8
        self._write_register(_CAP1188_LED_LINKING, 0xFF)     # turn on LED linking
        self._write_register(_CAP1188_MULTI_TOUCH_CFG, 0x80) # allow multi touch
        self._write_register(0x2B, 0x00) # Multiple Touch Pattern Config
        self._write_register(0x2D, 0xFF) # Multiple Touch Pattern Register
        self._write_register(0x2F, 0x10) # turn off input-1-sets-all-inputs feature, Recalibration Configuration reg
        self.recalibrate()

    def __getitem__(self, key):
        pin = key
        index = key - 1
        if pin < 1 or pin > 8:
            raise IndexError('Pin must be a value 1-8.')
        if self._channels[index] is None:
            self._channels[index] = CAP1188_Channel(self, pin)
        return self._channels[index]

    def touched_pins(self):
        """A tuple of touched state for all pins."""
        touched = self.touched()
        return tuple([bool(touched >> i & 0x01) for i in range(8)])

    def touched(self):
        """Return 8 bit value representing touch state of all pins."""
        # clear the INT bit and any previously touched pins
        current = self._read_register(_CAP1188_MAIN_CONTROL)
        self._write_register(_CAP1188_MAIN_CONTROL, current & ~0x01)
        # return only currently touched pins
        return self._read_register(_CAP1188_INPUT_STATUS)


    def get_sensitivity(self):
        """The sensitvity of touch detections. Range is 1 (least) to 128 (most)."""
        return CapSensor._SENSITIVITY[self._read_register(_CAP1188_SENSITIVTY) >> 4 & 0x07]

    def set_sensitivity(self, value):
        if value not in CapSensor._SENSITIVITY:
            raise ValueError("Sensitivty must be one of: {}".format(CapSensor._SENSITIVITY))
        value = CapSensor._SENSITIVITY.index(value) << 4
        new_setting = self._read_register(_CAP1188_SENSITIVTY) & 0x8F | value
        self._write_register(_CAP1188_SENSITIVTY, new_setting)

    def get_thresholds(self):
        """Touch threshold value for all channels."""
        return self.threshold_values()

    def set_thresholds(self, value):
        value = int(value)
        if not 0 <= value <= 127:
            raise ValueError("Threshold value must be in range 0 to 127.")
        self._write_block(_CAP1188_THESHOLD_1, bytearray((value,)*8))

    def threshold_values(self):
        """Return tuple of touch threshold values for all channels."""
        return tuple(self._read_block(_CAP1188_THESHOLD_1, 8))

    def recalibrate(self):
        """Perform a self recalibration on all the pins."""
        self.recalibrate_pins(0xFF)

    def delta_count(self, pin):
        """Return the 8 bit delta count value for the channel."""
        if pin < 1 or pin > 8:
            raise IndexError('Pin must be a value 1-8.')
        # 8 bit 2's complement
        raw_value = self._read_register(self._CAP1188_DELTA_COUNT[pin-1])
        raw_value = raw_value - 256 if raw_value & 128 else raw_value
        return raw_value

    def recalibrate_pins(self, mask):
        """Recalibrate pins specified by bit mask."""
        self._write_register(_CAP1188_CAL_ACTIVATE, mask)

    def _read_register(self, memaddr):
        """Return 8 bit value of register at address."""
        self.i2c.readfrom_mem_into(self.address, memaddr, self.one_byte_buffer)
        return self.one_byte_buffer[0]

    def _write_register(self, memaddr, value):
        """Write 8 bit value to registter at address."""
        self.one_byte_buffer[0] = value & 0xFF
        self.i2c.writeto_mem(self.address, memaddr, self.one_byte_buffer)

    def _read_block(self, start, length):
        """Return byte array of values from start address to length."""
        raise NotImplementedError

    def _write_block(self, start, data):
        """Write out data beginning at start address."""
        raise NotImplementedError
