import time

SHORT_PRESS_MS = 40  # minimal duration of press, anything less is noise
LONG_PRESS_MS = 750  # threshold for differentiating long button press
HOLD_INVOKE_INT_MS = 400  # interval for periodical ivoking of hold callback


class Button(object):

    def __init__(self, pin):
        from machine import Pin
        import time

        # initial state of class variables
        self.pin = pin
        self.pressed = False

        self.__onPress = None
        self.__onShortPress = None
        self.__onLongPress = None
        self.__onHold = None
        self.__onRelease = None
        self.__startTime = None
        self.__hold_ms = 0
        self.__hold = False

        self.__pin = Pin(pin, Pin.IN, Pin.PULL_UP)  # init Pin
        self.__pin.irq((lambda p: self.__pressed()), trigger=Pin.IRQ_FALLING)  # create interrupts for button

    def __pressed(self):  # onPress interrupt callback
        self.__startTime = time.ticks_ms()

    def __released(self):  # onRelease function
        self.pressed = False
        self.__hold = False
        self.__startTime = None

    def update(self):  # call periodically in a loop
        if self.__startTime:  # button has been pressed
            if self.__hold:  # if hold callback exists, call ite periodically while button is being held
                if self.__onHold and time.ticks_diff(time.ticks_ms(), self.__hold_ms) >= HOLD_INVOKE_INT_MS:
                    self.__hold_ms = time.ticks_ms()
                    self.__onHold()
            elif not self.pressed and time.ticks_diff(time.ticks_ms(),
                                                      self.__startTime) >= SHORT_PRESS_MS:  # button is pressed
                self.pressed = True
                if self.__onPress:  # generic press callback
                    self.__onPress()
            elif time.ticks_diff(time.ticks_ms(), self.__startTime) >= LONG_PRESS_MS:  # onLongPress
                self.__hold = True
                self.__hold_ms = time.ticks_ms()
                if self.__onLongPress:  # long press callback
                    self.__onLongPress()
            if not self.value():  # button has been released
                if self.pressed:  # button was pressed for long enough
                    if not self.__hold and self.__onShortPress: # not a long press
                            self.__onShortPress()
                    if self.__onRelease:  # call release callback
                        self.__onRelease()
                self.__released()

    def value(self):
        return self.__pin.value() == 0

    # callback takes no parameter.
    def onpress(self, callback=None):  # general button press
        self.__onPress = callback

    def onshortpress(self, callback=None):  # short button press
        self.__onShortPress = callback

    def onlongpress(self, callback=None):  # long button press
        self.__onLongPress = callback

    def onhold(self, callback=None):  # button being pressed down
        self.__onHold = callback

    def onrelease(self, callback=None):  # button released
        self.__onRelease = callback    
