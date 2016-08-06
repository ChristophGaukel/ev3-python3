#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 - sound
"""

# Copyright (C) 2016 Christoph Gaukel <christoph.gaukel@gmx.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import datetime
import numbers
import time
import ev3
import task

TRIAS = {
    "tempo": 80,
    "beats_per_bar": 3,
    "led_sequence": [ev3.LED_ORANGE, ev3.LED_RED_FLASH],
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
    "led_sequence": [ev3.LED_ORANGE, ev3.LED_RED, ev3.LED_ORANGE, ev3.LED_GREEN],
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
    "led_sequence": [ev3.LED_ORANGE, ev3.LED_GREEN, ev3.LED_RED, ev3.LED_GREEN],
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

class Jukebox(ev3.EV3):
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
        assert value >= 0 and  value <= 100, "volume needs to be in range [0 - 100]"
        self._volume = value

    @property
    def temperament(self):
        """
        temperament of the tones (delfault: 440 Hz)
        """
        return self._temperament
    @temperament.setter
    def temperament(self, value: float):
        assert isinstance(value, numbers.Number), "temperament needs to be a number"
        assert value > 0, "temperament needs to be positive"
        self._temperament = value

    def change_color(self, led_pattern: bytes) -> None:
        """
        changes LED color

        Attributes:
        led_pattern: color of LEDs, f.i. ev3.LED_RED
        """
        ops = b''.join([
            ev3.opUI_Write,
            ev3.LED,
            led_pattern
        ])
        self.send_direct_cmd(ops)

    # pylint: disable=too-many-branches
    def play_tone(self, tone: str, duration: float=0) -> None:
        """
        plays a tone

        Attributes:
        tone: name of tone f.i. "c'", "cb''", "c#"

        Keyword Attributes:
        duration: length (sec.) of the tone (value 0 means forever)
        """
        assert isinstance(duration, numbers.Number), "duration needs to be a number"
        assert duration >= 0, "duration needs to be positive"
        # pylint: disable=redefined-variable-type
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
        # pylint: enable=redefined-variable-type

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
            ev3.opSound,
            ev3.TONE,
            ev3.LCX(self._volume),
            ev3.LCX(freq),
            ev3.LCX(round(1000*duration))
        ])
        self.send_direct_cmd(ops)
    # pylint: enable=too-many-branches

    def sound(self, path: str, duration: float=None, repeat: bool=False) -> task.Task:
        """
        returns a Task object, that plays a sound file

        Attributes:
        path: name of the sound file (without extension ".rsf")

        Keyword Attributes:
        duration: duration of the sound file (in sec.)
        repeat: flag, if repeatedly playing
        """
        if repeat:
            ops = b''.join([
                ev3.opSound,
                ev3.REPEAT,
                ev3.LCX(self._volume), # VOLUME
                ev3.LCS(path)          # NAME
            ])
        else:
            ops = b''.join([
                ev3.opSound,
                ev3.PLAY,
                ev3.LCX(self._volume), # VOLUME
                ev3.LCS(path)          # NAME
            ])
        # pylint: disable=redefined-variable-type
        if not repeat and not duration:
            return task.Task(
                self.send_direct_cmd,
                args=(ops,)
            )
        elif not repeat and duration:
            t_inner = task.Task(
                self.send_direct_cmd,
                args=(ops,),
                duration=duration,
                action_stop=self.stop
            )
            return task.Task(t_inner.start, join=True)
        elif repeat and not duration:
            t_inner = task.Task(
                self.send_direct_cmd,
                args=(ops,),
                action_stop=self.stop,
                action_cont=self.send_direct_cmd,
                args_cont=(ops,),
                duration=999999999
            )
            return task.Task(t_inner.start, join=True)
        elif repeat and duration:
            class _Task(task.Task):
                # pylint: disable=protected-access
                def _final(self, **kwargs):
                    super()._final(**kwargs)
                    if self._root._time_action:
                        self._root._time_rest = self._root._time_action - time.time()
                        self._root._time_action -= self._root._time_rest
                # pylint: enable=protected-access
                def _cont2(self, **kwargs):
                    self._time_action += self._time_rest
                    super()._cont2(**kwargs)

            t_inner = task.concat(
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
        # pylint: enable=redefined-variable-type
            return task.Task(t_inner.start, join=True)

    def stop(self) -> None:
        """
        stops the sound
        """
        self.send_direct_cmd(ev3.opSound + ev3.BREAK)

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

    def song(self, song: dict) -> task.Task:
        """
        returns a Task object, that plays a song

        example:
        jukebox = ev3_sound.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
        my_song = jukebox.song(ev3_sound.HAPPY_BIRTHDAY)
        my_song.start()
        """
        tones = task.concat(
            task.Task(
                self._init_tone,
                action_stop=self.stop
            ),
            task.Repeated(
                self._next_tone,
                args=(song,)
            ),
            task.Task(self.stop)
        )
        colors = task.Periodic(
            60 * song["beats_per_bar"] / song["tempo"],
            self._next_color,
            args=(song,)
        )
        if "upbeat" in song:
            colors = task.concat(
                task.Sleep(60 * song["upbeat"] / song["tempo"]),
                colors
            )
        colors = task.concat(
            task.Task(
                self._init_color,
                action_stop=self.change_color,
                args_stop=(ev3.LED_GREEN,)
            ),
            colors
        )
        return task.concat(
            task.Task(colors.start),
            task.Task(tones.start, join=True),
            task.Task(colors.stop)
        )

# pylint: disable=invalid-name
if __name__ == "__main__":
    jukebox = Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
    jukebox.verbosity = 1
    songs = task.concat(
        jukebox.song(HAPPY_BIRTHDAY),
        task.Sleep(1),
        jukebox.song(ALLE_MEINE_ENTCHEN)
    )
    songs.start()
    time.sleep(5)
    songs.stop()
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** stopped ***")
    time.sleep(3)
    songs.cont()
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** continued ***")
    time.sleep(14)
    jukebox.volume = 12
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 12 ***")
    time.sleep(5)
    jukebox.volume = 1
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 1 ***")
