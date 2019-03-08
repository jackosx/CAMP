import machine
import time
import struct

class Accelerometer:

    # Internal constants:
    _MMA8451_DEFAULT_ADDRESS   = 0x1D
    _MMA8451_REG_OUT_X_MSB     = 0x01
    _MMA8451_REG_SYSMOD        = 0x0B
    _MMA8451_REG_WHOAMI        = 0x0D
    _MMA8451_REG_XYZ_DATA_CFG  = 0x0E
    _MMA8451_REG_PL_STATUS     = 0x10
    _MMA8451_REG_PL_CFG        = 0x11
    _MMA8451_REG_CTRL_REG1     = 0x2A
    _MMA8451_REG_CTRL_REG2     = 0x2B
    _MMA8451_REG_CTRL_REG4     = 0x2D
    _MMA8451_REG_CTRL_REG5     = 0x2E
    _MMA8451_DATARATE_MASK     = 0b111
    _SENSORS_GRAVITY_EARTH     = 9.80665

    # External user-facing constants:
    PL_PUF           = 0      # Portrait, up, front
    PL_PUB           = 1      # Portrait, up, back
    PL_PDF           = 2      # Portrait, down, front
    PL_PDB           = 3      # Portrait, down, back
    PL_LRF           = 4      # Landscape, right, front
    PL_LRB           = 5      # Landscape, right, back
    PL_LLF           = 6      # Landscape, left, front
    PL_LLB           = 7      # Landscape, left, back
    RANGE_8G         = 0b10   # +/- 8g
    RANGE_4G         = 0b01   # +/- 4g (default value)
    RANGE_2G         = 0b00   # +/- 2g
    DATARATE_800HZ   = 0b000  #  800Hz
    DATARATE_400HZ   = 0b001  #  400Hz
    DATARATE_200HZ   = 0b010  #  200Hz
    DATARATE_100HZ   = 0b011  #  100Hz
    DATARATE_50HZ    = 0b100  #   50Hz
    DATARATE_12_5HZ  = 0b101  # 12.5Hz
    DATARATE_6_25HZ  = 0b110  # 6.25Hz
    DATARATE_1_56HZ  = 0b111  # 1.56Hz



    def __init__(self, scl=21, sda=22):
        self.six_byte_buffer = bytearray(6)
        self.one_byte_buffer = bytearray(1)
        self.i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
        self.address = self.i2c.scan()[0]
        print("Reset and wait for chip to be ready.")
        self.write_u8(Accelerometer._MMA8451_REG_CTRL_REG2, 0x40)
        while ((self.read_u8(Accelerometer._MMA8451_REG_CTRL_REG2) & 0x40) > 0):
            print("\t WAITING")
        print("Enable 8g mode")
        self.write_u8(Accelerometer._MMA8451_REG_XYZ_DATA_CFG, Accelerometer.RANGE_8G)
        print("High res mode")
        self.write_u8(Accelerometer._MMA8451_REG_CTRL_REG2, 0x02)
        print("DRDY on INT1")
        self.write_u8(Accelerometer._MMA8451_REG_CTRL_REG4, 0x01)
        self.write_u8(Accelerometer._MMA8451_REG_CTRL_REG5, 0x01)
        print("Turn on orientation config")
        self.write_u8(Accelerometer._MMA8451_REG_PL_CFG, 0x40)
        print("Activate at max rate, low noise mode")
        self.write_u8(Accelerometer._MMA8451_REG_CTRL_REG1, 0x01 | 0x04)


    def read_u8(self, memaddr):
        self.i2c.readfrom_mem_into(self.address, memaddr, self.one_byte_buffer)
        return self.one_byte_buffer[0]


    def write_u8(self, memaddr, val):
        self.one_byte_buffer[0] = val & 0xFF
        self.i2c.writeto_mem(self.address, memaddr, self.one_byte_buffer)

    def get_accel(self):
        self.i2c.readfrom_mem_into(self.address, Accelerometer._MMA8451_REG_OUT_X_MSB, self.six_byte_buffer)
        x, y, z = struct.unpack('>hhh', self.six_byte_buffer)
        x >>= 2
        y >>= 2
        z >>= 2
        x=x/1024.0*Accelerometer._SENSORS_GRAVITY_EARTH
        y=y/1024.0*Accelerometer._SENSORS_GRAVITY_EARTH
        z=z/1024.0*Accelerometer._SENSORS_GRAVITY_EARTH
        # print("{:4.4f}, {:4.4f}, {:4.4f}".format(x, y, z))
        return (x, y, z)

    def get_orient(self):
        orient = self.read_u8(Accelerometer._MMA8451_REG_PL_STATUS) & 0x07
        # print("Orientation: ", orient)
        return orient
