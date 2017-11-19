from max7219.led import matrix
import max7219.font as fonts
from datetime import datetime
import time
import threading


class display(matrix):
    """
    Custom matrix for showing alarmclock info
    """

    def __init__(self, cascaded=4, spi_bus=0, spi_device=0, vertical=False):
        super().__init__(cascaded, spi_bus, spi_device, vertical)
        self.orientation(90)
        self.brightness(1)
        self._alarms = [(False, [7, 3, 1]), (False, [224, 192, 128])]
        self._clockEvent = threading.Event()
        self.start_clock()

    def stop_clock(self):
        self._clockEvent.clear()
        self._deamon.join()

    def start_clock(self):
        self._clockEvent.set()
        self._deamon = threading.Thread(name='clock', target=self.__render_time,
                                        args=(self._clockEvent, fonts.SINCLAIR_FONT))
        self._deamon.daemon = True
        self._deamon.start()

    def toogle_alarm(self, number):
        self._alarms[number - 1] = (not self._alarms[number - 1][0], self._alarms[number - 1][1])

    def show_custom_message(self, text):
        self.stop_clock()
        self.show_message(text)
        self.start_clock()

    def __render_time(self, event, font=fonts.CP437_FONT):
        while event.is_set():
            naa = datetime.now().strftime("%k:%M")
            self.__show_time_and_alarms(naa, fonts.proportional(font))
            time.sleep(1)

    def __show_time_and_alarms(self, text, font=fonts.proportional(fonts.SINCLAIR_FONT)):
        """
        Shows time and alarms status
        """
        display_length = self.NUM_DIGITS * self._cascaded
        src = [c for ascii_code in text for c in font[ord(ascii_code)]]
        del src[-1]  # remove whitespace after last char
        left_margin = display_length - len(src)

        alarm_sign = self.__alarm_state()
        src = alarm_sign + src
        for i in range(left_margin - len(alarm_sign)):
            src.insert(len(alarm_sign), 0)

        # Reset the buffer so no traces of the previous message are left
        self._buffer = [0] * display_length

        for pos, value in enumerate(src):
            self._buffer[pos] = value

        self.flush()

    def __alarm_state(self):
        alarm = [0] * 3
        if self._alarms[0][0]:
            alarm = [sum(value) for value in zip(alarm, self._alarms[0][1])]

        if self._alarms[1][0]:
            alarm = [sum(value) for value in zip(alarm, self._alarms[1][1])]

        return alarm
