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
which are not red from global or local memory. Dependent from the
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


Classes
-------

EV3
~~~~

EV3 establishes a connection between your computer and the EV3
device. It allows to send direct and system commands and receive their
replies.

.. autoclass:: ev3_dc.EV3
   :members:


Jukebox
~~~~~~~

Jukebox is a subclass of EV3 and provides higher order methods for
sound and LEDs.

.. autoclass:: ev3_dc.Jukebox
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
      

PID
~~~

PID is a `PID controller
<https://en.wikipedia.org/wiki/PID_controller>`_. It continuously
adjusts a system by calculating an error value as the difference
between a desired setpoint and a measured variable.

.. autoclass:: ev3_dc.PID
   :members:
