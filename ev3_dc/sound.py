"""
LEGO Mindstorms EV3 direct commands - sound
"""

from numbers import Number
from thread_task import Task, Repeated, Periodic
from .constants import (
    opUI_Write,
    opSound,
    TONE,
    PLAY,
    REPEAT,
    BREAK,
    LED,
    LED_OFF,
    LED_ORANGE,
    LED_RED,
    LED_GREEN,
    LED_GREEN_FLASH,
    LED_RED_FLASH,
    LED_ORANGE_FLASH,
    LED_GREEN_PULSE,
    LED_RED_PULSE,
    LED_ORANGE_PULSE,
)
from .functions import LCX, LCS
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
    def __init__(
            self,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            volume: int = None,
            temperament:int = 440,
            verbosity: int = 0
    ):
        """
        Keyword only arguments (either protocol and host or ev3_obj)

          protocol
            either ev3_dc.BLUETOOTH, ev3_dc.USB or ev3_dc.WIFI
          host
            mac-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object 
            (its already established connection will be used)
          volume
            sound volume [%], values from 0 to 100
          temperament
            temperament of the tones (delfault: 440 Hz)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert volume is None or isinstance(volume, int), \
            'volume needs to be of type int'
        assert volume is None or 0 <= volume <= 100, \
            'volume must be between 0 and 100'
        assert isinstance(temperament, int), \
            'temperament needs to be an int'
        assert temperament > 0, \
            'temperament needs to be positive'

        super().__init__(
                 protocol=protocol,
                 host=host,
                 ev3_obj=ev3_obj,
                 verbosity=verbosity
         )
        
        self._volume = volume
        self._temperament = temperament

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)
        
    def __str__(self):
        """description of the object in a str context"""
        return 'Jukebox as ' + super().__str__()

    @property
    def temperament(self):
        """
        temperament of the tones (delfault: 440 Hz)
        """
        return self._temperament

    @temperament.setter
    def temperament(self, value: int):
        assert isinstance(value, int), \
            "temperament needs to be an int"
        assert value > 0, "temperament needs to be positive"
        self._temperament = value

    def change_color(self, led_pattern: bytes) -> None:
        """
        changes LED color

        Positional arguments:
          led_pattern:
            color of LEDs, f.i. ev3.LED_RED
        """
        assert isinstance(led_pattern, bytes), \
            'led_pattern must be of type bytes'
        assert led_pattern in (
                LED_OFF,
                LED_GREEN,
                LED_RED,
                LED_ORANGE,
                LED_GREEN_FLASH,
                LED_RED_FLASH,
                LED_ORANGE_FLASH,
                LED_GREEN_PULSE,
                LED_RED_PULSE,
                LED_ORANGE_PULSE,
        ), 'LED pattern ' + led_pattern + ' not provided'
        ops = b''.join((
            opUI_Write,
            LED,
            led_pattern
        ))
        self.send_direct_cmd(ops)

    def play_tone(
            self,
            tone: str,
            *,
            duration: Number = None,
            volume: int = None
    ) -> None:
        """
        plays a tone

        Mandatory positional arguments

          tone
            name of tone f.i. "c'", "cb''", "c#"

        Keyword only arguments

          duration
            length (sec.) of the tone (no duration means forever)
          volume
            volume [0 - 100] of tone (defaults to attribute volume)
        """
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
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
            volume = self._physical_ev3._introspection["volume"]

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
            *,
            volume: int = None,
            repeat: bool = False
    ) -> None:
        """
        plays a sound file

        Mandatory positional arguments

          path
            name of the sound file (without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Keyword only arguments

          volume
            volume [0 - 100] of tone (defaults to attribute volume)
          repeat
            flag, if repeatedly playing
        """
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"

        if volume is not None:
            pass
        elif self._volume is not None:
            volume = self._volume
        else:
            volume = self._physical_ev3._introspection["volume"]

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
            *,
            duration: float = None,
            volume: int = None,
            repeat: bool = False
    ) -> Task:
        """
        returns a Task object, that plays a sound file

        Mandatory positional arguments

          path
            name of the sound file (without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Keyword only arguments

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
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"

        if volume is not None:
            pass
        elif self._volume is not None:
            volume = self._volume
        else:
            volume = self._physical_ev3._introspection["volume"]

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

    def song(
            self,
            song: dict,
            *,
            volume: int = None
    ) -> Task:
        """
        returns a Task object, that plays a song

        Mandatory positional arguments

          song
            dict with song data (e.g. ev3.HAPPY_BIRTHDAY)

        Keyword only arguments

          volume
            volume [0 - 100] of tone (defaults to attribute volume)
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
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or volume >= 0 and volume <= 100, \
            "volume needs to be in range [0 - 100]"

        if volume is not None:
            pass
        elif self._volume is not None:
            volume = self._volume
        else:
            volume = self._physical_ev3._introspection["volume"]

        class Tones(object):
            def __init__(self, song: dict, jukebox: 'Jukebox'):
                self._tones = song['tones']
                self._tempo = song['tempo']
                self._jukebox = jukebox
                self._pos = 0

            def reset(self):
                self._pos = 0

            def tone_next(self):
                if self._pos == len(self._tones):
                    return -1
                tone, beats = self._tones[self._pos]
                self._jukebox.play_tone(tone, volume=volume)
                self._pos += 1
                return 60 * beats / self._tempo

            def tone_again(self):
                tone, beats = self._tones[self._pos]
                self._jukebox.play_tone(tone, volume=volume)

        class Colors(object):
            def __init__(self, song: dict, jukebox: 'Jukebox'):
                self._led_sequence = song['led_sequence']
                self._jukebox = jukebox
                self._pos = 0

            def reset(self):
                self._pos = 0

            def color_next(self):
                self._jukebox.change_color(self._led_sequence[self._pos])
                self._pos += 1
                self._pos %= len(self._led_sequence)

            def color_again(self):
                self._jukebox.change_color(self._led_sequence[self._pos])

        if "upbeat" in song:
            upbeat_duration = 60 * song["upbeat"] / song["tempo"]
        else:
            upbeat_duration = 0

        t = Tones(song, self)
        c = Colors(song, self)
        # colors is endless and must be stopped
        colors = Periodic(
                60 * song["beats_per_bar"] / song["tempo"],
                c.color_next,
                action_stop=self.change_color,
                args_stop=(LED_GREEN,),
                action_cont=c.color_again
        )
        # tones knows its end and does the timing
        return Task(
                t.reset
        ) + Task(
                c.reset
        ) + Task(
                colors.start,
                args=(upbeat_duration,)
        ) + Repeated(
                t.tone_next,
                action_stop=self.stop_sound,
                action_cont=t.tone_again
        ) + Task(
                self.stop_sound
        ) + Task(
                colors.stop
        )
