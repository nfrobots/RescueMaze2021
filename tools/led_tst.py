from adafruit_ws2801 import WS2801
import board
import time

leds = WS2801(board.SCLK, board.MOSI, 12*3, brightness=0.1)
leds.fill(0x000000)
time.sleep(0.4)
leds.fill(0xff0000)
time.sleep(0.4)
leds.fill(0x000000)
time.sleep(0.4)
leds.fill(0xff0000)
time.sleep(0.4)
leds.fill(0x000000)
time.sleep(0.4)
leds.fill(0xff0000)
time.sleep(0.4)
leds.fill(0x0000ff)
time.sleep(0.4)
leds.fill(0x00ff00)
