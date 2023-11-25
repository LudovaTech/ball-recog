

import sensor
import time
import machine
import pyb

#P4 (TX)
#P5 (RX)

uart = pyb.UART(3, 115200, timeout_char = 1000)
uart.write("Hello World\n")

while True:
    pass
