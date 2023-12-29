

import sensor
import time
import machine
import pyb
from random import randrange

#P4 (TX)
#P5 (RX)

uart = pyb.UART(3, 115200)

def r() {
    return round(randrange(0, 150), 5)
}

while True:
   uart.write(
   f"b{r()}, {r()}m{r()}, {r()}p{r()}, {r()}"
)
