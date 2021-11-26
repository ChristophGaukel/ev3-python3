ev3-python3
=============

Use python3 to program your LEGO Mindstorms EV3. The program runs on
the local host and sends direct commands to the EV3 device. It
communicates via Bluetooth, WiFi or USB. There is no need to boot the
EV3 device from an SD Card or manipulate its software. You can use it
as it is, the EV3 is designed to execute commands which come from
outside. If you prefer coding from scratch, read this `blog
<http://ev3directcommands.blogspot.com>`_, if you like to benefit from
preliminary work, then use module ``ev3_dc``.

Installation
------------

::

  python3 -m pip install --user ev3_dc

Examples
--------


Writing and sending direct commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following program communicates via USB with an EV3 device and
plays a tone with a frequency of 440 Hz for a duration of 1 sec. This
says, you need to connect the EV3 device and your computer with an USB
cable.

::

  import ev3_dc as ev3

  my_ev3 = ev3.EV3(protocol=ev3.USB)
  my_ev3.verbosity = 1
  ops = b''.join((
      ev3.opSound,
      ev3.TONE,
      ev3.LCX(1),  # VOLUME
      ev3.LCX(440),  # FREQUENCY
      ev3.LCX(1000),  # DURATION
  ))
  my_ev3.send_direct_cmd(ops)

The output shows the request, which was sent to the EV3 device and the
corresponding response::

  13:02:23.425843 Sent 0x|0E:00|2A:00|00|00:00|94:01:01:82:B8:01:82:E8:03|
  13:02:23.432733 Recv 0x|03:00|2A:00|02|

Subclasses of EV3 with specialized APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method **play_tone** of class **Jukebox** also plays tones:

::

  import ev3_dc as ev3

  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  jukebox.play_tone("a'", duration=1)

This program does the very same thing via Bluetooth! Before you can
run it, you need to pair the two devices (the computer, that
executes the program and the EV3 device) and replace the MAC-address
``00:16:53:42:2B:99`` by the one of your EV3. The output::

  13:05:11.324701 Sent 0x|0E:00|2A:00|80|00:00|94:01:01:82:B8:01:82:E8:03|

Some remarks:
  - Protocol ``USB`` replies all requests to provide
    collisions. Protocol ``BLUETOOTH`` is much slower and replies only
    requests, which demand it.
  - Module ``ev3_dc`` provides objects with specialized
    functionality. Behind the scene, this functionality depends on
    messages, which are sent to the EV3 device and replied by the EV3
    device.


Independent Tasks
~~~~~~~~~~~~~~~~~

Specialized classes (e.g. class `Jukebox
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#jukebox>`_)
provide factory methods, which return `thread_task.Task
<https://thread_task.readthedocs.io/en/latest/>`_ objects. Thread
tasks allow to start, stop and continue independent tasks.

::

  import ev3_dc as ev3

  jukebox = ev3.Jukebox(protocol=ev3.WIFI)
  antemn = jukebox.song(ev3.EU_ANTEMN)

  antemn.start()

This program plays the EU antemn. Before you can execute it, you need
to connect both devices (the computer, that runs the program and the
EV3 device) with the same LAN (local area network), the EV3 device
must be connected via WiFi. If you don't own a WiFi dongle, modify the
protocol and select ev3.BLUETOOTH or ev3.USB.

Some remarks:
  - Method ``song()`` returns a thread_task.Task object and we need to
    start it explicitly. It plays tones and changes the LED-colors.
  - Starting a thread task does not block the program nor does it
    block the EV3 device. It runs in the background and allows to do
    additional things parallel.
  - Alternatively, you can start a thread task without mutlithreading
    by ``antemn.start(thread=False)``. This lets it behave like any
    normal callable.


Specialized Subclasses handle Sensors and Motors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specialized subclasses of class `EV3
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#ev3>`_,
like `Touch
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#touch>`_,
`Infrared
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#infrared>`_,
`Ultrasonic
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#ultrasonic>`_,
`Color
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#color>`_,
`Motor
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#motor>`_,
`TwoWheelVehicle
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#twowheelvehicle>`_,
`Sound
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#sound>`_
or `Voice
<https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#voice>`_
handle sensors, motors, sound or text to speech. You can use multiple
of these objects parallel and all of them can share a single physical
EV3 device. You can also build complex robots with more than one EV3
device and control these robots easily by a single python program.

::

  import ev3_dc as ev3
  
  with ev3.Touch(ev3.PORT_1, protocol=ev3.USB) as touch_1:
      touch_4 = ev3.Touch(ev3.PORT_4, ev3_obj=touch_1)
      voice = ev3.Voice(ev3_obj=touch_1, volume=100)
      
      touched_1 = touch_1.touched
      touched_4 = touch_4.touched
      if touched_1 and touched_4:
          txt = 'both sensors are touched'
      elif touched_1:
          txt = 'only sensor 1 is touched'
      elif touched_4:
          txt = 'only sensor 4 is touched'
      else:
          txt = 'none of the sensors is touched'
  
      voice.speak(txt).start(thread=False)
  
Some remarks:
  - You need to connect two touch sensors, one at port 1, the
    other at port 4 and you need to connect your EV3 device and
    your computer with an USB cable.
  - Class `EV3
    <https://ev3-dc.readthedocs.io/en/latest/api_documentation.html#ev3>`_
    and all its subclasses support the with statement.
  - touch_4 and voice use the connection of touch_1. This is done by setting
    keyword argument ``ev3_obj=touch_1``.
  - If you have more than a single EV3 device connected via USB, this
    program will fail. To handle this special case identify the device
    by using keyword argument host, e.g. ``ev3.Touch(ev3.PORT_1,
    protocol=ev3.USB, host='00:16:53:42:2B:99')``. For protocol
    BLUETOOTH keyword argument host is mandatory.
  - Method ``speak()`` returns a thread_task.Task object, which we
    start threadless.
  - This program depends on the tool `ffmpeg <https://ffmpeg.org/>`_
    and you need to have it installed on your computer.

Read `ev3-dc.readthedocs.io
<https://ev3_dc.readthedocs.io/en/latest/>`_ for more details.
