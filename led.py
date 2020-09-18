import time


class Led(object):
    def __init__(self, pin):
        from machine import Pin

        self.__pin = Pin(pin, Pin.OUT, value=1)  # init superclass Pin
        # initial state of class variables
        self.pin = pin

    def on(self):
        self.__pin.value(0)

    def off(self):
        self.__pin.value(1)

    def value(self):
        return not self.__pin.value()


__blink_config_ms = 0


def blink_config(leds):
    global __blink_config_ms

    if time.ticks_diff(time.ticks_ms(), __blink_config_ms) >= 200:
        __blink_config_ms = time.ticks_ms()
        state = leds[0].value()
        for l in leds:
            l.value(not state)


__blink_connecting_ms = 0
__blink_connecting_led = 0


def blink_connecting(leds):
    global __blink_connecting_ms
    global __blink_connecting_led

    if time.ticks_diff(time.ticks_ms(), __blink_connecting_ms) >= 200:
        __blink_connecting_ms = time.ticks_ms()
        if leds[__blink_connecting_led].value():
            leds[__blink_connecting_led].off()
        else:
            leds[__blink_connecting_led].on()
            __blink_connecting_led += 1
            if __blink_connecting_led == len(leds):
                __blink_connecting_led = 0


def blink_error(leds):
    for l in leds:
        l.on()

