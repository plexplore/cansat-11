from ulora import LoRa, ModemConfig
from machine import SPI, Pin
from time import sleep, time, ticks_ms
#for i in range(10):
#    print("free ", gc.mem_free()/1024)
#    print("alloc ", gc.mem_alloc()/1024)
#    
#    sleep(1)


"""import machine

 
i2c=machine.I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)
 
print('I2C address:')
print(i2c.scan(),' (decimal)')
print(hex(i2c.scan()[3]), ' (hex)')
"""
"""import adafruit_bme680
import busio
import board

i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

print("Temperature: %0.1f C" % bme680.temperature)
print("Gas: %d ohm" % bme680.gas)
print("Humidity: %0.1f %%" % bme680.humidity)
print("Pressure: %0.3f hPa" % bme680.pressure)"""

import board
import busio

class SensorData:
    def __init__(self, sensor_id:int, time:int, value:str) -> None:
        self.id = sensor_id
        self.time = time
        self.value = value
        
    def csv(self):
        return f"{self.id},{self.time},{self.value};"
    
class Sensor:
    def __init__(self) -> None:
        pass
    
    def get_data(self) -> list[SensorData]:
        return []

from machine import I2C as machine_I2C
from machine import Pin as machine_Pin
import mpu9250
class MPU9250():
    def __init__(self) -> None:
        self.mpu9250 = mpu9250.MPU9250(machine_I2C(0,scl=machine_Pin(21), sda=machine_Pin(20)))
    def get_data(self) -> list[SensorData]:
        t = time.ticks_ms()
        return [
            SensorData(19, t, str(self.mpu9250.acceleration)),
        ]

mpu = MPU9250()
print(mpu.get_data())

#print("Temperature: %0.1f C" % bme680.temperature)
"""
RFM95_RST = 4
RFM95_SPIBUS = (0, 2, 3, 0)
RFM95_CS = 1
RFM95_INT = 6
RF95_FREQ = 868.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2

lora = LoRa(
    RFM95_SPIBUS,
    RFM95_INT,
    CLIENT_ADDRESS,
    RFM95_CS,
    reset_pin=RFM95_RST
)

t = ticks_ms()
lora.send_to_wait("Hello World!", SERVER_ADDRESS)

print("Time to send: ", ticks_ms() - t)
print("Sent Hello World!")

sleep(1)
"""
""""
from machine import SPI, Pin
import sdcard
import uos
import json
import time


#sd = sdcard.SDCard(SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(8)), Pin(9, Pin.OUT))
sd = sdcard.SDCard(SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12)), Pin(13, Pin.OUT))
vfs=uos.VfsFat(sd)
#vfs2=uos.VfsFat(sd2)
uos.mount(vfs, "sd1")
#uos.mount(vfs2, "sd2")

with open("/d1/test.txt", "w") as f:
    f.write("hi1234")

#with open("/d2/test.txt", "w") as f:
#    f.write("hi5678")

with open("/d1/test.txt", "r") as f:
    conf = f.read()

#with open("/d2/test.txt", "r") as f:
#    conf2 = f.read()class NitrogenDioxideSensor(Sensor)

print(conf)
#print(conf2)
print(uos.listdir("/d1"))
#print(uos.listdir("/d2"))"""