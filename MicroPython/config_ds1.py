# Drumpad Config

instrument_type = 'drumstick'

id = 0

threshold = 20
min_strike_scale = -50
max_strike_scale = 28 # Used for velocity calc

# Milliseconds between readings
sample_frequency = 10

# ms for haptic buzz
buzz_ms_min = 75
buzz_ms_max = 100

# GPIO Pin for vibration motor
buzz_pin = 2

# Power to raise jerk to
power = 0.5
use_jerk = True

# Debounce period
debounce_ms = 70

# Acceleromter pins
accel_scl = 4
accel_sda = 15

print_threshold = 200

# Development mode. False means start read loop at boot
dev = False
