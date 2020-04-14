import gc
import webrepl
import network
from machine import UART
import machine
import os
import time

uart = UART(0, baudrate=115200)
os.dupterm(uart)

webrepl.start()
gc.collect()

network.WLAN(network.AP_IF).active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('network', 'password')

count = 0
while not sta_if.isconnected():
    time.sleep_ms(1)
    count += 1
    if count == 5000:
        print('Not connected')
        break
print('Config: ', sta_if.ifconfig())
