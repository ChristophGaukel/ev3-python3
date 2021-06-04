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

Instead of coding a direct command, like we did in
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

Playing tones is the other competence of class
:py:class:`~ev3_dc.Jukebox`. Different from method
:py:meth:`~ev3_dc.Sound.tone` of class :py:class:`~ev3_dc.Sound`,
these tones are defined by their musical names and not by their
frequencies. Method :py:meth:`~ev3_dc.Jukebox.play_tone` allows to
name them *c*, *d*, *e*, *c'*, *d'* or *e'*. One does not need to know
their frequencies.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program

.. code:: python3

  import ev3_dc as ev3
  
  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  
  jukebox.play_tone("f'''", duration=1, volume=100)

This plays f³ for one second at maximum volume (f³ is the highest tone
of Mozart's *Queen of the night aria*). If no duration is given,
method :py:meth:`~ev3_dc.Jukebos.play_tone` plays the tone
unlimited. If no volume is given, it takes the volume, which was set as
an optional argument of class Jukebox's creation. If neither was set,
it takes the volume from the device.

The output:

.. code-block:: none

  13:13:49.071839 Sent 0x|0F:00|2A:00|80|00:00|94:01:81:64:82:75:05:82:E8:03|



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



