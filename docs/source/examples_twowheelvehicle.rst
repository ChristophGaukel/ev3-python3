-----------------
Two Wheel Vehicle
-----------------

.. role:: python(code)
   :language: python3

:py:class:`~ev3_dc.TwoWheelVehicle` is a subclass of
:py:class:`~ev3_dc.EV3`.  You can use it for synchronized movements of
two motors. You need no knowledge of direct command syntax. Class
TwoWheelVehicle uses `thread_task
<https://thread-task.readthedocs.io/en/latest>`_, which allows to move
a vehicle parallel to other activities.

:py:class:`~ev3_dc.TwoWheelVehicle` tracks the movements of the
vehicle by tracking the motor movements of its two wheels. This allows
to ask for the current position and the current orientation of the
vehicle.


Calibration
~~~~~~~~~~~

Construct a vehicle with two drived wheels, connect your EV3 brick and
your computer via Wifi, replace the MAC-address by the one of your EV3
brick, connect the left wheel motor (medium or large) with PORT A and
the right wheel motor with PORT D, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Sleep, Task
  
  my_vehicle = ev3.TwoWheelVehicle(
      0.0209,  # radius_wheel
      0.1175,  # tread
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99',
  )
  
  parcours = (
      my_vehicle.task_straight(2.) +
      Sleep(.5) +
      Task(my_vehicle.stop)
  )
  parcours.start(thread=False)
  
Some remarks:
  - If you don't own a Wifi dongle, use protocol *BLUETOOTH* instead.
  - If your vehicle circles clockwise on place, add
    :python:`my_vehicle.polarity_right = -1` to your code.
  - If your vehicle circles anticlockwise on place, add
    :python:`my_vehicle.polarity_left = -1` to your code.
  - If your vehicle moves backwards, add :python:`my_vehicle.polarity_left = -1`
    and :code:`my_vehicle.polarity_right = -1` to your code.
  - Measure the real distance of your vehicle's movement, then do these steps:

    - Calclulate :math:`radius\_wheel = 0.0209\,m \times \frac{real\_distance}{2\,m}`.
    - In the program code replace 0.0209 by your :math:`radius\_wheel`.
    - Restart the program and again measure the distance of the movement. Now it
      should be close to :math:`2.00\,m`.
      

  - This parcours is quite simple, but you need to calibrate your vehicle before you
    can do precise movements.

Now, when you know the radius of your vehicle's wheels, you need to
know its tread. Please start the following program and count the circles.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Sleep, Task
  
  my_vehicle = ev3.TwoWheelVehicle(
      0.0209,  # radius_wheel
      0.1175,  # tread
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99',
  )
  
  parcours = (
      my_vehicle.task_turn(0, 3600) +
      Sleep(.5) +
      Task(my_vehicle.stop)
  )
  parcours.start(thread=False)


    



