from machine import Pin
import led
from led import Led
from button import Button
import time
import confweb
import confman
import fileman
import structures
import netman
import gc

#create buttons 
#buttons = (Button(23), Button(5), Button(23), Button(5), Button(13), Button(12))
#btn_volUp, btn_volDown, btn_1, btn_2, btn_3, btn_4 = buttons
#create leds
#leds = (Led(23), Led(15), Led(4), Led(17), Led(18), Led(5), Led(16), Led(2))
#led_volUp, led_volDown, led_3, led_4, led_5, led_6, led_7 = leds

gc.collect()
CONF = "device.conf"

config = fileman.loadconfig(CONF)


