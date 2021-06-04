"""
LEGO Mindstorms EV3 direct commands - sound
"""

from struct import pack, unpack
from numbers import Number
import subprocess
import gtts
from thread_task import Task, Repeated, Periodic
from .constants import (
    opUI_Write,
    opSound,
    opFile,
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
    OPEN_READ,
    READ_BYTES,
    CLOSE
)
from .functions import LCX, LCS, LVX, GVX
from .ev3 import EV3
from .file import FileSystem
from .exceptions import FFMPEG, SysCmdError

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


class Sound(FileSystem):
    """
    basic sound functionality
    """
    def __init__(
            self,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            verbosity: int = 0,
            volume: int = None
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
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
          volume
            sound volume [%], values from 0 to 100
        """
        assert volume is None or isinstance(volume, int), \
            'volume needs to be of type int'
        assert volume is None or 0 <= volume <= 100, \
            'volume must be in range [0 - 100]'

        super().__init__(
                 protocol=protocol,
                 host=host,
                 ev3_obj=ev3_obj,
                 verbosity=verbosity
         )

        self._volume = volume

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)

        # create directory
        try:
            self.create_dir('../prjs/sound')
        except SysCmdError:
            pass  # directory already exists

    def __del__(self):
        try:
            self.del_dir('../prjs/sound', secure=False)
        except (SysCmdError, AttributeError):
            pass
        super().__del__()

    def __str__(self):
        '''
        description of the object in a str context
        '''
        return ' '.join((
            'Sound as',
            f'{self.protocol}',
            f'connected EV3 {self.host}',
            f'({self.name})'
        ))


    def tone(
            self,
            freq: int,
            *,
            duration: Number = None,
            volume: int = None
    ) -> None:
        '''
        plays a tone

        Mandatory positional arguments

          freq
            frequency of tone, range [250 - 10000]

        Optional keyword only arguments

          duration
            duration (sec.) of the tone (no duration means forever)
          volume
            volume [0 - 100] of tone
        '''
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or 0<= volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(freq, Number), \
            "freq must be a number"
        assert 250 <= freq <= 10000, \
            "freq needs to be in range [250 - 10000]"

        freq = round(freq)

        if duration is None:
            duration = 0

        if volume is None:
            volume = self._volume
        if volume is None:
            volume = self._physical_ev3._introspection["volume"]

        self.send_direct_cmd(
            b''.join((
                opSound,
                TONE,
                LCX(volume),
                LCX(freq),
                LCX(round(1000*duration))
            ))
        )

    def duration(
            self,
            path: str,
            *,
            local: bool = False
    ) -> float:
        '''
        detemines duration of a sound file by reading its header

        Mandatory positional arguments

          path
            name of the sound file (may be without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Optional keyword only arguments

          local
            flag, if path is a location on the local host
        '''
        assert isinstance(path, str), \
            'path needs to be a str'
        assert isinstance(local, bool), \
            "local must be a bool"

        if path.endswith('.rsf'):
            path = path[:-4]

        if local:
            with open(path + '.rsf', 'rb') as file:
                data = file.read(8)
        else:
            data = self.send_direct_cmd(
                b''.join((
                    opFile,
                    OPEN_READ,
                    LCS(path + '.rsf'),
                    LVX(4),  # file handle
                    LVX(0),  # file size
                    opFile,
                    READ_BYTES,
                    LVX(4),  # file handle
                    LCX(8),  # read 8 bytes (header only)
                    GVX(0),
                    opFile,
                    CLOSE,
                    LVX(4)  # file handle
                )),
                global_mem=8,
                local_mem=5
            )
        length, rate = unpack('>2H', data[2:6])
        return length / rate


    def play_sound(
            self,
            path: str,
            *,
            volume: int = None,
            repeat: bool = False,
            local: bool = False
    ) -> None:
        '''
        plays a sound file

        Mandatory positional arguments

          path
            name of the sound file (may be without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Keyword only arguments

          volume
            volume [0 - 100] of tone (defaults to attribute volume)
          repeat
            flag, if repeatedly playing
          local
            flag, if path is a location on the local host (PC)
        '''
        assert isinstance(path, str), \
            'path needs to be a str'
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or 0 <= volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"
        assert isinstance(local, bool), \
            "local must be a bool"

        if path.endswith('.rsf'):
            path = path[:-4]

        if volume is None:
            volume = self._volume
        if volume is None:
            volume = self._physical_ev3._introspection["volume"]

        if local:
            self.load_file(path + '.rsf', '../prjs/sound/tmp.rsf')
            path = '../prjs/sound/tmp'

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
            volume: int = None,
            duration: float = None,
            repeat: bool = False,
            local: bool = False
    ) -> Task:
        '''
        returns a Task object, which plays a sound file

        Mandatory positional arguments

          path
            name of the sound file (may be without extension ".rsf")
            as absolute path, or relative to /home/root/lms2012/sys/

        Optional keyword only arguments

          volume
            volume [0 - 100] of tone (defaults to attribute volume)
          duration
            total duration in sec.,
            in combination with repeat, this means interruption,
          repeat
            flag, if repeatedly playing (unlimited if no duration is set)
          local
            flag, if path is a location on the local host
        '''
        assert isinstance(path, str), \
            'path needs to be a str'
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, int), \
            "volume needs to be an int"
        assert volume is None or 0 <= volume <= 100, \
            "volume needs to be in range [0 - 100]"
        assert isinstance(repeat, bool), \
            "repeat must be a bool"
        assert isinstance(local, bool), \
            "local must be a bool"

        if path.endswith('.rsf'):
            path = path[:-4]

        if volume is None:
            volume = self._volume
        if volume is None:
            volume = self._physical_ev3._introspection["volume"]

        if local:
            ev3_path = '../prjs/sound/tmp'
        else:
            ev3_path = path

        if repeat:
            if duration is None:
                duration = 999999999  # unlimited
                stop_it = False
            else:
                stop_it = True
            # play it repeatedly
            task = Task(
                self.play_sound,
                args=(ev3_path,),
                kwargs={'repeat': True, 'volume': volume},
                action_stop=self.stop_sound,
                action_cont=self.play_sound,
                args_cont=(ev3_path,),
                kwargs_cont={'repeat': True, 'volume': volume},
                duration=duration
            )
            if stop_it:
                task += Task(
                    self.stop_sound
                )
        else:
            if duration is None:
                duration = self.duration(path, local=local)
            task = Task(
                self.play_sound,
                args=(ev3_path,),
                kwargs={'repeat': False, 'volume': volume},
                duration=duration
            )

        if local:
            return Task(
                self.load_file,
                args=(path + '.rsf', ev3_path + '.rsf'),
                kwargs={'check': True}
            ) + task

        return task

    def stop_sound(self) -> None:
        """
        stops the sound
        """
        self.send_direct_cmd(opSound + BREAK)


class Jukebox(Sound):
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
                volume=volume,
                verbosity=verbosity
         )

        self._volume = volume
        self._temperament = temperament

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)

    def __str__(self):
        """
        description of the object in a str context
        """
        return ' '.join((
            'Jukebox as',
            f'{self.protocol}',
            f'connected EV3 {self.host}',
            f'({self.name})'
        ))

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

        Optional keyword only arguments

          duration
            length (sec.) of the tone (no duration means forever)
          volume
            volume [0 - 100] of tone (defaults to attribute volume)
        """

        if tone == "p":
            self.stop_sound()
            return

        if tone.startswith("c"):
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

        self.tone(
            freq,
            duration=duration,
            volume=volume
        )


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
        assert volume is None or 0 <= volume <= 100, \
            "volume needs to be in range [0 - 100]"

        if volume is None:
            volume = self._volume
        if volume is None:
            volume = self._physical_ev3._introspection["volume"]

        class Tones:
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
                tone = self._tones[self._pos][0]
                self._jukebox.play_tone(tone, volume=volume)

        class Colors:
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

        tones = Tones(song, self)
        colors = Colors(song, self)
        # colors is endless and must be stopped
        t_colors = Periodic(
                60 * song["beats_per_bar"] / song["tempo"],
                colors.color_next,
                action_stop=self.change_color,
                args_stop=(LED_GREEN,),
                action_cont=colors.color_again
        )
        # tones knows its end and does the timing
        return Task(
                tones.reset
        ) + Task(
                colors.reset
        ) + Task(
                t_colors.start,
                args=(upbeat_duration,)
        ) + Repeated(
                tones.tone_next,
                action_stop=self.stop_sound,
                action_cont=tones.tone_again
        ) + Task(
                self.stop_sound
        ) + Task(
                t_colors.stop
        )


class Voice(Sound):
    """
    lets the EV3 device speak tts (text to sound)
    """
    def __init__(
            self,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            volume: int = None,
            lang: str = 'en',
            tld: str = 'com',
            slow: bool = False,
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
          filesystem
            already existing FileSystem object
          volume
            sound volume [%], values from 0 to 100
          lang
            language, e.g. 'it', 'fr, 'de', 'en' (default)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert lang is None or isinstance(lang, str), \
            'lang must be a str'
        assert isinstance(tld, str), \
            'tld must be a str'
        assert isinstance(slow, bool), \
            'slow must be a bool'

        super().__init__(
            protocol=protocol,
            host=host,
            ev3_obj=ev3_obj,
            verbosity=verbosity,
            volume=volume
         )

        self._lang = lang
        self._tld = tld
        self._slow = slow

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)

    def __str__(self):
        """
        description of the object in a str context
        """
        return ' '.join((
            'Voice as',
            f'{self.protocol}',
            f'connected EV3 {self.host}',
            f'({self.name})'
        ))


    def speak(
            self,
            txt: str,
            *,
            lang: str=None,
            tld: str = None,
            slow: bool = None,
            duration: Number=None,
            volume: int=None
    ) -> Task:
        '''
        let the EV3 device speak some text

        Mandatory positional arguments

          txt
            text to speak

        Optional keyword only arguments

          lang
            language, e.g. 'it', 'fr, 'de', 'en' (default)
          tld
            top level domain of google server, e.g. 'de', 'co.jp', 'com' (default)
          slow
            reads text more slowly. Defaults to False
          duration
            length (sec.) of the tone (no duration means forever)
          volume
            volume [0 - 100] of tone (defaults to attribute volume)
        '''
        assert lang is None or isinstance(lang, str), \
            'lang must be a str'
        assert tld is None or isinstance(tld, str), \
            'tld must be a str'
        assert slow is None or isinstance(slow, bool), \
            'slow must be a bool'
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"
        assert duration is None or duration > 0, \
            "duration needs to be positive"
        assert volume is None or isinstance(volume, int), \
            'volume needs to be of type int'
        assert volume is None or 0 <= volume <= 100, \
            'volume must be between 0 and 100'

        if lang is None:
            lang = self._lang
            tld = self._tld
        if tld is None:
            tld = self._tld
        if slow is None:
            slow = self._slow
        if volume is None:
            volume = self._volume
        if volume is None:
            volume = self._physical_ev3._introspection["volume"]

        path = '../prjs/sound/txt'
        safety_gap = 120  # add this number of b'\x80'
        min_gap = 0  # minimum (real) gap between peaces
        data = None


        def prepare():
            '''
            prepare raw sound data
            '''
            nonlocal data

            # ffmpeg converts to raw audio (rate 8000 Hz, sample width 8 bit)
            process = subprocess.Popen(
                [
                    'ffmpeg',
                    '-loglevel', 'error',
                    '-i', '-',  # read from stdin
                    '-acodec', 'pcm_u8',
                    '-f', 'u8',
                    '-ar', '8000',
                    '-filter:a', 'volume=1.5',
                    '-'  # write to stdout
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # tts produces mp3 data
            tts = gtts.gTTS(txt, lang=lang, tld=tld, slow=slow)
            tts.write_to_fp(process.stdin)

            # do transformation into raw data
            data, err = process.communicate()
            if err != b'':
                raise FFMPEG(err.decode())

        def send_and_play(data: bytes, *, pause: float=0, volume: int=None):
            '''
            send data to EV3 and play
            '''
            def header(size: int) -> bytes:
                '''
                creates rsf header
                '''
                return b''.join((
                    b'\x00\x01',
                    pack('H', size),
                    b'\x1f\x40',  # 8000 (sampling rate)
                    b'\x00\x00'
                ))

            duration = (len(data) + pause) / 8000

            # send to EV3
            self.write_file(
                path + '.rsf',
                header(len(data) + safety_gap) + data + b'\x80' * safety_gap,
                check=False
            )

            # play
            self.play_sound(
                path,
                volume=volume
            )

            return duration


        def next_part() -> float:
            '''
            This one is called by the Repeated
            '''
            nonlocal data

            # when all is done, end Repeated
            if data is None:
                del data
                return -1

            pause_start = None
            for pos, curr_byte in enumerate(data):
                if pos == 0 and curr_byte == 128:
                    signal_start = None
                elif pos == 0:
                    signal_start = pos
                elif pre_byte != 128 and curr_byte == 128:
                    pause_start = pos
                elif pre_byte == 128 and curr_byte != 128:
                    if (
                            signal_start is not None and
                            pause_start is not None and
                            pos >= (pause_start + safety_gap + min_gap)
                    ):
                        wait = send_and_play(
                            data[signal_start:pause_start],
                            pause=pos - pause_start,
                            volume=volume
                        )
                        data = data[pos:]
                        return wait

                    pause_start = None
                    if signal_start is None:
                        signal_start = pos
                pre_byte = curr_byte

            if signal_start is not None and pause_start is not None:
                wait = send_and_play(data[signal_start:pause_start], volume=volume)
                data = None
                return wait

            if signal_start is not None:
                wait = send_and_play(data[signal_start:], volume=volume)
                data = None
                return wait

            del data
            return -1

        if duration is None:
            return Task(prepare) + Repeated(next_part)
        return Task(
            Task(prepare) + Repeated(next_part),
            duration=duration
        )
