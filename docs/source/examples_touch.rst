-----
Touch
-----

:py:class:`~ev3_dc.Touch` is a subclass of :py:class:`~ev3_dc.EV3`.
You can use it to read values from a single touch sensor without any knowledge of direct
command syntax.

To use multiple touch sensors, you can create multiple instances of class Touch.


Asking for the current state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attribute :py:attr:`~ev3_dc.Touch.touched` is of type bool and tells,
if the sensor currently is touched.

Connect your EV3 device with your local network via Wifi.
Replace the MAC-address by the one of your EV3 brick, connect a touch sensor
(it may be an EV3-Touch or a NXT-Touch)
with PORT 1, then start this program.
            

.. code:: python3

  import ev3_dc as ev3
  
  my_touch = ev3.Touch(
      ev3.PORT_1,
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99'
  )
  is_touched = my_touch.touched

  print(str(my_touch) + ':')
  print(
      'currently touched' if is_touched else 'currently not touched'
  )
    
Some remarks:

  - You already know, how to change the program, when using protocols
    Bluetooth or USB.
  - As the first output line shows, the class knows it's sensor type.
  - Run the program multiple times with touched and not touched sensor.
  - Test what happens, when no sensor is connected to PORT 1.
  - Test what happens, when another sensor type is connected to PORT 1.
  - Switch on verbosity and you will see the communication data.


Multiple instances of class Touch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect another touch sensor
(again it may be an EV3-Touch or a NXT-Touch)
with PORT 4, then start this program.
            

.. code:: python3

  import ev3_dc as ev3
  
  touch_left = ev3.Touch(
      ev3.PORT_1,
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99'
  )
  
  touch_right = ev3.Touch(
      ev3.PORT_4,
      ev3_obj=touch_left
  )
  
  is_touched_left = touch_left.touched
  is_touched_right = touch_right.touched

  print(str(touch_left) + ':')
  print(
      'currently touched' if is_touched_left else 'currently not touched'
  )
  print(str(touch_right) + ':')
  print(
      'currently touched' if is_touched_right else 'currently not touched'
  )
    
Some remarks:

  - Both touch sensors share the same EV3 device. Therefore only the
    first instance is initialized with the keyword arguments
    *protocol* and *host*.  The second instance is initialized with
    keyword argument *ev3_obj* instead.
  - Here, both sensors are handled independently, therefore the
    communication data are not optimized. The request of the sensors'
    state could have been done in a single direct command, but here it
    needs two instead.


Bump-Mode
~~~~~~~~~

Touch sensors provide two modes, touch and bump (see sections
:ref:`Touch mode of the Touch Sensor <touch-mode-dc>` and :ref:`Bump
mode of the Touch Sensor <bump-mode-dc>`). The touch-mode is, what we
have seen above: the sensor replies it's current state. The bump-mode
counts the number of bumps since the last sensor clearing.

Connect your EV3 device with your local network via Wifi.
Replace the MAC-address by the one of your EV3 brick, connect a touch sensor
(it may be an EV3-Touch or a NXT-Touch)
with PORT 1, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_touch = ev3.Touch(
          ev3.PORT_1,
          protocol=ev3.WIFI,
          host='00:16:53:42:2B:99'
  )
  
  print('\n' + 'countdown ...' + '\n')
  for n in range(10, 0, -1):
      print('\r' + f'{n:2d} ', end='', flush=True)
      sleep(1)
  
  print('\r' + '** go ** ', end='', flush=True)
  
  my_touch.bumps = 0
  sleep(5)
  
  print('\r' + 'number of bumps:', my_touch.bumps)
    
Some remarks:

  - This program counts the number of bumps for a timespan of 5 sec.
  - To prevent jumping the start, the sensor clearing is done at the
    end of the countdown.
  - Instead of setting property *bumps = 0*, you alternatively can
    call method :py:meth:`~ev3_dc.Touch.clear()`.
  - Compare the version above with the manually coded direct commands
    from section :ref:`Bump mode of the Touch Sensor <bump-mode-dc>`
    and you will realize the handiness of sensor classes.



 
