from machine import Pin, SPI
import sdcard
import uos
import time
import gc

sd1 = sdcard.SDCard(SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12)), Pin(13, Pin.OUT))
vfs1 = uos.VfsFat(sd1)
uos.mount(vfs1, '/sd1')

print(uos.listdir('/'))

t_start = time.ticks_ms()
with open("/sd1/test.txt", "w") as f:
    f.write("")
    
print("Write time:", time.ticks_ms() - t_start)
print(gc.mem_free()/1024, "KB free")
print(gc.mem_alloc()/1024, "KB allocated")