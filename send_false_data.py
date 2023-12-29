

import sensor
import time
import machine
import pyb
from random import randint, uniform

#P4 (TX)
#P5 (RX)

uart = pyb.UART(3, 115200)

def r():
    return round(uniform(0, 150), randint(0, 5))

while True:
   uart.write(
   f"b{r()},{r()}m{r()},{r()}p{r()},{r()}"
)
