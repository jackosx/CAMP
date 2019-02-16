class accelerometer:

    _BUFFER = bytearray(6)

    def __init__(self, scl=22, sda=21):
        self.i2c = machine.I2C(machine.Pin(scl), machine.Pin(sda))
        self.address = i2c.scan()[0]
        print("Reset and wait for chip to be ready.")
        self.write_u8(_MMA8451_REG_CTRL_REG2, 0x40)
        while ((read_u8(_MMA8451_REG_CTRL_REG2) & 0x40) > 0):
            print("\t WAITING")
        print("Enable 4g mode")
        self.write_u8(_MMA8451_REG_XYZ_DATA_CFG, RANGE_4G)
        print("High res mode")
        self.write_u8(_MMA8451_REG_CTRL_REG2, 0x02)
        print("DRDY on INT1")
        self.write_u8(_MMA8451_REG_CTRL_REG4, 0x01)
        self.write_u8(_MMA8451_REG_CTRL_REG5, 0x01)
        print("Turn on orientation config")
        self.write_u8(_MMA8451_REG_PL_CFG, 0x40)
        print("Activate at max rate, low noise mode")
        self.write_u8(_MMA8451_REG_CTRL_REG1, 0x01 | 0x04)


    def read_u8(self, memaddr):
        temp_buffer = bytearray(1)
        self.i2c.readfrom_mem_into(self.address, memaddr, temp_buf)
        return temp_buf[0]


    def write_u8(self, memaddr, val):
        short_buf = bytearray(1)
        short_buf[0] = val & 0xFF
        self.i2c.writeto_mem(self.address, memaddr, short_buf)

    def get_accel(self):
        self.i2c.readfrom_mem_into(self.address, _MMA8451_REG_OUT_X_MSB, _BUFFER)
        x, y, z = struct.unpack('>hhh', _BUFFER)
        x >>= 2
        y >>= 2
        z >>= 2
        x=x/2048.0*_SENSORS_GRAVITY_EARTH
        y=y/2048.0*_SENSORS_GRAVITY_EARTH
        z=z/2048.0*_SENSORS_GRAVITY_EARTH
        print("{:4.4f}, {:4.4f}, {:4.4f}".format(x, y, z))
        return (x, y, z)

    def get_orient(self):
        orient = self.read_u8(_MMA8451_REG_PL_STATUS) & 0x07
        print("Orientation: ", orient)
        return orient

    def stream_vals(self, time_ms=10000, read_a=True, read_o=True):
        num_iter = time_ms / 50
        for i in range(0, num_iter):
            if read_a:
                get_accel()
            if read_o:
                get_orient()
