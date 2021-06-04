#####
Sound
#####

:py:class:`~ev3_dc.Sound` is a subclass of :py:class:`~ev3_dc.FileSystem`.
It provides higher order methods to play tones and sound files.


+++++++++++
Play a Tone
+++++++++++

Method :py:meth:`~ev3_dc.Sound.tone` of class
:py:class:`~ev3_dc.Sound` plays tones with given frequencies. Connect
your EV3 brick and your computer with an USB cable, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Sound(protocol=ev3.USB) as sound:
      sound.verbosity = 1
      sound.tone(250, duration=1, volume=100)
  
This plays a tone with frequency 250 Hz for one second at maximum
volume. If no duration is given, method :py:meth:`~ev3_dc.Sound.tone`
plays the tone unlimited. If no volume is given it takes the volume,
which can be set as a property of class Sound. If neither was set, it
takes the volume from the EV3 device. The frequency must be in a range
of 250 - 10.000 Hz, the volume must be in a range of 1 - 100.

The output:

.. code-block:: none

  13:01:25.162280 Sent 0x|0F:00|2B:00|00|00:00|94:01:81:64:82:FA:00:82:E8:03|
  13:01:25.168008 Recv 0x|03:00|2B:00|02|


+++++++++++++++++
Play a Sound File
+++++++++++++++++

Robot sound files are a special `pulse code modulation
<https://en.wikipedia.org/wiki/Pulse-code_modulation>`_ format for
audio signals. The single channel signal has a sample rate of 8 kHz
and an 8 bit resolution. This `blog
<https://tiebing.blogspot.com/2019/09/lego-ev3-sound-file-rsf-format.html>`_
describes, how to add the header information and create robot sound
files. Some sound files can be found on the EV3 device. Method
:py:meth:`~ev3_dc.Sound.play_sound` allows to play these sound files.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  hugo = ev3.Sound(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99', volume=100)
  hugo.verbosity = 1
  
  hugo.play_sound(
      './ui/DownloadSucces.rsf',
      repeat=True
  )
  
  sleep(5)
  
  hugo.stop_sound()

Some remarks:

  - The program plays a sound file repeatedly and stops the sound after 5 sec. This is
    exactly, what program :ref:`playing_sound_files_repeatedly_label` does.
  - The timing is done by the program.
  - It needs to call method :py:meth:`~ev3_dc.Sound.stop_sound` to
    stop the playing, otherwise it would last forever.

The output:

.. code-block:: none

  13:45:30.663648 Sent 0x|1E:00|2A:00|80|00:00|94:03:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  13:45:35.669587 Sent 0x|07:00|2B:00|80|00:00|94:00|


++++++++++++++++++++++++++++++++++
Play a Sound File as a Thread Task
++++++++++++++++++++++++++++++++++

`thread_task <https://thread-task.readthedocs.io/en/latest>`_ objects
allow to define the timing beforehand, when the thread task is
created. Starting thread tasks allows to do multiple things parallel.

Connect your EV3 brick and your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  
  hugo = ev3.Sound(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99', volume=100)
  hugo.verbosity = 1
  
  t_sound = hugo.sound(
      './ui/DownloadSucces.rsf',
      duration=5,
      repeat=True
  )
  
  t_sound.start()

Some remarks:

  - method :py:meth:`~ev3_dc.Sound.sound` returns a thread task object, we name it *t_sound*.
  - *t_sound* can be started, stopped, continued and restarted. We only start it.
  - *t_sound* runs in the background. If you add some more commands to this program, you will
    realize, they are executed parallel to *t_sound*.
  - the timing is done inside the thread task object.
  - stopping the sound also is done by the task object.
  - thread task objects encapsulate program logik behind a simple public API.

The output:

.. code-block:: none

  14:06:40.170520 Sent 0x|1E:00|2A:00|80|00:00|94:03:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  14:06:45.170841 Sent 0x|07:00|2B:00|80|00:00|94:00|


+++++++++++++++++++++++
Play a local Sound File
+++++++++++++++++++++++

If you combine method :py:meth:`~ev3_dc.FileSystem.load_file` from
class :py:meth:`~ev3_dc.FileSystem` with the above described
functionality, you can also play local sound files.

Find the location of LEGO’s sound files, which in my case was:
.../Program Files (x86)/LEGO Software/LEGO MINDSTORMS EV3 Home
Edition/Resources/BrickResources/Retail/Sounds/files (I copied this directory to
a location with a shorter path). Modify
the program by replacing the file location. Take an USB cable and
connect your EV3 brick with your computer then start the following
program.

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Sound(protocol=ev3.USB, volume=20) as hugo:
      hugo.sound(
          '../Sound/Expressions/Laughing 2.rsf',
          local=True
      ).start(thread=False)
  print('all done')

Some remarks:

  - keyword argument *local* makes the distinction between local sound
    files and sound files on the EV3 device. In this case, the sound
    file exists in the file system of the machine, which runs the
    program and the relative path is from the directory, where this
    python program is located.
  - Starting a Thread Task with *thread=False* lets it behave
    traditional, it does its actions and your program continues with
    execution, when they are done.

 
