from machine import SPI, Pin
import sdcard
import uos
import json
import time


sd = sdcard.SDCard(SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(8)), Pin(9, Pin.OUT))
vfs=uos.VfsFat(sd)
uos.mount(vfs, "sd1")

with open("/d1/test.txt", "w") as f:
    f.write("hi1234")

with open("/d1/test.txt", "r") as f:
    conf = f.read()
    
print(conf)
print(uos.listdir("/d1"))