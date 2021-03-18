----------
Ultrasonic
----------

Class :py:class:`~ev3_dc.Ultrasonic` is a subclass of
:py:class:`~ev3_dc.EV3`. You can use it to read values from a single
ultrasonic sensor without any knowledge of direct command syntax.

The ultrasonic sensor sends and receives ultrasonic sound signals. It
is able to calculate distances by analyzing reflected sound. This is a
subset of the infrared sensors functionality,

The ultrasonic sensor returns a distance of 2.55 m, when it does not
detect anything. Class *Ultrasonic* replaces this by value *None*.

If you like to use multiple ultrasonic sensors simultaneously, you can
create more than one instance of this class.


Asking for the distance from a surface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Ultrasonic` has an attribute
:py:attr:`~ev3_dc.Ultrasonic.distance`, which is of type float and
tells, if the the sensor currently *sees* some surface in front and in
a distance closer than 2.55 m.

Take an USB cable and connect your EV3 device with your
computer. Replace MAC-address ``00:16:53:42:2B:99`` by the one of your
EV3 brick, connect an ultrasonic sensor (it may be of type
ev3.NXT_ULTRASONIC or ev3.EV3_ULTRASONIC) with PORT 3, then start this
program:

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  my_ultrasonic = ev3.Ultrasonic(
          ev3.PORT_3,
          protocol=ev3.USB,
          host='00:16:53:42:2B:99'
  )
  
  while True:
      dist = my_ultrasonic.distance
      if dist:
          break
      sleep(0.1)
  
  print(f'something seen {dist:3.2f} m ahead')
    
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or WiFi.
  - Run the program multiple times with different surfaces and distances.
  - Test what happens, when no sensor is connected to PORT 2.
  - Test what happens, when another sensor type is connected to PORT 2.
  - Test for the maximum distance and determine if this depends on the
    surface material.
  - Every reference of property *distance* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Ultrasonic.verbosity` to value 1 and you will see
    the communication data.
