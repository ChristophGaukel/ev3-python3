-----
Motor
-----

:py:class:`~ev3_dc.Motor` is a subclass of :py:class:`~ev3_dc.EV3`.
You can use it to move a single motor without any knowledge of direct
command syntax. Class Motor uses `thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_,
which allows to move motors parallel to other activities.

To use multiple motors, you can create multiple instances of class Motor.


Properties of Class Motor
~~~~~~~~~~~~~~~~~~~~~~~~~

Beside the properties, which it inherits from its parent class
:py:class:`~ev3_dc.EV3`, class :py:class:`~ev3_dc.Motor` provides some
additional properties.


busy
^^^^

Read only property :py:attr:`~ev3_dc.Motor.busy` tells if the motor
currently is busy, which means, it is actively moving.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  ) as my_motor:
      if my_motor.busy:
          print('the motor currently is busy')
      else:
          print('the motor currently is not busy')


motor_type
^^^^^^^^^^

Read only property :py:attr:`~ev3_dc.Motor.motor_type` tells the motor
type of the motor. The values may be 7 (ev3_dc.EV3_LARGE_MOTOR) or 8
(ev3_dc.EV3_MEDIUM_MOTOR).

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print(f'the motor type: {my_motor.motor_type}')



port
^^^^

Read only property :py:attr:`~ev3_dc.Motor.port` tells the port to
which this motor is connected. The values may be 1 (ev3_dc.PORT_A), 2
(ev3_dc.PORT_B), 3 (ev3_dc.PORT_C) or 4 (ev3_dc.PORT_D).

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print(f'the port, where this motor is connected to: {my_motor.port}')


position
^^^^^^^^

Property :py:attr:`~ev3_dc.Motor.position` tells the current motor
position [degree]. After creating a new object of class *Motor*, its
*position* is *0°*. This is independent from the motor's history.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print('please move the motor manually (you have 5 sec. of time)')
      sleep(5)

      print(f'the current motor position is: {my_motor.position}°')

Property *position* allows to reset the motor's position. This means:
the current position becomes the new zero position. As mentioned
above, this also is done, whenever a new instance of class *Motor* is
instantiated.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print('please move the motor manually (you have 5 sec. of time)')
      sleep(5)

      print(f'the current motor position is: {my_motor.position}°')

      my_motor.position = 0
      print(f'after resetting, the new motor position is: {my_motor.position}°')
      
 
delta_time
^^^^^^^^^^

Property :py:attr:`~ev3_dc.Motor.delta_time` affects the data traffic
and precision of controlled movements. Its default value depends on
the connection type and is 0.05 sec. (ev3.USB), 0.10 sec. (ev3.WIFI)
and 0.20 sec. (ev3.BLUETOOTH). You can set this value when creating a
new *Motor* object, you can also change this value, whenever you need
higher precision or whenever you need to reduce the data traffic.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print(f'the default value of delta_time is: {my_motor.delta_time} sec.')
      sleep(5)

      my_motor.delta_time = 0.2
      print(f'we reduce data traffic and set delta_time to: {my_motor.delta_time} sec.')


speed
^^^^^

Property :py:attr:`~ev3_dc.Motor.speed` and measures in percent and
sets the speed of this motor's movements.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
      speed=100
  ) as my_motor:
      print(f'speed: {my_motor.speed}%')
      sleep(5)
  
      my_motor.speed = 20
      print(f'new speed: {my_motor.speed}%')


ramp_up and ramp_down
^^^^^^^^^^^^^^^^^^^^^

Properties :py:attr:`~ev3_dc.Motor.ramp_up` and
:py:attr:`~ev3_dc.Motor.ramp_down` measure in degrees and adjust the
smoothness of precise movements. The higher the speed is, the higher these
values should be. This relationship is a quadratic one. This says: if
you double the speed, you should multiply ramp_up and ramp_down by a
factor four.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print(
          f'defaults of speed: {my_motor.speed}%, ' +
	  f'ramp_up: {my_motor.ramp_up}° ' +
	  f'and ramp_down: {my_motor.ramp_down}°'
      )

The output:

.. code-block:: none

  defaults of speed: 10%, ramp_up: 15° and ramp_down: 15°

There are three options to set *speed*, *ramp_up* and *ramp_down*:

- Set them as keyword arguments, when a new object of class
  :py:class:`~ev3_dc.Motor` is created.
- Use properties to change these values for defined parts of your program.
- Set them as keyword arguments per movement. This option does not
  affect any of the following movements.


ramp_up_time and ramp_down_time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Properties :py:attr:`~ev3_dc.Motor.ramp_up_time` and
:py:attr:`~ev3_dc.Motor.ramp_down_time` measure in seconds and adjust the
smoothness of timed movements. As before, the higher the speed is, the higher these
values should be. But here the relationship is linear. This says: if
you double the speed, you should also double ramp_up_time and ramp_down_time.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.            

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      print(
          f'defaults of speed: {my_motor.speed} %, ' +
	  f'ramp_up_time: {my_motor.ramp_up_time} sec. ' +
	  f'and ramp_down_time: {my_motor.ramp_down_time} sec.'
      )

The output:

.. code-block:: none

  defaults of speed: 10%, ramp_up_time: 0.15 sec. and ramp_down_time: 0.15 sec.
  

Precise and Smooth Motor Movements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

move_to
^^^^^^^

Method :py:meth:`~ev3_dc.Motor.move_to` returns a `thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object, which can be started, stopped and continued. You can combine
such *Task* objects with other *Task* objects just like you combine
LEGO bricks.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.
            

