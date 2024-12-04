import time
import struct
import machine

# MPU-9250 I2C address and registers
MPU9250_ADDR = 0x68  # Default I2C address
MAGNETOMETER_ADDR = 0x0C  # Magnetometer address (used in I2C read/write)

# MPU-9250 register addresses
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
ACCEL_CONFIG = 0x1C
GYRO_CONFIG = 0x1B
MAGNETOMETER_CTRL = 0x0A
MAGNETOMETER_DATA = 0x03

# Scale factors for converting raw data
ACCEL_SCALE = 16384  # for ±2g accelerometer sensitivity
GYRO_SCALE = 131  # for ±250°/s gyroscope sensitivity
MAG_SCALE = 0.15  # for magnetometer (uT per LSB, scaled after calibration)

class MPU9250:
    def __init__(self, i2c, address=MPU9250_ADDR):
        """Initialize the MPU9250 sensor."""
        self.i2c = i2c
        self.address = address
        self.initialize()

    def initialize(self):
        """Wake up the MPU9250 and configure it."""
        self._write_byte(PWR_MGMT_1, 0x00)  # Wake up the sensor
        time.sleep(0.1)

        # Configure accelerometer: ±2g range (default)
        self._write_byte(ACCEL_CONFIG, 0x00)

        # Configure gyroscope: ±250°/s range (default)
        self._write_byte(GYRO_CONFIG, 0x00)

        # Configure magnetometer (continuous measurement mode)
        self._write_byte(MAGNETOMETER_CTRL, 0x01)

    def _write_byte(self, reg, value):
        """Write a single byte to a specific register."""
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read_bytes(self, reg, length):
        """Read multiple bytes from a specific register."""
        return self.i2c.readfrom_mem(self.address, reg, length)

    def read_accelerometer(self):
        """Read accelerometer data (X, Y, Z)."""
        data = self._read_bytes(ACCEL_XOUT_H, 6)
        ax, ay, az = struct.unpack('>hhh', bytes(data))
        return ax / ACCEL_SCALE, ay / ACCEL_SCALE, az / ACCEL_SCALE  # Convert to g

    def read_gyroscope(self):
        """Read gyroscope data (X, Y, Z)."""
        data = self._read_bytes(GYRO_XOUT_H, 6)
        gx, gy, gz = struct.unpack('>hhh', bytes(data))
        return gx / GYRO_SCALE, gy / GYRO_SCALE, gz / GYRO_SCALE  # Convert to °/s

    def read_magnetometer(self):
        """Read magnetometer data (X, Y, Z)."""
        data = self._read_bytes(MAGNETOMETER_DATA, 6)
        mx, my, mz = struct.unpack('>hhh', bytes(data))
        return mx * MAG_SCALE, my * MAG_SCALE, mz * MAG_SCALE  # Convert to µT

    def read_all(self):
        """Read all sensor values (accelerometer, gyroscope, magnetometer)."""
        accel = self.read_accelerometer()
        gyro = self.read_gyroscope()
        mag = self.read_magnetometer()
        return accel, gyro, mag