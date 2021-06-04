#####
Touch
#####

:py:class:`~ev3_dc.Touch` is a subclass of :py:class:`~ev3_dc.EV3`.
You can use it to read values from a single touch sensor without any knowledge of direct
command syntax.

To use multiple touch sensors, you can create multiple instances of class Touch.


++++++++++++++++++++++++++++
Asking for the current state
++++++++++++++++++++++++++++

Property :py:attr:`~ev3_dc.Touch.touched` is of type bool and tells,
if the sensor currently is touched.

Connect your EV3 device with your local network via WiFi and make
sure, it's the only EV3 devices in the network. Connect a touch
sensor (it may be an EV3-Touch or a NXT-Touch) with PORT 1, then start
this program.
            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Touch(ev3.PORT_1, protocol=ev3.WIFI) as my_touch:
      print(str(my_touch) + ':', end=' ')
      print('touched' if my_touch.touched else 'not touched')
    
Some remarks:

  - You already know, how to modify the program, when using protocols
    Bluetooth or USB.
  - As the output line shows, the class knows it's sensor type.
  - Run the program multiple times with touched and not touched sensor.
  - Test what happens, when no sensor is connected to PORT 1.
  - Test what happens, when another sensor type is connected to PORT 1.
  - Switch on verbosity and you will see the communication data.


+++++++++++++++++++++++++++++++++
Multiple instances of class Touch
+++++++++++++++++++++++++++++++++

Connect an additional touch sensor (again it may be an EV3-Touch or a
NXT-Touch) with PORT 4, then start this program.
            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Touch(ev3.PORT_1, protocol=ev3.WIFI) as touch_left:
      touch_right = ev3.Touch(ev3.PORT_4, ev3_obj=touch_left)
      print(str(touch_left) + ':', end=' ')
      print('touched' if touch_left.touched else 'not touched')
      print(str(touch_right) + ':', end=' ')
      print('touched' if touch_right.touched else 'not touched')
    
Some remarks:

  - Both touch sensors share the same EV3 device. Therefore only the
    first instance is initialized with keyword argument
    *protocol*. The second instance is initialized with keyword
    argument *ev3_obj* instead.
  - *touch_left* owns the connection, *touch_right* is its joint user.
  - A single EV3 device controls up to four sensors and additionally
    up to four motors. You will deal with more than two objects, when
    you make use of EV3's full capacity.
  - Both sensors are handled independently, therefore the
    communication is not optimized. The request of both sensors' state
    could have been done in a single direct command, but here it needs
    two instead.


.. _bump_mode:

+++++++++
Bump-Mode
+++++++++

Touch sensors provide two modes, touch and bump (see sections
:ref:`Touch mode of the Touch Sensor <touch-mode-dc>` and :ref:`Bump
mode of the Touch Sensor <bump-mode-dc>`). The touch-mode is, what we
have seen above: the sensor replies it's current state. The bump-mode
counts the number of bumps since the last sensor clearing.

Connect your EV3 device with your local network via WiFi.
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



 
