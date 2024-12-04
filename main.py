from machine import Pin, SPI, ADC
import sdcard
import uos
import logging
import gc
import _thread

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

logger = logging.getLogger("CanSat")

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
    
    def setup(self):
        pass
    
    def get_data(self) -> list[SensorData]:
        return []

class IOThread:
    def __init__(self, lock) -> None:
        self.lock = lock
    
    def run(self):
        pass
    
    def start(self):
        _thread.start_new_thread(self.run, ())

class Pico:
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

class SDCard:
    def __init__(self, name:str, spi: SPI, cs: Pin):
        self.name = name
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
            joined_name = f"/{self.name}/{filename}"
            
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
    
class CanSat:
    def __init__(self) -> None:
        self.pico = Pico()
        self.sdcard_array = SdCardArray()

    def setup(self):
        # Setup SD cards
        self.sdcard_array.cards.append(SDCard("sd1", SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12)), Pin(13, Pin.OUT)))
        self.sdcard_array.mount_all()
        
        self.thread_lock = _thread.allocate_lock()
        self.io_thread = IOThread(self.thread_lock)
        
        
        
    def run(self):
        self.setup()