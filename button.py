import time

SHORT_PRESS_MS = 40  # minimal duration of press, anything less is noise
LONG_PRESS_MS = 750  # threshold for differentiating long button press
HOLD_INVOKE_INT_MS = 400  # interval for periodical ivoking of hold callback


class Button(object):
    """
    Button object with helper functions
    """
    def __init__(self, pin):
        from machine import Pin
        import time

        # initial state of object variables
        self.pin = pin
        self.pressed = False
        self.__onPress = []
        self.__onShortPress = []
        self.__onLongPress = []
        self.__onHold = []
        self.__onRelease = []
        self.__startTime = None
        self.__hold_ms = 0
        self.__hold = False
        # create Pin for the button
        self.__pin = Pin(pin, Pin.IN, Pin.PULL_UP)  # init Pin
        self.__pin.irq((lambda p: self.__pressed()), trigger=Pin.IRQ_FALLING)  # init interrupt

    def __pressed(self):  # onPress interrupt callback
        self.__startTime = time.ticks_ms()

    def __released(self):  # onRelease function
        self.pressed = False
        self.__hold = False
        self.__startTime = None

    @staticmethod
    def __invoke(methods): # invokes callback
        for m in methods:
            m()

    def update(self):
        """
        Update button states and invoke callbacks
        For proper functionality of the button this method needs to be periodically called.
        """
        if self.__startTime:  # button has been pressed
            if self.__hold:  # if hold callback exists, call it periodically while button is being held
                if self.__onHold and time.ticks_diff(time.ticks_ms(), self.__hold_ms) >= HOLD_INVOKE_INT_MS:
                    self.__hold_ms = time.ticks_ms()
                    Button.__invoke(self.__onHold)
            elif not self.pressed and time.ticks_diff(time.ticks_ms(),
                                                      self.__startTime) >= SHORT_PRESS_MS:  # button was just pressed
                self.pressed = True
                Button.__invoke(self.__onPress) # call generic press callbacks
            elif time.ticks_diff(time.ticks_ms(), self.__startTime) >= LONG_PRESS_MS:  # button is being pressed for longer
                self.__hold = True
                self.__hold_ms = time.ticks_ms()
                Button.__invoke(self.__onLongPress) # long press callbacks
            if not self.value():  # button has been released
                if self.pressed:  # button was pressed for long enough
                    if not self.__hold: # not a long press
                        Button.__invoke(self.__onShortPress)
                    Button.__invoke(self.__onRelease) # call release callbacks
                self.__released() # reset vars

    def value(self):
        """
        get value of the button
        :return: value
        """
        return self.__pin.value() == 0

    # callback takes no parameter.
    def onpress(self, callback=None):  # general button press
        """
        adds callback to a list of callbacks invoked after given event occurs
        If called without parameters or callback is None, removes all callbacks instead
        :param callback: method with no parameter
        """
        if callback is None:
            self.__onPress.clear()
        else:
            self.__onPress.append(callback)

    def onshortpress(self, callback=None):  # short button press
        """
        adds callback to a list of callbacks invoked after given event occurs
        If called without parameters or callback is None, removes all callbacks instead
        :param callback: method with no parameter
        """
        if callback is None:
            self.__onShortPress.clear()
        else:
            self.__onShortPress.append(callback)

    def onlongpress(self, callback=None):  # long button press
        """
        adds callback to a list of callbacks invoked after given event occurs
        If called without parameters or callback is None, removes all callbacks instead
        :param callback: method with no parameter
        """
        if callback is None:
            self.__onLongPress.clear()
        else:
            self.__onLongPress.append(callback)

    def onhold(self, callback=None):  # button being pressed down
        """
        adds callback to a list of callbacks invoked after given event occurs
        If called without parameters or callback is None, removes all callbacks instead
        :param callback: method with no parameter
        """
        if callback is None:
            self.__onHold.clear()
        else:
            self.__onHold.append(callback)

    def onrelease(self, callback=None):  # button released
        """
        adds callback to a list of callbacks invoked after given event occurs
        If called without parameters or callback is None, removes all callbacks instead
        :param callback: method with no parameter
        """
        if callback is None:
            self.__onRelease.clear()
        else:
            self.__onRelease.append(callback)
