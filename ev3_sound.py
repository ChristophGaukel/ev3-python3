#!/usr/bin/env python3

import ev3, time, datetime, sched, threading, task, numbers

ALLE_MEINE_ENTCHEN = {"tempo": 130,
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

HAPPY_BIRTHDAY = {"tempo": 100,
                  "beats_per_bar": 3,
                  "led_sequence": [ev3.LED_ORANGE, ev3.LED_RED, ev3.LED_ORANGE, ev3.LED_GREEN],
                  "tones": [
                      ["p", 2],
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
        self._tone_timer = None
        self._led_timer = None
        self._tone_stop = None
        self._time_abs = None
        self._led_periodic = None
        self._pos_color = None
        self._pos_tone = None
        self._song = None

    @property
    def volume(self):
        """
        volume of sound [0 - 100] (default: 1)
        """
        return self._volume
    @volume.setter
    def volume(self, value:int):
        assert isinstance(value, int), "volume needs to be an integer"
        assert 0 <= value and  value <= 100, "volume needs to be in range [0 - 100]"
        self._volume = value

    @property
    def temperament(self):
        """
        temperament of the tones (delfault: 440 Hz)
        """
        return self._temperament
    @temperament.setter
    def temperament(self, value:numbers.Number):
        assert isinstance(temperament, numbers.Number), "temperament needs to be a number"
        assert value > 0, "temperament needs to be positive"
        self._temperament = value

    def change_color(self, led_pattern: bytes, duration: float=0) -> None:
        """
        changes LED color
          duration: time (sec.) until control comes back (value 0 means directly)
        """
        assert isinstance(duration, numbers.Number), "duration needs to be a number"
        assert duration >= 0, "duration needs to be positive"
        if duration != 0:
            time_start = time.time()
        ops = b''.join([
            ev3.opUI_Write,
            ev3.LED,
            led_pattern
        ])
        self.send_direct_cmd(ops)
        if duration != 0:
            wait = max(0, time.time() + duration - time_start)
            time.sleep(wait)

    def play_tone(self, tone: str, beat: float=0, duration: float=0) -> None:
        """
        plays a tone
          tone: name f.i. "c'", "cb''", "c#"
          beat: length (sec.) of the tone (value 0 means forever)
          duration: time (sec.) until control comes back (value 0 means directly)
        """
        assert isinstance(beat, numbers.Number), "beat needs to be a number"
        assert beat >= 0, "beat needs to be positive"
        assert isinstance(duration, numbers.Number), "duration needs to be a number"
        assert duration >= 0, "duration needs to be positive"
        if duration != 0:
            time_start = time.time()
        volume = self._volume
        if   tone.startswith("c#"):
            freq = self._temperament * 2**(-8/12)
        elif tone.startswith("cb"):
            freq = self._temperament * 2**(-10/12)
        elif tone.startswith("c"):
            freq = self._temperament * 2**(-9/12)
        elif tone.startswith("d#"):
            freq = self._temperament * 2**(-6/12)
        elif tone.startswith("db"):
            freq = self._temperament * 2**(-8/12)
        elif tone.startswith("d"):
            freq = self._temperament * 2**(-7/12)
        elif tone.startswith("e#"):
            freq = self._temperament * 2**(-4/12)
        elif tone.startswith("eb"):
            freq = self._temperament * 2**(-6/12)
        elif tone.startswith("e"):
            freq = self._temperament * 2**(-5/12)
        elif tone.startswith("f#"):
            freq = self._temperament * 2**(-3/12)
        elif tone.startswith("fb"):
            freq = self._temperament * 2**(-5/12)
        elif tone.startswith("f"):
            freq = self._temperament * 2**(-4/12)
        elif tone.startswith("g#"):
            freq = self._temperament * 2**(-1/12)
        elif tone.startswith("gb"):
            freq = self._temperament * 2**(-3/12)
        elif tone.startswith("g"):
            freq = self._temperament * 2**(-2/12)
        elif tone.startswith("a#"):
            freq = self._temperament * 2**(1/12)
        elif tone.startswith("ab"):
            freq = self._temperament * 2**(-1/12)
        elif tone.startswith("a"):
            freq = self._temperament
        elif tone.startswith("b#"):
            freq = self._temperament * 2**(3/12)
        elif tone.startswith("bb"):
            freq = self._temperament * 2**(1/12)
        elif tone.startswith("b"):
            freq = self._temperament * 2**(2/12)
        elif tone == "p":
            pass
        else:
            raise AttributeError('unknown Tone')

        if tone == "p":
            self.stop_sound()
        else:
            if tone.endswith("'''"):
                freq *= 4
            elif tone.endswith("''"):
                freq *= 2
            elif tone.endswith("'"):
                pass
            else:
                freq /= 2
            ops = b''.join([
                ev3.opSound,
                ev3.TONE,
                ev3.LCX(volume),
                ev3.LCX(round(freq)),
                ev3.LCX(round(1000*beat))
            ])
            self.send_direct_cmd(ops)
        if duration != 0:
            wait = max(0, time.time() + duration - time_start)
            time.sleep(wait)

    def stop_sound(self) -> None:
        """
        stops the sound
        """
        self.send_direct_cmd(ev3.opSound + ev3.BREAK)

    def song(self, song: dict):
        """
        factory: returns Song object, that plays a song
        """
        return Song(self, song)

    def play_song(self, song: dict) -> bytes:
        """
        plays a song (dependend from sync_mode):
          STD:   sends one direct command,
                 control directly comes back,
                 EV3 device is blocked until the song is finished.
          SYNC:  sends tone after tone, 
                 control comes back, when song is finished
                 EV3 device is blocked until the song is finished.
          ASYNC: uses multithreading, 
                 control directly comes back,
                 EV3 device is not blocked 
        """
        if self._return_ops:
            return self._play_song_std(song)
        elif self._sync_mode == ev3.ASYNC:
            self._play_song_async(song)
            return b''
        elif self._sync_mode == ev3.STD:
            ops = self._play_song_std(song)
            return self.send_direct_cmd(ops)
        else:
            self._play_song_sync(song)
            return b''

    def _play_song_async(self, song: dict) -> None:
        """
        plays a song (uses multithreading)
        """
        Song(self, song).start()

    def _play_song_sync(self, song: dict) -> None:
        """
        plays a song (synchrone mode)
        """
        tempo = song["tempo"]
        beats_per_bar = song["beats_per_bar"]
        led_sequence = song["led_sequence"]
        pos_color = 0
        duration_total = 0
        duration_led = 0
        duration_bar =  (60000 * beats_per_bar / tempo)
        for tone, beats in song["tones"]:
            duration_tone = round(60000 * beats / tempo)
            # change color of LED?
            if round(duration_led, 2) >= round(duration_bar, 2):
                self.change_color(led_sequence[pos_color])
                pos_color += 1
                pos_color %= len(led_sequence)
                duration_led %= duration_bar
            if (tone != "p" or duration_total != 0):
                self.play_tone(tone, duration_tone)
            duration_total += duration_tone
            duration_led += duration_tone
        self.change_color(ev3.LED_GREEN)

    def _play_song_std(self, song: dict) -> bytes:
        """
        plays a song (return sequence of operations)
        """
        tempo = song["tempo"]
        beats_per_bar = song["beats_per_bar"]
        led_sequence = song["led_sequence"]
        pos_color = 0
        duration_total = 0
        duration_led = 0
        duration_bar =  (60000 * beats_per_bar / tempo)
        ops = b''
        for tone, beats in song["tones"]:
            duration_tone = round(60000 * beats / tempo)
            if (tone != "p" or duration_total != 0):
                ops += self.play_tone(tone, duration_tone)
            # change color of LED?
            if round(duration_led, 2) >= round(duration_bar, 2):
                ops += self.change_color(led_sequence[pos_color])
                pos_color += 1
                pos_color %= len(led_sequence)
                duration_led %= duration_bar
            duration_total += duration_tone
            duration_led += duration_tone
        ops += ev3.opSound_Ready
        ops += self.change_color(ev3.LED_GREEN)
        return ops

class Song(task.Repeated):
    """
    task, that plays a song, using sound and LED
    """
    def __init__(self, jukebox: Jukebox, song: dict):
        super().__init__(self._next_tone)
        self._song = song
        self._pos_tone = 0
        self._jukebox = jukebox
        self._pos_led = 0
        self._task_led = task.Periodic(
            60 * song["beats_per_bar"] / song["tempo"],
            self._next_color
        )
        self.append(
            task.Task(jukebox.stop_sound)
        ).append(
            task.Task(self._task_led.stop)
        ).append(
            task.Task(
                jukebox.change_color,
                args=(ev3.LED_GREEN,)
            )
        )

    def _next_color(self) -> bool:
        self._jukebox.change_color(self._song["led_sequence"][self._pos_led])
        self._pos_led += 1
        self._pos_led %= len(self._song["led_sequence"])
        return True

    def _next_tone(self) -> numbers.Number:
        if self._pos_tone == len(self._song["tones"]):
            return -1
        tone, beats = self._song["tones"][self._pos_tone]
        if self._pos_tone > 0 or tone !="p":
            self._jukebox.play_tone(tone, 0)
        self._pos_tone += 1
        return 60 * beats / self._song["tempo"]

    def stop(self):
        """
        stops playing of the song
        """
        super().stop()
        self._jukebox.stop_sound()
        self._task_led.stop()
        self._jukebox.change_color(ev3.LED_GREEN)

    def start(self):
        """
        starts playing of the song
        """
        self._pos_tone = 0
        self._pos_led = 0
        super().start()

    def cont(self):
        """
        continues sound and changing of led colors
        """
        time_event_tone = self.time_event
        time_event_led = self._task_led.time_event
        if time_event_tone > time_event_led:
            gap = time_event_tone - time_event_led
            self._task_led.cont()
            super().cont(gap=gap)
        else:
            gap = time_event_led - time_event_tone
            self._task_led.cont(gap=gap)
            super().cont()

    def _execute(self):
        if not self._task_led.started:
            self._task_led.start()
        super()._execute()

if __name__ == "__main__":
    my_jukebox = Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
    my_jukebox.verbosity = 1

    my_songs = my_jukebox.song(HAPPY_BIRTHDAY).append(
        task.Task(
            time.sleep,
            args=(1,)
        )
    ).append(
        my_jukebox.song(ALLE_MEINE_ENTCHEN)
    )
    my_songs.start()
    time.sleep(5)
    my_songs.stop()
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** stopped ***")
    time.sleep(3)
    my_songs.cont()
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** continued ***")
    time.sleep(14)
    my_jukebox.volume=12
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 12 ***")
    time.sleep(5)
    my_jukebox.volume=1
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')
    print(now, "*** volume 1 ***")
