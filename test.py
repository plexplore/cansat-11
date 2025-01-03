from ulora import LoRa, ModemConfig
from machine import SPI, Pin
from time import sleep, time, ticks_ms


RFM95_RST = 27
RFM95_SPIBUS = (0, 2, 3, 0)
RFM95_CS = 1
RFM95_INT = 28
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


"""from machine import SPI, Pin
import sdcard
import uos
import json
import time


sd = sdcard.SDCard(SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(8)), Pin(9, Pin.OUT))
sd2 = sdcard.SDCard(SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12)), Pin(13, Pin.OUT))
vfs=uos.VfsFat(sd)
vfs2=uos.VfsFat(sd2)
uos.mount(vfs, "sd1")
uos.mount(vfs2, "sd2")

with open("/d1/test.txt", "w") as f:
    f.write("hi1234")

with open("/d2/test.txt", "w") as f:
    f.write("hi5678")

with open("/d1/test.txt", "r") as f:
    conf = f.read()

with open("/d2/test.txt", "r") as f:
    conf2 = f.read()

print(conf)
print(conf2)
print(uos.listdir("/d1"))
print(uos.listdir("/d2"))"""