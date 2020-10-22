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

    def value(self, state=None):
        """
        get or change state of led
        :param state: new state or None
        :return: led state if param state is None
        """
        if not state:
            return not self.__pin.value()
        else:
            self.__pin.value(state)


__blink_config_ms = 0


def blink_config(*leds):
    """
    turn leds on and off nonblocking
    :param leds: leds
    """
    global __blink_config_ms

    if time.ticks_diff(time.ticks_ms(), __blink_config_ms) >= 1000:
        __blink_config_ms = time.ticks_ms()
        state = leds[0].value()
        for l in leds:
            l.value(not state)


__blink_connecting_ms = 0


def blink_connecting(*leds):
    """
    turn leds on and off nonblocking
    :param leds: leds
    """
    global __blink_connecting_ms

    if time.ticks_diff(time.ticks_ms(), __blink_connecting_ms) >= 100:
        __blink_connecting_ms = time.ticks_ms()
        state = leds[0].value()
        for l in leds:
            l.value(not state)


def blink_error(*leds):
    """
    keep led on
    :param leds: leds
    """
    for l in leds: l.on()


def blink_init(*leds, count=3):
    """
    turn leds on and off
    blocking - actively waits
    :param leds: leds
    :param count: number of times to blink
    """
    for c in range(count):
        for l in leds: l.on()
        time.sleep_ms(200)
        for l in leds: l.off()
        time.sleep_ms(200)
