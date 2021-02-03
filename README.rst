ev3-python3
=============

Use python3 to program your LEGO Mindstorms EV3. The program runs on the local host
and sends direct commands to the EV3 device. It communicates via bluetooth, wifi or USB.
I wrote a `blog <http://ev3directcommands.blogspot.com>`_ about this code.

There is no need to boot the EV3 device from a SD Card or manipulate
its software. You can use it as it is, the EV3 is designed to execute
commands which come from outside.

Installation
------------

::

  python3 -m pip install --user ev3_dc

Examples
--------


Writing and sending direct commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This program communicates via USB with an EV3 device (mac-address:
'00:16:53:42:2B:99', replace it by the the mac-address of your EV3)
and plays a tone with a frequency of 440 Hz for a duration of 1 sec.

::

  import ev3_dc as ev3

  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  ops = b''.join((
      ev3.opSound,
      ev3.TONE,
      ev3.LCX(1),  # VOLUME
      ev3.LCX(440),  # FREQUENCY
      ev3.LCX(1000),  # DURATION
  ))
  my_ev3.send_direct_cmd(ops)

The output shows the direct command, which was sent to the EV3 device::

  11:48:31.188008 Sent 0x|0E:00|2A:00|80|00:00|94:01:01:82:B8:01:82:E8:03|

Subclasses of EV3 with comfortable APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method **play_tone** of class **Jukebox** also plays tones:

::

  import ev3_dc as ev3

  jukebox = ev3.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  jukebox.verbosity = 1
  jukebox.play_tone("a'", duration=1)

This program does the very same thing via bluetooth! Before you can
run it, you need to pair the two devices (the computer, that
executes the program and the EV3 brick). The output::

  11:55:11.324701 Sent 0x|0E:00|2A:00|80|00:00|94:01:01:82:B8:01:82:E8:03|


Independent Tasks
~~~~~~~~~~~~~~~~~

Specialized classes (e.g. class **Jukebox**) provide factory methods,
that return thread tasks. Thread tasks allow to start, stop and
continue independent tasks.

::

  import ev3_dc as ev3

  jukebox = ev3.Jukebox(protocol=ev3.WIFI, host='00:16:53:42:2B:99')
  antemn = jukebox.song(ev3.EU_ANTEMN)

  antemn.start()

This program plays the EU antemn. Before you can execute it, you need
to connect both devices (the computer, that runs the program and the
EV3 brick) with the same LAN (local area network), the EV3 brick must
be connected via wifi. If you don't own a wifi dongle, modify the
protocol and select ev3.BLUETOOTH or ev3.USB.

Some remarks:
  - Method song() returns a `thread_task
    <https://thread_task.readthedocs.io/en/latest/>`_ object, which
    can be started, stopped and continued. It plays tones and changes
    the LED-colors.
  - Starting the thread task does not block the program nor does it
    block the EV3 brick. It runs in the background and allows to do
    additional things parallel.

Read `ev3_dc.readthedocs.io
<https://ev3_dc.readthedocs.io/en/latest/>`_ for more details.
