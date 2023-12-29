from random import randint, uniform

def r():
    return round(uniform(0, 150), randint(0, 5))


def send_data(uart, bx, by):
    uart.write(
    f"b{bx},{by}m{r()},{r()}p{r()},{r()}"
    )
