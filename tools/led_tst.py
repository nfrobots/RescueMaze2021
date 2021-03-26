from adafruit_ws2801 import WS2801
import board
import time

def color_wheel(n):
    n %= 255
    if n < 85:
        modifier = n * 3
        return (255 - modifier, modifier, 0)
    if n < 170:
        modifier = (n - 85) * 3
        return (0, 255 - modifier, modifier)
    else:
        modifier = (n - 170) * 3
        return (modifier, 0, 255 - modifier)


NUM_LEDS = 12

leds = WS2801(board.SCLK, board.MOSI, NUM_LEDS*3, brightness=0.1)

def startup():
    for i in range(NUM_LEDS):
        leds.fill((0, 0, 0))
        leds[i] = (255, 0, 40)
        time.sleep(0.6)

    leds.fill((0, 255, 0))
    time.sleep(1)
    leds.fill((0, 0, 0))

startup()