#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - sound
"""

from datetime import datetime
from numbers import Number
from time import time, sleep
from thread_task import Task, Repeated, Periodic, Sleep, concat
from .constants import (
    BLUETOOTH,
    opUI_Write,
    opSound,
    TONE,
    PLAY,
    REPEAT,
    BREAK,
    LED,
    LED_ORANGE,
    LED_RED,
    LED_RED_FLASH,
    LED_GREEN
)
from .functions import (
    LCX,
    LCS
)
from .ev3 import EV3

TRIAS = {
    "tempo": 80,
    "beats_per_bar": 3,
    "led_sequence": [LED_ORANGE, LED_RED_FLASH],
    "tones": [
        ["c'", 1],
        ["e'", 1],
        ["g'", 1],
        ["c''", 3],
    ]
}

ALLE_MEINE_ENTCHEN = {
    "tempo": 130,
    "beats_per_bar": 4,
    "led_sequence": [
        LED_ORANGE,
        LED_RED,
        LED_ORANGE,
        LED_GREEN
    ],
    "tones": [
        ["c'", 1],
        ["d'", 1],
        ["e'", 1],
        ["f'", 1],
        ["g'", 2],
        ["g'", 2],
        ["a'", 1],
        ["a'", 1],
        ["a'", 1],
        ["a'", 1],
        ["g'", 4],
        ["a'", 1],
        ["a'", 1],
        ["a'", 1],
        ["a'", 1],
        ["g'", 4],
        ["f'", 1],
        ["f'", 1],
        ["f'", 1],
        ["f'", 1],
        ["e'", 2],
        ["e'", 2],
        ["d'", 1],
        ["d'", 1],
        ["d'", 1],
        ["d'", 1],
        ["c'", 4]
    ]
}

HAPPY_BIRTHDAY = {
    "tempo": 100,
    "beats_per_bar": 3,
    "upbeat": 1,
    "led_sequence": [
        LED_ORANGE,
        LED_GREEN,
        LED_RED,
        LED_GREEN
    ],
    "tones": [
        ["d'", 0.75],
        ["d'", 0.25],
        ["e'", 1],
        ["d'", 1],
        ["g'", 1],
        ["f#'", 2],
        ["d'", 0.75],
        ["d'", 0.25],
        ["e'", 1],
        ["d'", 1],
        ["a'", 1],
        ["g'", 2],
        ["d'", 0.75],
        ["d'", 0.25],
        ["d''", 1],
        ["b'", 1],
        ["g'", 1],
        ["f#'", 1],
        ["e'", 1],
        ["c''", 0.75],
        ["c''", 0.25],
        ["b'", 1],
        ["g'", 1],
        ["a'", 1],
        ["g'", 2]
    ]
}


class Jukebox(EV3):
    """
    plays songs and uses LEDs
    """
    def __init__(self, protocol: str=None, host: str=None, ev3_obj=None):
        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._volume = 1
        self._temperament = 440
        self._pos_color = None
        self._pos_tone = None
        self._pos_led = None

    @property
    def volume(self):
        """
        volume of sound [0 - 100] (default: 1)
        """
        return self._volume

    @volume.setter
    def volume(self, value: int):
        assert isinstance(value, int), "volume needs to be an integer"
        assert value >= 0 and value <= 100, \
            "volume needs to be in range [0 - 100]"
        self._volume = value

    @property
    def temperament(self):
        """
        temperament of the tones (delfault: 440 Hz)
        """
        return self._temperament

    @temperament.setter
    def temperament(self, value: Number):
        assert isinstance(value, Number), \
            "temperament needs to be a number"
        assert value > 0, "temperament needs to be positive"
        self._temperament = value

    def change_color(self, led_pattern: bytes) -> None:
        """
        changes LED color

        Positional Arguments:
          led_pattern:
            color of LEDs, f.i. ev3.LED_RED
        """
        ops = b''.join([
            opUI_Write,
            LED,
            led_pattern
        ])
        self.send_direct_cmd(ops)

    def play_tone(self, tone: str, duration: Number=0) -> None:
        """
        plays a tone

        Positional Arguments:
          tone:
            name of tone f.i. "c'", "cb''", "c#"

        Keyword Arguments:
          duration:
            length (sec.) of the tone (value 0 means forever)
        """
        assert isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration >= 0, "duration needs to be positive"
        if tone == "p":
            self.stop()
            return
        elif tone.startswith("c"):
            freq = self._temperament * 2**(-9/12)
        elif tone.startswith("d"):
            freq = self._temperament * 2**(-7/12)
        elif tone.startswith("e"):
            freq = self._temperament * 2**(-5/12)
        elif tone.startswith("f"):
            freq = self._temperament * 2**(-4/12)
        elif tone.startswith("g"):
            freq = self._temperament * 2**(-2/12)
        elif tone.startswith("a"):
            freq = self._temperament
        elif tone.startswith("b"):
            freq = self._temperament * 2**(2/12)
        else:
            raise AttributeError('unknown Tone: ' + tone)

        if len(tone) > 1:
            if tone[1] == "#":
                freq *= 2**(1/12)
            elif tone[1] == "b":
                freq /= 2**(1/12)

        if tone.endswith("'''"):
            freq *= 4
        elif tone.endswith("''"):
            freq *= 2
        elif tone.endswith("'"):
            pass
        else:
            freq /= 2

        freq = round(freq)
        if freq < 250:
            raise AttributeError('tone is too low: ' + tone)
        if freq > 10000:
            raise AttributeError('tone is too high: ' + tone)
        ops = b''.join([
            opSound,
            TONE,
            LCX(self._volume),
            LCX(freq),
            LCX(round(1000*duration))
        ])
        self.send_direct_cmd(ops)

    def sound(
            self,
            path: str,
            duration: float=None,
            repeat: bool=False
    ) -> Task:
        """
        returns a Task object, that plays a sound file

        Positional Arguments:
          path:
            name of the sound file (without extension ".rsf")

        Keyword Arguments:
          duration:
            duration of the sound file (in sec.)
          repeat:
            flag, if repeatedly playing
        """
        if repeat:
            ops = b''.join([
                opSound,
                REPEAT,
                LCX(self._volume),  # VOLUME
                LCS(path)  # NAME
            ])
        else:
            ops = b''.join([
                opSound,
                PLAY,
                LCX(self._volume),  # VOLUME
                LCS(path)  # NAME
            ])
        if not repeat and not duration:
            return Task(
                self.send_direct_cmd,
                args=(ops,)
            )
        elif not repeat and duration:
            t_inner = Task(
                self.send_direct_cmd,
                args=(ops,),
                duration=duration,
                action_stop=self.stop
            )
            return Task(t_inner.start, join=True)
        elif repeat and not duration:
            t_inner = Task(
                self.send_direct_cmd,
                args=(ops,),
                action_stop=self.stop,
                action_cont=self.send_direct_cmd,
                args_cont=(ops,),
                duration=999999999
            )
            return Task(t_inner.start, join=True)
        elif repeat and duration:
            class _Task(Task):
                def _final(self, **kwargs):
                    super()._final(**kwargs)
                    if self._root._time_action:
                        self._root._time_rest = (
                            self._root._time_action -
                            time()
                        )
                        self._root._time_action -= self._root._time_rest

                def _cont2(self, **kwargs):
                    self._time_action += self._time_rest
                    super()._cont2(**kwargs)

            t_inner = concat(
                _Task(
                    self.send_direct_cmd,
                    args=(ops,),
                    duration=duration,
                    action_stop=self.stop,
                    action_cont=self.send_direct_cmd,
                    args_cont=(ops,)
                ),
                _Task(self.stop)
            )
            return Task(t_inner.start, join=True)

    def stop(self) -> None:
        """
        stops the sound
        """
        self.send_direct_cmd(opSound + BREAK)

    def _init_tone(self) -> None:
        self._pos_tone = 0

    def _next_tone(self, song) -> float:
        if self._pos_tone == len(song["tones"]):
            return -1
        tone, beats = song["tones"][self._pos_tone]
        self.play_tone(tone)
        self._pos_tone += 1
        return 60 * beats / song["tempo"]

    def _init_color(self) -> None:
        self._pos_led = 0

    def _next_color(self, song) -> bool:
        self.change_color(song["led_sequence"][self._pos_led])
        self._pos_led += 1
        self._pos_led %= len(song["led_sequence"])

    def song(self, song: dict) -> Task:
        """
        returns a Task object, that plays a song
        """
        tones = concat(
            Task(
                self._init_tone,
                action_stop=self.stop
            ),
            Repeated(
                self._next_tone,
                args=(song,)
            ),
            Task(self.stop)
        )
        colors = Periodic(
            60 * song["beats_per_bar"] / song["tempo"],
            self._next_color,
            args=(song,)
        )
        if "upbeat" in song:
            colors = concat(
                Sleep(60 * song["upbeat"] / song["tempo"]),
                colors
            )
        colors = concat(
            Task(
                self._init_color,
                action_stop=self.change_color,
                args_stop=(LED_GREEN,)
            ),
            colors
        )
        return concat(
            Task(colors.start),
            Task(tones.start, join=True),
            Task(colors.stop)
        )


if __name__ == "__main__":
    jukebox = Jukebox(protocol=BLUETOOTH, host='00:16:53:42:2B:99')
    jukebox.verbosity = 1
    songs = concat(
        jukebox.song(HAPPY_BIRTHDAY),
        Sleep(1),
        jukebox.song(ALLE_MEINE_ENTCHEN)
    )
    songs.start()
    sleep(5)
    songs.stop()
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** stopped ***")
    sleep(3)
    songs.cont()
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** continued ***")
    sleep(14)
    jukebox.volume = 12
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 12 ***")
    sleep(5)
    jukebox.volume = 1
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 1 ***")