.. code:: python3

  from thread_task import Sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      movement_plan = (
          my_motor.move_to(360) +
          Sleep(5) +
          my_motor.move_to(0, speed=100, ramp_up=90, ramp_down=90, brake=True) +
          Sleep(0.5) +
          my_motor.stop_as_task(brake=False)
      )
  
      movement_plan.start()
      print('movement has been started')
      
      movement_plan.join()
      print('movement has been finished')
      
Some remarks:

  - operator + combines two *Task* objects. Here we combine multiple
    *Task* objects and the resulting *Task* object is named
    *movement_plan*.
  - Starting the *Task* object happens in the blink of an eye even when
    the movement needs a number of seconds.
  - The program joins the *movement_plan*, which says: it waits until
    the *movement_plan* has finished.
  - *movement_plan* first moves the motor to position *360°*, then it
    sleeps for five sec., then it moves the motor back to its original
    position.
  - The first movements ends with a free floating motor, the second
    one with activated brake, which is released 0.5 sec. later.
  - Explicitly setting *brake=False* in method *stop_as_task* is not
    needed, this is the default.
  - You can manually move the motor in the first sleeping
    timespan. Try that, it will not prevent the motor from moving back
    to its original position.
  - The first movement moves with default speed of *10%*, the second one
    moves with maximum speed.
  - Joining allows to do the second printing after *movement_plan's*
    end.

The output:

.. code-block:: none

  movement has been started
  movement has been finished

We modify this program:

.. code:: python3

  from thread_task import Sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      movement_plan = (
          my_motor.move_to(360) +
          Sleep(5) +
          my_motor.move_to(0, speed=100, ramp_up=90, ramp_down=90, brake=True) +
          Sleep(0.5) +
          my_motor.stop_as_task(brake=False)
      )
  
      print('movement starts now')
      movement_plan.start(thread=False)
  
      print('movement has been finished')

Starting *movement_plan* with keyword argument *thread=False* makes
its execution more familiar. The program waits until the movement has
finished, then it continues with its next statement. The creation of
*movement_plan* with its two movements is not different from the
version above.


move_by
^^^^^^^

Method :py:meth:`~ev3_dc.Motor.move_by` moves a motor by a given
angle. The API is very similar to method
:py:meth:`~ev3_dc.Motor.move_to`.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      (
          my_motor.move_by(360, brake=True) +
	  my_motor.move_by(-360)
      ).start(thread=False)

Some remarks:

- Programs should never end with any motor's brake in active
  state. This permanently would cost power until the motor is used
  again or the LEGO brick shuts down. Therefore the default setting is
  *brake=False*.
- Here the *Task* has no name, it's a anonymous *Task* object.
  

The next program really does two things parallel. It plays the song
*Frère Jacques* and it moves the motor at port *B* forwards and
backwards.
 
.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task, Repeated, Sleep
  from time import sleep
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_jukebox = ev3.Jukebox(ev3_obj=my_motor)
  
  t_song = my_jukebox.song(ev3.FRERE_JACQUES, volume=1)
  t_movements = Repeated(
      my_motor.move_by(90) + my_motor.move_by(-90)
  )
  t = Task(t_movements.start) + t_song + Task(t_movements.stop)
  
  t.start()
  
  sleep(5)
  t.stop()
  
  sleep(2)
  t.cont(thread=False)
  print('all done')

Some remarks:

  - *my_motor* and *my_jukebox* communicate with the same physical EV3
    brick. This is, what *ev3_obj=my_motor* means.
  - *t_song* is a `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    object.
  - *t_movements* is a `thread_task.Repeated
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#repeated>`_
    object.
  - *t*, which combines *t_song* and *t_movements* also is a `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    object, that can be started, stopped and continued.
  - The timing is done by the song *Frère Jacques*. As long as it lasts, the motor moves
    forwards and backwards.
  - The movements are precise and smooth and have a measure of 90 degrees.
  - Stopping *t* stops the song and the movement and continuing *t*
    continues both.
  - There is no setting of *speed*, *ramp_up* or *ramp_down*, this
    program uses the defaults.


start_move_to
^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.start_move_to` moves a motor to a given
position. But it does not control time. It's movement ends after
undetermined time and the program can't subsequently follow with the
next action.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  
  my_motor.start_move_to(90)
  sleep(5)
  my_motor.start_move_to(0)

