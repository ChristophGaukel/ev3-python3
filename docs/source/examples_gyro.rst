####
Gyro
####

Class :py:class:`~ev3_dc.Gyro` is a subclass of
:py:class:`~ev3_dc.EV3`. You can use it to read values from a single
LEGO gyro sensor (a `gyroscope
<https://en.wikipedia.org/wiki/Gyroscope>`_) without any knowledge of
direct command syntax.

The gyro sensor is used to measure one-dimensional orientation and
angular velocity. These attributes allow to get the measurements:

  - :py:attr:`~ev3_dc.Gyro.angle` measures the current orientation as
    an angle, which is an integer representing the sensor's clockwise
    rotation.
  - :py:attr:`~ev3_dc.Gyro.rate` is an integer, representing the
    sensor's clockwise rotation rate (or `angular velocity
    <https://en.wikipedia.org/wiki/Angular_velocity>`_) in degree per
    second.
  - :py:attr:`~ev3_dc.Gyro.state` holds both, the current angle and
    the current rotation rate. It is of type *GyroState*.

If you like to use multiple gyro sensors simultaneously (e.g. to
receive rotations along multiple axes), you can create more than one
instance of this class.

++++++++++++++++++++++++++++++++++++++++
Asking for the current orientation angle
++++++++++++++++++++++++++++++++++++++++

Choose settings (protocol and host) to connect the EV3 to your
computer.  Replace the settings in the program below, connect a gyro
sensor to PORT_1, run this program and rotate the gyro sensor:

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  settings = {"protocol":ev3.BLUETOOTH, "host":"00:16:53:81:D7:E2"}
  with ev3.Gyro(ev3.PORT_1, **settings) as gyro:
      while True:
          current_angle = gyro.angle
          print(f"\rThe current angle is {current_angle:4d} °", end='')
          if current_angle >= 360:
              print("\n" + "The sensor made a full clockwise turn!")
              break
          elif current_angle <= -360:
              print("\n" + "The sensor made a full counterclockwise turn!")
              break
          sleep(0.05)
      
Some remarks:
  - Mathematically, clockwise rotation is measured with negative
    values, counterclockwise rotation with positive ones. LEGO's gyro
    sensor does not follow this convention! If you face the the red
    icon on its top, then clockwise rotation measures positive.
  - In the moment, when class :py:class:`~ev3_dc.Gyro` is initiated,
    the sensor's current rotation angle becomes value zero.
  - What a LEGO gyro sensor measures is not really
    orientation. Instead it measures the orientation angle between an
    original orientation and the current one. If the sensor made
    multiple full rotations, then *angle* will correctly show
    it. Modify the program and break the loop when at least 2 full
    turns have been made.
  - Every reference of property *angle* starts a new communication
    between the program and the EV3 device.
  - Method :py:meth:`~ev3_dc.Gyro.reset` allows to reset the zero
    position at any other time or to set the current angle to any
    other value.
  - Printing '\\r' (carriage return) returns to the beginning of the
    current line. This allows to print the same line again and again.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Gyro.verbosity` to value 1 and you will see the
    communication data. This will show you, that the measurements
    use mode 3, which is *EV3-Gyro-Rate & Angle* and get angle and rate
    as results.

++++++++++++++++++++++++++++++++++++
Asking for the current rotation rate
++++++++++++++++++++++++++++++++++++

Connect your EV3 device and your computer via USB cable, connect a
gyro sensor to PORT_1, then run this program and rotate the gyro sensor:

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Gyro(ev3.PORT_1, protocol=ev3.USB) as gyro:
      min_rate, max_rate = 0, 0
      print('for 10 sec. do some rotation movements')
      for i in range(100):
          cur_rate = gyro.rate
          min_rate = min(min_rate, cur_rate)
          max_rate = max(max_rate, cur_rate)
          sleep(0.1)
  print(f'max. rate: {max_rate} °/s, min. rate: {min_rate} °/s')
        
Some remarks:
  - Every reference of property *rate* starts a new communication
    between the program and the EV3 device. This is why we use
    variable *cur_rate* (current rate) to hold the values.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Gyro.verbosity` to value 1 and you will see
    the communication data.


+++++++++++++++++++++++++++++++++++++++++++++
Asking for the current state (angle and rate)
+++++++++++++++++++++++++++++++++++++++++++++

Connect your EV3 device and your computer via USB cable, connect a
gyro sensor to PORT_1, then run this program and rotate the gyro sensor:

.. code:: python3

  import time import sleep
  import ev3_dc as ev3
  
  with ev3.Gyro(ev3.PORT_1, protocol=ev3.USB) as gyro:
      cs = gyro.state
      print(f'angle: {cs.angle:4d} °, rate: {cs.rate:4d} °/s', end='')
      for i in range(10):
          sleep(1)
          cs = gyro.state
          print('\r' + f'angle: {cs.angle:4d} °, rate: {cs.rate:4d} °/s', end='')
      print()
      
Some remarks:
  - Every reference of property *state* starts a new communication
    between the program and the EV3 device. This is why we use
    variable *cs* (current state) to hold the values.
  - Porperty *state* is of type *GyroState*, which has two attributes:
    *angle* and *rate*.
  - Printing '\\r' (carriage return) returns to the beginning of the
    current line. This allows to print the same line again and again.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Gyro.verbosity` to value 1 and you will see
    the communication data.


++++++++++++++++++++++++++++++
Reset the original orientation
++++++++++++++++++++++++++++++

Sometimes the orientation in the moment of class initialization is not
the best point of reference. E.g. an algorithm for a balancing device
is clearer coded, when the perfect balance becomes the point of
reference. Method :py:meth:`~ev3_dc.Gyro.reset` allows to do exactly
that.

Connect your EV3 device and your computer via USB cable, connect a
gyro sensor to PORT_1, then run this program and don't rotate the gyro
sensor:

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Gyro(ev3.PORT_1, protocol = ev3.USB) as gyro:
          print(f"The current angle is {gyro.angle} °")
          sleep(5)
  
          gyro.reset(angle=90)
          print(f"After resetting: The current angle is {gyro.angle} °")
          sleep(5)
  
          gyro.reset(angle=180)
          print(f"After another resetting: The current angle is {gyro.angle} °")
          sleep(5)
  
          gyro.reset()
          print(f"After resetting again: The current angle is {gyro.angle} °")

The output:

.. code:: none

  The current angle is 0 °
  After resetting: The current angle is 90 °
  After another resetting: The current angle is 180 °
  After resetting again: The current angle is 0 °

Some remarks:
  - Run the program again and do some rotation movements of the sensor
    while the sleeping. You will see the very same output, why?
  - Modify the program and do the sleeping between the resets and the
    measurements. Then start the program again and do some rotation movements
    of the sensor.

