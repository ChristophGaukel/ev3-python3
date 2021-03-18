-------
Jukebox
-------

:py:class:`~ev3_dc.Jukebox` is a subclass of :py:class:`~ev3_dc.EV3`.
You can use it to play tones or to change the LED color without
internal knowledge of direct commands.

But Jukebox is more than that. It combines direct commands with
`thread_task <https://thread-task.readthedocs.io/en/latest>`_. This
allows to use sounds and light effects parallel to other activities.


Change Color
~~~~~~~~~~~~

Instead of coding a direct command, like we do in
:ref:`changing_led_colors_label`, you can do the same thing a bit more
comfortable.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  
  jukebox.change_color(ev3.LED_RED_FLASH)
  
  sleep(5)
  
  jukebox.change_color(ev3.LED_GREEN)

For five seconds, the LED will flah red, then it will become green
again. Calling method :py:meth:`~ev3_dc.Jukebox.change_color` hides
the technical details behind a more user friendly API. We set the
verbosity because we like to see the communication between our program
an the EV3 brick. The output:

.. code-block:: none

  13:09:05.718859 Sent 0x|08:00|2A:00|80|00:00|82:1B:05|
  13:09:10.724762 Sent 0x|08:00|2B:00|80|00:00|82:1B:01|

Obviously, :py:class:`~ev3_dc.Jukebox` sends direct commands.


Play Tone
~~~~~~~~~

Sound is the other competence of class
:py:class:`~ev3_dc.Jukebox`. Method
:py:meth:`~ev3_dc.Jukebox.play_tone` allows to play tones 
like *c*, *d*, *e* or *c'*, *d'*, *e'* without
knowing the frequencies.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program

.. code:: python3

  import ev3_dc as ev3
  
  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  
  jukebox.play_tone("f'''", duration=1, volume=100)

This plays f³ for one second at maximum volume (f³ is the highest tone
of Mozart's *Queen of the night aria*). If no duration is given,
METHOD play_tone plays the tone unlimited. If no volume is given it
takes the volume, which can be set as a property of class Jukebox and
is 1 by default.

The output:

.. code-block:: none

  13:13:49.071839 Sent 0x|0F:00|2A:00|80|00:00|94:01:81:64:82:75:05:82:E8:03|


Play Sound
~~~~~~~~~~

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  
  jukebox.play_sound(
      './ui/DownloadSucces',
      volume=100,
      repeat=True
  )
  
  sleep(5)
  
  jukebox.stop_sound()

Some remarks:

  - The program plays a sound file repeatedly and stops the sound after 5 sec. This is
    exactly, what program :ref:`playing_sound_files_repeatedly_label` does.
  - It needs another direct command to stop the playing.

The output:

.. code-block:: none

  13:45:30.663648 Sent 0x|1E:00|2A:00|80|00:00|94:03:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  13:45:35.669587 Sent 0x|07:00|2B:00|80|00:00|94:00|


Sound as a Thread Task
~~~~~~~~~~~~~~~~~~~~~~

`thread_task <https://thread-task.readthedocs.io/en/latest>`_ objects allow
to do the timing inside and they allow to do multiple things
parallel.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  
  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  
  t_sound = jukebox.sound(
      './ui/DownloadSucces',
      volume=100,
      duration=5,
      repeat=True
  )
  
  t_sound.start()

Some remarks:

  - method :py:meth:`~ev3_dc.Jukebox.sound` returns a thread task object, we name it *t_sound*.
  - *t_sound* can be started, stopped, continued and restarted. We only start it.
  - *t_sound* runs in the background. If you add some more commands to this program, you will
    see, they are executed parallel to *t_sound*.

The output:

.. code-block:: none

  14:06:40.170520 Sent 0x|1E:00|2A:00|80|00:00|94:03:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  14:06:45.170841 Sent 0x|07:00|2B:00|80|00:00|94:00|



Playing the EU-Antemn
~~~~~~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99') as jukebox:
      jukebox.song(ev3.EU_ANTEMN).start()

Some remarks:

  - Method :py:meth:`~ev3_dc.Jukebox.song` returns a `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    object, which can be started, stopped and continued. It plays
    tones and changes the LED-colors.
  - Starting the thread task does not block the program nor does it
    block the EV3 brick. It runs in the background and allows to do
    additional things parallel.

EU_ANTEMN is a dictionary:

.. code-block:: none

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

  ...

          ("g'", 1.5),
          ("f'", .5),
          ("f'", 1)
      )
  }

Some remarks:

  - *tempo* is beats per minute.
  - *led_sequence* is the color sequence, which changes per bar.
  - *tones* are the tones to play, the duration is not in seconds, but
    in beats.


Combine Happy Birthday with the Triad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Sleep

  with ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99') as jukebox:
      (
          jukebox.song(ev3.TRIAD) +
          Sleep(1) +
          jukebox.song(ev3.HAPPY_BIRTHDAY) +
          Sleep(1) +
          jukebox.song(ev3.TRIAD)
      ).start()
      
The program builds a chain of tasks, which also is a `thread_task
<https://thread-task.readthedocs.io/en/latest>`_ object. It
demonstrates how to build tasks of growing complexity, which still
keep their simple public API.


Singing Canon with an EV3 brick
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Repeated
  
  with ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99') as jukebox:
      Repeated(
          jukebox.song(ev3.FRERE_JACQUES),
          num=3
      ).start()
    
Class `Repeated
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#repeated>`_
plays the canon three times.