Some remarks:

  - The motor positions are relative to the position from where
    instance *my_motor* of class :py:class:`~ev3_dc.Motor` was
    created. From then on class *Motor* remembers this position as its
    zero point.
  - Again you can use the timespan between the two movements and move the
    motor by hand. Class Motor will realize the manual movement and
    will correctly move the motor back to its zero position.
  - Modify the program and set *brake=True* in the first
    movement. This activates the brake and prevents manual movements.
  - Method *start_move_to* does not return a *thread_task.Task* object.
    It is an ordinary method, it just starts the movement.
  - The timing depends on the suggestion, that a movement of 90° needs
    less than 5 sec. of time. Method *start_move_to* is not time
    controlled, which makes it different from method *move_to*.


start_move_by
^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.start_move_by` relates to method
:py:meth:`~ev3_dc.Motor.move_by` as method
:py:meth:`~ev3_dc.Motor.start_move_to` relates to method
:py:meth:`~ev3_dc.Motor.move_to`. It starts a movement without any
time control. A program, which needs to know, if the movement still is
in progress, can use property :py:attr:`~ev3_dc.Motor.busy`. 

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      my_motor.start_move_by(360, brake=False)
      print('movement has been started')
      
      while my_motor.busy:
          sleep(.1)
          
      print(f'movement has finished at position {my_motor.position}°')
        
Some remarks:

  - The motor does a movement by 360° without time control.
  - The time control is done by the while loop.
  - Instead of coding the time control this way, think about using
    method :py:meth:`~ev3_dc.Motor.move_by`.

Timed and Smooth Motor Movements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

move_for
^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.move_for` returns a `thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object. It does not set the angle of a movement. Instead it sets its
duration. The name is meant as: move for a defined duration.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.
            

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      t = my_motor.move_for(
          3,
          speed=20,
          ramp_up_time=0.3,
          ramp_down_time=0.3
      ) + my_motor.move_for(
          3,
          speed=20,
          direction=-1,
          ramp_up_time=0.3,
          ramp_down_time=0.3
      )
      t.start()
      print('movement has been started')
  
      sleep(2)
      t.stop()
      
      sleep(3)
      t.cont(thread=False)
  
      print(f'movement has finished at position {my_motor.position}°')
  
Some remarks:

- As in some examples before, this program schedules two movements,
  forwards and backwards.
- After two seconds, during the first movement, task t is stopped and
  continued three seconds later. After the continuation it absolves
  the last second forwards and then the three seconds backwards.
- Compared with the examples above, here the duration of the task is
  precisely determined. It lasts exactly six seconds. If stopped and
  continued, the timespan of the interruption is added on top.

start_move_for
^^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.start_move_for` has the same argument
signature as method *move_for*, but it directly starts the movement
and does not return a `thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  from time import sleep
  import ev3_dc as ev3
  
  with ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  ) as my_motor:
      my_motor.start_move_for(
          3,
          speed=20,
          ramp_up_time=0.4,
          ramp_down_time=0.4
      )
      sleep(3)
      print(f'movement has finished at position {my_motor.position}°')

      
Unlimited Motor Movements
~~~~~~~~~~~~~~~~~~~~~~~~~

Another operating mode of a motor may be to start and steadily run it
until something interrupts or stops it. If you like to do so, use
methods :py:meth:`~ev3_dc.Motor.start_move` and
:py:meth:`~ev3_dc.Motor.stop`.

Connect your EV3 brick with your computer via USB, replace the
MAC-address by the one of your EV3 brick, connect a motor (medium or
large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_motor.verbosity = 1
  my_motor.sync_mode = ev3.STD
  
  my_motor.start_move()
  sleep(1)
  my_motor.start_move(direction=-1)
  sleep(1)
  my_motor.stop()
  
Some remarks:

  - No speed was set, therefore the default speed is used.
  - Each movement would last for unlimited time, if not interrupted.
  - Interrupting a movement by a next one with significant different
    speed means mechanical stress for the motor.
  - We want analyze the communication, therefore we set *verbosity = 1*.
  - *sync_mode = ev3.STD* prevents from needless replies because
    protocol *USB* would default to *sync_mode = ev3.SYNC*, which
    replies all requests.

The output:

.. code-block:: none

  08:30:44.141158 Sent 0x|15:00|2C:00|80|00:00|AF:00:02:0A:81:64:83:FF:FF:FF:7F:00:00:A6:00:02|
  08:30:45.143264 Sent 0x|15:00|2D:00|80|00:00|AF:00:02:36:81:64:83:FF:FF:FF:7F:00:00:A6:00:02|
  08:30:46.145253 Sent 0x|09:00|2E:00|80|00:00|A3:00:02:00|
  
Some remarks:

  - The first direct command starts the motor. It consists from two
    operations: *opOutput_Time_Speed* and *opOutput_Start*.
  - The second command interrupts the current motor movement and starts a new
    movement in opposite direction.
  - The third command stops the motor movement.

  
