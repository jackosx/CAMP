import machine
import time
import struct

# Internal constants:
_MMA8451_DEFAULT_ADDRESS   = const(0x1D)
_MMA8451_REG_OUT_X_MSB     = const(0x01)
_MMA8451_REG_SYSMOD        = const(0x0B)
_MMA8451_REG_WHOAMI        = const(0x0D)
_MMA8451_REG_XYZ_DATA_CFG  = const(0x0E)
_MMA8451_REG_PL_STATUS     = const(0x10)
_MMA8451_REG_PL_CFG        = const(0x11)
_MMA8451_REG_CTRL_REG1     = const(0x2A)
_MMA8451_REG_CTRL_REG2     = const(0x2B)
_MMA8451_REG_CTRL_REG4     = const(0x2D)
_MMA8451_REG_CTRL_REG5     = const(0x2E)
_MMA8451_DATARATE_MASK     = const(0b111)
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
