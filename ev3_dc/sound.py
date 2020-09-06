#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - sound
"""

from datetime import datetime
from numbers import Number, Integral
from time import sleep
from thread_task import Task, Repeated, Periodic, Sleep
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

TRIAD = {
    "tempo": 80,
    "beats_per_bar": 3,
    "led_sequence": (LED_ORANGE, LED_RED_FLASH),
    "tones": (
        ("c'", 1),
        ("e'", 1),
        ("g'", 1),
        ("c''", 3)
    )
}

ALLE_MEINE_ENTCHEN = {
    "tempo": 130,
    "beats_per_bar": 4,
    "led_sequence": (
        LED_ORANGE,
        LED_RED,
        LED_ORANGE,
        LED_GREEN
    ),
    "tones": (
        ("c'", 1),
        ("d'", 1),
        ("e'", 1),
        ("f'", 1),
        ("g'", 2),
        ("g'", 2),
        ("a'", 1),
        ("a'", 1),
        ("a'", 1),
        ("a'", 1),
        ("g'", 4),
        ("a'", 1),
        ("a'", 1),
        ("a'", 1),
        ("a'", 1),
        ("g'", 4),
        ("f'", 1),
        ("f'", 1),
        ("f'", 1),
        ("f'", 1),
        ("e'", 2),
        ("e'", 2),
        ("d'", 1),
        ("d'", 1),
        ("d'", 1),
        ("d'", 1),
        ("c'", 4)
    )
}

HAPPY_BIRTHDAY = {
    "tempo": 100,
    "beats_per_bar": 3,
    "upbeat": 1,
    "led_sequence": (
        LED_ORANGE,
        LED_GREEN,
        LED_RED,
        LED_GREEN
    ),
    "tones": (
        ("d'", 0.75),
        ("d'", 0.25),
        ("e'", 1),
        ("d'", 1),
        ("g'", 1),
        ("f#'", 2),
        ("d'", 0.75),
        ("d'", 0.25),
        ("e'", 1),
        ("d'", 1),
        ("a'", 1),
        ("g'", 2),
        ("d'", 0.75),
        ("d'", 0.25),
        ("d''", 1),
        ("b'", 1),
        ("g'", 1),
        ("f#'", 1),
        ("e'", 1),
        ("c''", 0.75),
        ("c''", 0.25),
        ("b'", 1),
        ("g'", 1),
        ("a'", 1),
        ("g'", 2)
    )
}

EU_ANTEMN = {
    "tempo": 100,
    "beats_per_bar": 4,
    "led_sequence": (
        LED_ORANGE,
        LED_GREEN,
        LED_RED,
        LED_GREEN
    ),
    "tones": (
        ("a'", 1),
        ("a'", 1),
        ("bb'", 1),
        ("c''", 1),
        ("c''", 1),
        ("bb'", 1),
        ("a'", 1),
        ("g'", 1),
        ("f'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", 1),
        ("a'", 1.5),
        ("g'", .5),
        ("g'", 2),
        ("a'", 1),
        ("a'", 1),
        ("bb'", 1),
        ("c''", 1),
        ("c''", 1),
        ("bb'", 1),
        ("a'", 1),
        ("g'", 1),
        ("f'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", 1),
        ("g'", 1.5),
        ("f'", .5),
        ("f'", 2),
        ("g'", 1),
        ("g'", 1),
        ("a'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", .5),
        ("bb'", .5),
        ("a'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", .5),
        ("bb'", .5),
        ("a'", 1),
        ("g'", 1),
        ("f'", 1),
        ("g'", 1),
        ("c'", 1),
        ("a'", 2),
        ("a'", 1),
        ("bb'", 1),
        ("c''", 1),
        ("c''", 1),
        ("bb'", 1),
        ("a'", 1),
        ("g'", 1),
        ("f'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", 1),
        ("g'", 1.5),
        ("f'", .5),
        ("f'", 1)
    )
}

FRERE_JACQUES = {
    "tempo": 100,
    "beats_per_bar": 4,
    "led_sequence": (
        LED_RED,
        LED_GREEN,
        LED_RED,
        LED_GREEN
    ),
    "tones": (
        ("f'", 1),
        ("g'", 1),
        ("a'", 1),
        ("f'", 1),
        ("f'", 1),
        ("g'", 1),
        ("a'", 1),
        ("f'", 1),
        ("a'", 1),
        ("bb'", 1),
        ("c''", 2),
        ("a'", 1),
        ("bb'", 1),
        ("c''", 2),
        ("c''", .75),
        ("d''", .25),
        ("c''", .5),
        ("bb'", .5),
        ("a'", 1),
        ("f'", 1),
        ("c''", .75),
        ("d''", .25),
        ("c''", .5),
        ("bb'", .5),
        ("a'", 1),
        ("f'", 1),
        ("f'", 1),
        ("c'", 1),
        ("f'", 2),
        ("f'", 1),
        ("c'", 1),
        ("f'", 2)
     )
}


class Jukebox(EV3):
    """
    plays songs and uses LEDs
    """
    def __init__(self, protocol: str = None, host: str = None, ev3_obj=None):
        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._volume = 1
        self._temperament = 440

    @property
    def volume(self):
        """
        volume of sound [0 - 100] (default: 1)
        """
        return self._volume

    @volume.setter
    def volume(self, value: int):
        assert isinstance(value, Integral), \
            "volume needs to be an integer"
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
        ops = b''.join((
            opUI_Write,
            LED,
            led_pattern
        ))
        self.send_direct_cmd(ops)

    def play_tone(
            self,
            tone: str,
            duration: Number = None,
            volume: Number = None
    ) -> None:
        """
        plays a tone

        Positional Arguments

          tone
            name of tone f.i. "c'", "cb''", "c#"

        Keyword Arguments

          duration
            length (sec.) of the tone (no duration means forever)
          volume
            volume [0 - 100] of tone (defaults to attribute volume)
        """
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, Integral), \
            "volume needs to be an integer"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"

        if tone == "p":
            self.stop_sound()
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
            raise AttributeError('unknown tone: ' + tone)

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
            raise AttributeError(
                'tone is too low: ' + tone + ' (' + str(freq) + ' Hz)'
            )
        if freq > 10000:
            raise AttributeError(
                'tone is too high: ' + tone + ' (' + str(freq) + ' Hz)'
            )

        if duration is None:
            duration = 0

        if volume is None:
            volume = self._volume

        ops = b''.join((
            opSound,
            TONE,
            LCX(volume),
            LCX(freq),
            LCX(round(1000*duration))
        ))
        self.send_direct_cmd(ops)

    def play_sound(
            self,
            path: str,
            volume: Number = None,
            repeat: bool = False
    ) -> None:
        """
        plays a sound file

        Positional Arguments

          path
            name of the sound file (without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Keyword Arguments

          volume
            volume [0 - 100] of tone (defaults to attribute volume)
          repeat
            flag, if repeatedly playing
        """
        assert volume is None or isinstance(volume, Integral), \
            "volume needs to be an integer"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"

        if volume is None:
            volume = self._volume

        if repeat:
            ops = b''.join((
                opSound,
                REPEAT,
                LCX(volume),  # VOLUME
                LCS(path)  # NAME
            ))
        else:
            ops = b''.join((
                opSound,
                PLAY,
                LCX(volume),  # VOLUME
                LCS(path)  # NAME
            ))

        self.send_direct_cmd(ops)

    def sound(
            self,
            path: str,
            duration: float = None,
            volume: Number = None,
            repeat: bool = False
    ) -> Task:
        """
        returns a Task object, that plays a sound file

        Positional Arguments

          path
            name of the sound file (without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Keyword Arguments

          duration
            duration of the sound file (in sec.)
          volume
            volume [0 - 100] of tone (defaults to attribute volume)
          repeat
            flag, if repeatedly playing
        """
        assert isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, Integral), \
            "volume needs to be an integer"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"

        if not repeat and not duration:
            return Task(
                self.play_sound,
                args=(path,),
                kwargs={'volume': volume},
                action_stop=self.stop_sound
            )
        elif not repeat and duration:
            return Task(Task(
                self.play_sound,
                args=(path,),
                kwargs={'volume': volume},
                duration=duration,
                action_stop=self.stop_sound
            ))
        elif repeat and not duration:
            return Task(Task(
                self.play_sound,
                args=(path,),
                kwargs={'repeat': True, 'volume': volume},
                action_stop=self.stop_sound,
                action_cont=self.play_sound,
                args_cont=(path,),
                kwargs_cont={'repeat': repeat, 'volume': volume},
                duration=999999999  # unlimited
            ))
        elif repeat and duration:
            return Task(
                Task(
                    self.play_sound,
                    args=(path,),
                    kwargs={'repeat': True, 'volume': volume},
                    action_stop=self.stop_sound,
                    action_cont=self.play_sound,
                    args_cont=(path,),
                    kwargs_cont={'repeat': True, 'volume': volume},
                    duration=duration
                ).append(
                    Task(self.stop_sound)
                )
            )

    def stop_sound(self) -> None:
        """
        stops the sound
        """
        self.send_direct_cmd(opSound + BREAK)

    def song(self, song: dict) -> Task:
        """
        returns a Task object, that plays a song
        """
        assert isinstance(song, dict), \
            'song needs to be a dict'
        assert 'beats_per_bar' in song, \
            "song must have a key 'beats_per_bar'"
        assert 'tempo' in song, \
            "song must have a key 'tempo'"
        assert 'tones' in song, \
            "song must have a key 'tones'"
        assert 'led_sequence' in song, \
            "song must have a key 'led_sequence'"

        class NextTone(object):
            def __init__(self, song: dict, jukebox: 'Jukebox'):
                self._tones = song['tones']
                self._tempo = song['tempo']
                self._jukebox = jukebox
                self._pos = 0

            def reset(self):
                self._pos = 0

            def next(self):
                if self._pos == len(self._tones):
                    return -1
                tone, beats = self._tones[self._pos]
                self._jukebox.play_tone(tone)
                self._pos += 1
                return 60 * beats / self._tempo

        class NextColor(object):
            def __init__(self, song: dict, jukebox: 'Jukebox'):
                self._led_sequence = song['led_sequence']
                self._jukebox = jukebox
                self._pos = 0

            def reset(self):
                self._pos = 0

            def next(self):
                self._jukebox.change_color(self._led_sequence[self._pos])
                self._pos += 1
                self._pos %= len(self._led_sequence)

        nt = NextTone(song, self)
        nc = NextColor(song, self)
        tones = (
            Task(
                nt.reset,
                action_stop=self.stop_sound
            ) +
            Repeated(nt.next) +
            Task(self.stop_sound)
        )
        colors = (
            Task(
                nc.reset,
                action_stop=self.change_color,
                args_stop=(LED_GREEN,)
            ) +
            Periodic(
                60 * song["beats_per_bar"] / song["tempo"],
                nc.next
            )
        )

        if "upbeat" in song:
            upbeat_duration = 60 * song["upbeat"] / song["tempo"]
        else:
            upbeat_duration = 0

        return (
            Task(
                colors.start,
                args=(upbeat_duration,)
            ) +
            Task(tones) +  # threadless child
            Task(colors.stop)
        )


if __name__ == "__main__":
    jukebox = Jukebox(protocol=BLUETOOTH, host='00:16:53:42:2B:99')
    jukebox.verbosity = 1
    songs = (
        jukebox.song(HAPPY_BIRTHDAY) +
        Sleep(1) +
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
