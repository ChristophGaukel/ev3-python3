=================
API documentation
=================

.. automodule:: ev3_dc


Static methods
--------------

LCX
~~~

Translates an integer into a direct command compatible number with
identification byte. It is used for input arguments of operations,
which are not read from global or local memory. Dependent from the
value an LCX will be a byte string of one, two, three or 5 bytes
length.

.. autofunction:: ev3_dc.LCX

LCS
~~~

Adds a leading identification byte and an ending zero terminator
to an ascii string and returns a byte string.

.. autofunction:: ev3_dc.LCS

LVX
~~~

Translates a local memory adress into a direct command compatible
format with identification byte. This can be used for input or output
arguments of operations.

.. autofunction:: ev3_dc.LVX

GVX
~~~

Translates a global memory adress into a direct command compatible
format with identification byte. This can be used for input or output
arguments of operations.

.. autofunction:: ev3_dc.GVX

port_motor_input
~~~~~~~~~~~~~~~~

Allows to use well known motor ports of output commands for input commands too.

.. autofunction:: ev3_dc.port_motor_input
      

pid
~~~

pid is a `PID controller
<https://en.wikipedia.org/wiki/PID_controller>`_. It continuously
adjusts a system by periodically calculating a signal value from a
measured variable. Function ``pid()`` does the setup and returns the
controller, which is a function (with this signature: ``signal(value:
float) -> float``).

.. autofunction:: ev3_dc.pid


Classes
-------

EV3
~~~

EV3 establishes a connection between your computer and the EV3
device. It allows to send direct and system commands and receive their
replies.

.. autoclass:: ev3_dc.EV3
   :members:
      

Touch
~~~~~

Touch is a subclass of EV3 and allows to read data from a touch
sensor, which may be an EV3-Touch or a NXT-Touch.

.. autoclass:: ev3_dc.Touch
   :members:
      

Infrared
~~~~~~~~

Infrared is a subclass of EV3 and allows to read data from an infrared
sensor. It uses three modes of the infrared sensor:

  - *proximity* mode, which measures the distance between the
    sensor an a surface in front of the sensor.
  - *seeker* mode, which measures the position (heading and distance) of
    up to four beacons.
  - *remode* mode, which reads the currently pressed buttons of up to
    four beacons.

.. autoclass:: ev3_dc.Infrared
   :members:
      

Ultrasonic
~~~~~~~~~~

Ultrasonic is a subclass of EV3 and allows to read data from an
ultrasonic sensor, which may be an EV3-Ultrasonic or a
NXT-Ultrasonic. It uses mode *EV3-Ultrasonic-Cm*
(resp. NXT-Ultrasonic-Cm).

.. autoclass:: ev3_dc.Ultrasonic
   :members:
      

Color
~~~~~

Color is a subclass of EV3 and allows to read data from a
color sensor, which may be an EV3-Color or a
NXT-Color. It uses modes *EV3-Color-Reflected*, 
(resp. *NXT-Color-Reflected*).

.. autoclass:: ev3_dc.Color
   :members:
      

Gyro
~~~~

Gyro is a subclass of EV3 and allows to read data from a
gyro sensor (EV3-Gyro). It uses mode *EV3-Gyro-Angle*.

.. autoclass:: ev3_dc.Gyro
   :members:


Sound
~~~~~

Sound is a subclass of EV3 and provides higher order methods for
the EV3 sound.

.. autoclass:: ev3_dc.Sound
   :members:


Jukebox
~~~~~~~

Jukebox is a subclass of Sound and provides higher order methods for
tones and LEDs.

.. autoclass:: ev3_dc.Jukebox
   :members:


Voice
~~~~~

Voice is a subclass of Sound and provides higher order methods for
speaking. It supports `text to speech
<https://en.wikipedia.org/wiki/Speech_synthesis>`_ and calls `gTTS
<https://gtts.readthedocs.io/en/latest/index.html>`_, which needs an
internet connection. *Voice* allows to select the language, the top
level domain and a slower reading speed by supporting *gTTS*'s
attributes *lang*, *tld* and *slow*.

*gTTS* answers with mp3 data, therefore *Voice* calls `ffmpeg
<https://ffmpeg.org/>`_ to convert mp3 to pcm. If *ffmpeg* is not
installed on your system, *Voice* will not work.

.. autoclass:: ev3_dc.Voice
   :members:
      

Motor
~~~~~

Motor is a subclass of EV3 and provides higher order methods for motor
movements.

.. autoclass:: ev3_dc.Motor
   :members:
      

TwoWheelVehicle
~~~~~~~~~~~~~~~

TwoWheelVehicle is a subclass of EV3 and provides higher order methods
for moving or driving a vehicle with two drived wheels. It tracks the
position of the vehicle.

.. autoclass:: ev3_dc.TwoWheelVehicle
   :members:
      

FileSystem
~~~~~~~~~~

FileSystem is a subclass of EV3 and provides higher order methods for
the filesystem of an EV3 device. It allows to read and write EV3's
files or directories.

.. autoclass:: ev3_dc.FileSystem
   :members:
