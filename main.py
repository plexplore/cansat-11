from machine import Pin, SPI, ADC
import sdcard
import uos
import logging
import gc
from threading import Thread
import _thread
import time
import json
import random

# CircuitPython 
import board
import busio

# Sensors
import adafruit_bme680

"""
sensors with IDs:
00 - BME680 - Temperature
01 - BME680 - Pressure
02 - BME680 - Humidity
03 - BME680 - Gas

04 - Pico - RAM free
05 - Pico - RAM allocated
06 - Pico - CPU temperature
07 - Pico - uname - sysname
08 - Pico - uname - nodename
09 - Pico - uname - release
10 - Pico - uname - version
11 - Pico - uname - machine

12 - Pico - SD card 1 - mounted
13 - Pico - SD card 2 - mounted

14 - GPS - Latitude
15 - GPS - Longitude
16 - GPS - Altitude
17 - GPS - Time
18 - GPS - Date

19 - MPU9250 - Accelerometer X
20 - MPU9250 - Accelerometer Y
21 - MPU9250 - Accelerometer Z
22 - MPU9250 - Gyroscope X
23 - MPU9250 - Gyroscope Y
24 - MPU9250 - Gyroscope Z
25 - MPU9250 - Magnetometer X
26 - MPU9250 - Magnetometer Y
27 - MPU9250 - Magnetometer Z
28 - MPU9250 - Temperature


"""

DEFAULT_CONF = {"runs":0}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CanSat")

SENSOR_DATA = []

class SensorData:
    def __init__(self, sensor_id:int, time:int, value:str) -> None:
        self.id = sensor_id
        self.time = time
        self.value = value
        
    def csv(self):
        return f"{self.id},{self.time},{self.value}"
    
class Sensor:
    def __init__(self) -> None:
        pass
    
    def get_data(self) -> list[SensorData]:
        return []
    
class BME680(Sensor):
    def __init__(self) -> None:
        self.i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c)
    
    def get_data(self) -> list[SensorData]:
        return [
            SensorData(0, 0, str(self.bme680.temperature)),
            SensorData(1, 0, str(self.bme680.pressure)),
            SensorData(2, 0, str(self.bme680.relative_humidity)),
            SensorData(3, 0, str(self.bme680.gas))
        ]
        

class Pico(Sensor):
    def __init__(self) -> None:
        pass
    
    def ram_stats(self):
        return (gc.mem_free()/1024, gc.mem_alloc()/1024)
    
    def device_info(self):
        return uos.uname()
    
    def cpu_temperature(self):
        adc = ADC(4).read_u16()
        u = (3.3/65536) * adc
        return round(27 - (u - 0.706)/0.001721, 1)

    def get_data(self) -> list[SensorData]:
        ram_free, ram_allocated = self.ram_stats()
        sysname, nodename, release, version, machine = self.device_info()
        t = time.ticks_ms()
        return [
            SensorData(4, t, str(ram_free)),
            SensorData(5, t, str(ram_allocated)),
            SensorData(6, t, str(self.cpu_temperature())),
            SensorData(7, t, sysname),
            SensorData(8, t, nodename),
            SensorData(9, t, release),
            SensorData(10, t, version),
            SensorData(11, t, machine)
        ]
        
        
class SDCard:
    def __init__(self, name:str, spi: SPI, cs: Pin):
        self.name = name
        self.mount_name = self.name[1:] # for a reason I do not understand, when mounting the first character is removed
        self.spi = spi
        self.cs = cs
        self.mounted = False
        
        
    def mount(self) -> bool:
        try:
            self.card = sdcard.SDCard(self.spi, self.cs)
            self.vfs = uos.VfsFat(self.card)
            
            uos.mount(self.vfs, self.name)
            
            self.mounted = True
            return True
        
        except Exception as e:
            logger.error(f"Error mounting {self.name} SD card: {e}")
            return False
        
    
    def write(self, filename:str, text:str) -> bool:
        if self.mounted:
            joined_name = f"/{self.mount_name}/{filename}"
            
            try:
                with open(joined_name, "a") as f:
                    f.write(text)       
                return True
            
            except Exception as e:
                logger.error(f"Error writing to {joined_name}: {e}")
                return False
        return False

class SdCardArray:
    def __init__(self) -> None:
        self.cards = []
        
    def mount_all(self) -> bool:
        for card in self.cards:
            card.mount()
        return True

    def write_all(self, filename:str, text:str) -> bool:
        for card in self.cards:
            card.write(filename, text)
        return True


class IOThread(Thread):
    def __init__(self, lock, conf: dict, cards: SdCardArray, sensor_data: list[SensorData]) -> None:
        super(IOThread, self).__init__()
        self.lock = lock
        self.local_sensor_data = []
        self.sensor_data = sensor_data
        self.conf = conf
        self.cards: SdCardArray = cards
    
    def run(self):
        i = 0
        r = self.conf["runs"]
        while True:
            t = time.ticks_ms()
            with self.lock:
                self.local_sensor_data = self.sensor_data.copy()
                self.sensor_data.clear()
            
            if len(self.local_sensor_data) != 0:
                fcsv = "\n".join([x.csv() for x in self.local_sensor_data]) + "\n"
                self.cards.write_all(f"data-{r}.csv", fcsv)
            
            i += len(self.local_sensor_data)
            dt = (time.ticks_ms() - t)
            if dt !=0:
                print(f"Writing {len(self.local_sensor_data)} took {time.ticks_ms() - t} ms, total: {i}, speed: {len(self.local_sensor_data)/dt*100}")
            
            time.sleep(0.5)
            
    
class CanSat:
    def __init__(self) -> None:
        self.pico = Pico()
        self.sdcard_array = SdCardArray()
        self.sensors = []
        self.sensor_data = []
        self.onboard_led = Pin(25, Pin.OUT)
        self.onboard_led.off()

    def setup(self):
        # Setup SD cards
        self.sdcard_array.cards.append(SDCard("sd1", SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(8)), Pin(9, Pin.OUT)))
        self.sdcard_array.mount_all()
        # conf file
        conf_exists = "conf.json" in uos.listdir("/d1")
        if conf_exists:
            t = time.ticks_ms()
            with open("/d1/conf.json", "r") as f:
                self.conf = json.load(f)
            self.conf["runs"] += 1
            with open("/d1/conf.json", "w") as f:
                json.dump(self.conf, f)
            logger.info(f"Loading config took {time.ticks_ms() - t} ms")
            logger.info(f"Configuration file exists, runs: {self.conf},")
        else:
            with open("/d1/conf.json", "w") as f:
                self.conf = DEFAULT_CONF
                json.dump(self.conf, f)
            logger.info("Created default configuration")
        
        # Setup LoRa
        
        # Setup sensors
        try:
            bme680 = BME680()
            self.sensors.append(bme680)
            del bme680
        except Exception as e:
            logger.error(f"Error initializing BME680: {e}")
                
        self.sensors.append(self.pico)
        
        # Threading
        self.thread_lock = _thread.allocate_lock()
        self.io_thread = IOThread(self.thread_lock, self.conf, self.sdcard_array, self.sensor_data)
        self.io_thread.start()
        
        
        
    def run(self):
        self.setup()
        logger.info("CanSat started")
        
        for i in range(1000):
            with self.thread_lock:
                self.sensor_data.extend([SensorData(0, time.ticks_ms(), str(self.pico.ram_stats()[0]))])
                    
            time.sleep(random.random()/100)
        
        
        time.sleep(1)
        self.onboard_led.on()
        time.sleep(4)
        
cansat = CanSat()
cansat.run()
    