from machine import Pin
import led
from led import Led
from button import Button
import time
import webserver
import config
import structures
import netconnect
import gc
import network
from heos import *

# create buttons
buttons = (Button(34), Button(35), Button(21), Button(39), Button(33), Button(36))
btn_1, btn_2, btn_3, btn_4, btn_5, btn_6 = buttons
# create leds
leds = (Led(2), Led(23), Led(5), Led(4), Led(18), Led(17), Led(16), Led(15))
led_1, led_2, led_3, led_4, led_5, led_6, led_7, led_8 = leds

device_config = config.loadconfig()  # load device config from memory
heos_discovery = DiscoveryService()
heos_device = Heos(device_config.HEOS)

def config_mode(): #
    led.blink_init(*leds, count=5) # signal entering config
    netconnect.startAP(config.AP)
    try:
        webserver.start()
        while True:
            webserver.listen()
            led.blink_config(*leds)
    except Exception as e:
        webserver.stop()
        raise e


def heos_ondiscover(ip): # stop discovery and start heos connection
    global heos_device
    global heos_discovery
    heos_discovery.stop()
    heos_device.start(ip)


def heos_ondisconnect(): # clear previous heos connection
    global heos_device
    heos_device.stop()


def sw1_shortpress(): # play state - play
    if heos_device.getpid():
        heos_device.send("player/set_play_state", {"pid":heos_device.getpid(),"state":"play"})
def sw1_longpress(): # select input
    if heos_device.getpid():
        heos_device.send("browse/play_input", {"pid":heos_device.getpid(), "input":"inputs/line_in_1"} )

def sw2_shortpress(): # play state - stop
    if heos_device.getpid():
        heos_device.send("player/set_play_state", {"pid":heos_device.getpid(),"state":"stop"})
def sw2_longpress(): # toggle mute
    if heos_device.getpid():
        heos_device.send("player/toggle_mute", {"pid":heos_device.getpid()})

def sw3_shortpress(): # fav 1
    if heos_device.getpid():
        heos_device.send("browse/play_preset", {"pid":heos_device.getpid(),"preset":"1"})
def sw3_longpress(): # fav 3
    if heos_device.getpid():
        heos_device.send("browse/play_preset", {"pid":heos_device.getpid(),"preset":"3"})

def sw4_shortpress(): # fav 2
    if heos_device.getpid():
        heos_device.send("browse/play_preset", {"pid":heos_device.getpid(),"preset":"2"})
def sw4_longpress(): # fav 4
    if heos_device.getpid():
        heos_device.send("browse/play_preset", {"pid":heos_device.getpid(),"preset":"4"})

def sw5_shortpress(): # vol up
    if heos_device.getpid():
        heos_device.send("player/volume_up", {"pid":heos_device.getpid(), "step":"3"})
def sw5_onhold(): # continuous vol up
    if heos_device.getpid():
        heos_device.send("player/volume_up", {"pid":heos_device.getpid(), "step":"5"})

def sw6_shortpress(): # vol down
    if heos_device.getpid():
        heos_device.send("player/volume_down", {"pid":heos_device.getpid(),"step":"3"})
def sw6_onhold():  # continuous vol down
    if heos_device.getpid():
        heos_device.send("player/volume_down", {"pid":heos_device.getpid(),"step":"5"})


button_shortpress_cb = (sw1_shortpress, sw2_shortpress, sw3_shortpress, sw4_shortpress, sw5_shortpress, sw6_shortpress)
button_longpress_cb = (sw1_longpress, sw2_longpress, sw3_longpress, sw4_longpress, None, None)
button_hold_cb = (None, None, None, None, sw5_onhold, sw6_onhold)

def normal_mode():
    led.blink_init(*leds, count=2)
    # init button callbacks
    for i, b in enumerate(buttons):  # button handler
        b.onpress(lambda i=i: leds[i].on())
        b.onrelease(lambda i=i: leds[i].off())
        if button_shortpress_cb[i] : b.onpress(button_shortpress_cb[i])
        if button_longpress_cb[i] : b.onlongpress(button_longpress_cb[i])
        if button_hold_cb[i] : b.onhold(button_hold_cb[i])
    # init heos callbacks
    heos_discovery.ondiscover(heos_ondiscover)
    heos_device.ondisconnect(heos_ondisconnect)

    millis_lastreconnect = 0
    while True:
        if not netconnect.isconnected():  # not connected, try reconnect
            if not (netconnect.statusWLAN() == network.STAT_CONNECTING or netconnect.statusETH() == network.STAT_CONNECTING) and time.ticks_diff(
                    time.ticks_ms(), millis_lastreconnect) > 2000:  # try connecting after the interval
                millis_lastreconnect = time.ticks_ms()
                netconnect.connect(config.WLAN, config.ETH)
            if netconnect.statusWLAN() == network.STAT_CONNECTING or netconnect.statusETH() == network.STAT_CONNECTING:
                led.blink_connecting(led_7)
        else: # connected
            if not led_7.value(): # signal stable network connection
                led_7.on()

            if not heos_device.getconnection(): # not connected nor connecting to heos
                heos_discovery.discover() # discover heos devices on network
            else: # heos connected or connecting
                heos_device.run()

            for b in buttons: # update button states
                b.update()

            if not heos_device.issigned(): # signal signed status of heos device
                led.blink_connecting(led_8)
            elif not led_8.value():
                led_8.on()


# startup code
gc.collect()  # collect previous garbage
if btn_1.value():  # button pressed on power up
    config_mode()  # enter configuration mode
else:
    normal_mode()  # enter normal mode
