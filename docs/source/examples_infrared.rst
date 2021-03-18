--------
Infrared
--------

Class :py:class:`~ev3_dc.Infrared` is a subclass of
:py:class:`~ev3_dc.EV3`. You can use it to read values from a single
infrared sensor without any knowledge of direct command syntax.

The infrared sensor sends and receives infrared light signals. It is
able to calculate distances by analyzing reflected light. It also is
able to communicate with the EV3 beacon device. This allows to
determine the current position of the beacon and it allows to use the
bacon as a remote control.

To use multiple infrared sensors simultaneously, you can create
multiple instances of this class.


Asking for the distance from a surface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Infrared` has an attribute
:py:attr:`~ev3_dc.Infrared.distance`, which is of type float and
tells, if the the sensor currently *sees* some surface in front of the
sensor and in a distance closer than 1.00 m.

Connect your EV3 device with your local network via Wifi.  Replace the
MAC-address by the one of your EV3 brick, connect an infrared sensor
with PORT 2, then start this program.

.. code:: python3

  import ev3_dc as ev3
  
  my_infrared = ev3.Infrared(
          ev3.PORT_2,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )

  dist = my_infrared.distance
  if dist:
      print(f'distance: {my_infrared.distance:3.2f} m')
  else:
      print('seen nothing')
  
  
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or USB.
  - Run the program multiple times with different surfaces and distances.
  - Test what happens, when no sensor is connected to PORT 2.
  - Test what happens, when another sensor type is connected to PORT 2.
  - Test with distances larger than 1.00 m.
  - Every time, you refrence attribute
    :py:attr:`~ev3_dc.Infrared.distance`, you again start a
    communication between your program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Infrared.verbosity` to value 1 and you will see
    the communication data.


Asking for a beacon's position
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Infrared` has an attribute
:py:attr:`~ev3_dc.Infrared.beacon`, which returns a named tuple of
type *Beacon*. It tells, if the sensor currently *sees* an active
beacon, which is sending on the requested channel.

Connect your EV3 device with your local network via Wifi. Replace the
MAC-address by the one of your EV3 brick. Connect an infrared sensor
with PORT 2, place a beacon somewhere in front of the sensor, select
channel 3 and switch on the beacon, then start this program.

.. code:: python3

  import ev3_dc as ev3
  
  my_infrared = ev3.Infrared(
          ev3.PORT_2,
          channel=3,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )
  
  print(my_infrared)
  print(f'beacon on channel {my_infrared.channel}: {my_infrared.beacon}')
  
Some remarks:

  - If you prefer protocols Bluetooth or USB, you know how to change
    the program.
  - The named tuple *Beacon* has two items, *heading* and *distance*,
    where *heading* is between -25 and 25, and *distance* is in
    meters.
  - The meaning of the *heading* values:

    - -25: far left
    - 0: straight forwards
    - 25: far right

The output of my program was:

.. code:: none

  EV3_IR at PORT_2 of Wifi connected EV3 00:16:53:42:2B:99 (Hugo)
  beacon on channel 3: Beacon(heading=-6, distance=0.23)

The beacon was positioned left ahead in a distance of 23 cm.


Using up to four beacons
~~~~~~~~~~~~~~~~~~~~~~~~

If you need to identify the exact orientation and position of your EV3
device, you can use multiple beacons. Because they send on four
different channels, you can simultaneously up to four of
them. Attribute :py:attr:`~ev3_dc.Infrared.beacons` allows to ask for
their positions at once.

As before, connect your EV3 device with your local network via
Wifi. Replace the MAC-address by the one of your EV3 brick. Connect an
infrared sensor with PORT 2, place up to four beacons somewhere in
front of the sensor, select different channels and switch on the
beacons, then start this program.

.. code:: python3

  import ev3_dc as ev3
  
  my_infrared = ev3.Infrared(
          ev3.PORT_2,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )
  
  print(f'beacons: {my_infrared.beacons}')

The output of my program run:

.. code:: none

  beacons: (None, Beacon(heading=5, distance=0.32), None, None)

Some remarks:

  - This was a single beacon, sending on channel 2, which was
    positioned right ahead in a distance of 32 cm.
  - The returned data is a tuple of four items, one per channel.
  - If no beacon was found, the channel's item is set to *None*.
  - If a beacon was found, the channel's item is of type *Beacon*.


Using the beacon as a remote control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Infrared` has an attribute
:py:attr:`~ev3_dc.Infrared.remote`, which returns a named tuple of
type *Remote*. It tells, which of the beacon's buttons currently were
pushed.

Connect your EV3 device with your local network via Wifi. Replace the
MAC-address by the one of your EV3 brick. Connect an infrared sensor
with PORT 2, place a beacon somewhere in front of the sensor, select
channel 3 and switch on the beacon, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_infrared = ev3.Infrared(
          ev3.PORT_2,
          channel=3,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )
  
  while True:
      remote_state = my_infrared.remote
      if remote_state is not None:
          break
      sleep(0.1)
      
  print(f'state of the remote on channel {my_infrared.channel}: {remote_state}')

Some remarks:

  - Every 100 ms, the state of the remote is requested, which means
    request and reply communication between program and EV3 device ten
    times per second.
  - The state of the remote control is stored in variable *remote_state*. This allows to
    use it to end the loop as well as for the printing.
  - You will easily imagine, how to define different actions for
    different states of the remote data.
    

The output of my program's execution:

.. code:: none

  state of the remote on channel 3: Remote(permanent=False, red_up=False, red_down=True, blue_up=True, blue_down=False)

This says, someone pushed two of the buttons simultaneously. The
communication does not handle triple pushes and double pushes are
restricted to the buttons *red_up*, *red_down*, *blue_up* and
*blue_down*. Altogether, we can distinguish 11 different states
plus none pushes.


Reading multiple remote control channels simultaneously
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you try to use multiple beacons simultaneously as remote controls,
you can do that with attribute :py:attr:`~ev3_dc.Infrared.remotes`,
which returns a tuple of four items, one per channel. As you will
have expected, each of them may be *None* or of type *Remote*.

As before, connect your EV3 device with your local network via
Wifi. Replace the MAC-address by the one of your EV3 brick. Connect an
infrared sensor with PORT 2, then start the program. After some time
push any button of a beacon.

.. code:: python3

  import ev3_dc as ev3
  import time
  
  my_infrared = ev3.Infrared(
          ev3.PORT_2,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )
  
  print(f'started at {time.strftime("%H:%M:%S", time.localtime())}')
  
  def any_remote():
      for remote in my_infrared.remotes:
          if remote:
              return remote
  
  while True:
      the_active_one = any_remote()
      if the_active_one:
          break
      time.sleep(0.1)
  
  print(the_active_one)
  print(f'stopped at {time.strftime("%H:%M:%S", time.localtime())}')
  
The output of my program's execution:

.. code:: none

  started at 18:32:01
  Remote(permanent=False, red_up=False, red_down=True, blue_up=True, blue_down=False)
  stopped at 18:32:09

Some remarks:

  - Eight seconds after the program's start, someone simultaneously
    pressed two buttons of a beacon. These buttons were *red_down* and
    *blue_up*.
  - This program does not care about channels. Function *any_remote*
    loops over all four channels and if it finds one unequal *None*,
    this one is returned.
  - May be, your program only supports one beacon as a remote control
    but you do not trust the user to select the correct channel. This
    may be the solution: you read all four channels and then select
    the correct one.
  - May be your program is thought for multiple users and every user
    has his own beacon. Then any of them can end the program.
    
