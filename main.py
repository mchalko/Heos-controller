from machine import Pin
import led
from led import Led
from button import Button
import time
import webloader
import webserver
import config
import structures
import netconnect
import gc
import network

CONF_FILE = "device.conf"
#create buttons
buttons = (Button(34), Button(35), Button(21), Button(39), Button(33), Button(36))
btn_1, btn_2, btn_3, btn_4, btn_5, btn_6 = buttons
#create leds
leds = (Led(2), Led(23), Led(5), Led(4), Led(18), Led(17), Led(16), Led(15))
led_1, led_2, led_3, led_4, led_5, led_6, led_7, led_8 = leds

gc.collect()
config = config.loadconfig(CONF_FILE)
if not config: # use default config if configuration file is corrupted
    config = structures.Configuration()


if btn_1.value(): # button pressed on power up
    # enter configuration mode
    netconnect.startAP(config.AP)
    try:
        webserver.start(CONF_FILE)
        led.blink_init(*leds, count=5)
        while True:
            webserver.listen()
            led.blink_config(*leds)
    except Exception as e:
        webserver.stop()
        raise e
else:
    # enter normal mode
    led.blink_init(*leds, count=2)
    for i,b in enumerate(buttons):
        b.onpress(lambda i=i:leds[i].on())
        b.onrelease(lambda i=i:leds[i].off())

    _millis_lastreconnect = 0
    while True:
        if not netconnect.isconnected(): # not connected, try reconnect
            if not(netconnect.statusWLAN() == network.STAT_CONNECTING or netconnect.statusETH() == network.STAT_CONNECTING) and time.ticks_diff(time.ticks_ms(), _millis_lastreconnect) > 2000:  # try connecting after the interval
                _millis_lastreconnect = time.ticks_ms()
                netconnect.connect(config.WLAN, config.ETH)
            if netconnect.statusWLAN() == network.STAT_CONNECTING or netconnect.statusETH() == network.STAT_CONNECTING:
                led.blink_connecting(led_7)
        else:
            if not led_7.value() : led_7.on()

        for b in buttons: b.update()



