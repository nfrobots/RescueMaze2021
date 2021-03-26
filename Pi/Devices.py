import gpiozero
from adafruit_ws2801 import WS2801
import board

button_left = gpiozero.Button(26)
button_right = gpiozero.Button(19)

NUM_LEDS = 12

leds = WS2801(board.SCLK, board.MOSI, NUM_LEDS, brightness=1)