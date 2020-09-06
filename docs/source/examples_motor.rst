-----
Motor
-----

:py:class:`~ev3_dc.Motor` is a subclass of :py:class:`~ev3_dc.EV3`.
You can use it to move a single motor without any knowledge of direct
command syntax. Class Motor uses `thread_task
<https://thread-task.readthedocs.io/en/latest>`_, which allows to move
motors parallel to other activities.

To use multiple motors, you can create multiple instances of class Motor.


Precise and Smooth Motor Movements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start_move
^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.start_move` starts a motor movement by
a given angle.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.
            

.. code:: python3

  import ev3_dc as ev3
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_motor.verbosity = 1
  my_motor.speed = 20
  my_motor.ramp_up = 30
  my_motor.ramp_down = 30
  
  my_motor.start_move(90, brake=False)
  
  print(
      '\n' +
      'type:', my_motor.type,
      'busy:', my_motor.busy
  )
    
Some remarks:

  - *verbosity* is set because we want to analyse the communication
    beween the program and the EV3 brick.
  - We set the default *speed* to 20 % of the maximum
    speed. Alternatively you can set the speed when creating the
    object or when starting a movement or you use the default setting
    of 10 %.
  - Setting a default *ramp_up* and *ramp_down* results in a smooth
    movement with acceleration and a deceleration phases at the begin
    and end of the movement. The defaults are 15 degrees, we want a
    smoother movement and set 30 degrees. As above, you can also set
    them when creating the object or when starting a movement.
  - The program ends before the movement has finished because method
    :py:meth:`~ev3_dc.Motor.start_move` does, what its name says. It
    starts a movement but does not control it.
  - Keyword argument *brake* allows to end the movement with an active brake (default)
    or with a free floating motor.
  - The EV3 knows two motor types (7: large, 8: medium). Class :py:class:`~ev3_dc.Motor` is
    introspective and can tell the motor type.
  - This program doesn't get any feedback at the end of the
    movement. It tells the EV3 brick what to do, then the EV3 brick
    acts independently. Periodically asking for the busy state would
    help to get informed.

The output:

.. code-block:: none

  16:58:29.784500 Sent 0x|1C:00|2A:00|00|01:04|99:05:00:11:60:40:A2:00:02:B2:00:02:AE:00:02:14:1E:1E:1E:00:A6:00:02|
  16:58:29.792001 Recv 0x|04:00|2A:00|02|08|
  16:58:29.792606 Sent 0x|09:00|2B:00|00|01:00|A9:00:02:60|
  16:58:29.805343 Recv 0x|04:00|2B:00|02|01|
  
  type: 8 busy: True

Some remarks:

  - If you are an expert on EV3 direct commands, you can do reverse enineering and
    you will identify the following operations in the first direct command:
    
    - *opInput_Device* with CMD *GET_TYPEMODE*: asks for the type of the motor.
    - *opOutput_Reset*: resets the tracking informations.
    - *opOutput_Clr_Count*: clears the tacho counter.
    - *opOutput_Step_Speed*: defines a smooth and exact movement.
    - *opOutput_Start*: starts the movement.
  
  - The first reply tells the type of the device at PORT B (medium motor).
  - The second direct command sends *opOutput_Test* as its single operation, which asks
    if the motor is currently busy.
  - The second reply tells, the motor is currently busy.


task_move
^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.task_move` moves a motor by a given
angle. The API is very similar to method
:py:meth:`~ev3_dc.Motor.start_move`, but it returns a
`thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object that controls the movement and allows parallel activities.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  
  t = my_motor.task_move(90, brake=False) + Task(print, args=('done',))
  t.start()
  
  print(
      '\n' +
      'type:', my_motor.type,
      'busy:', my_motor.busy
  )

Some remarks:

  - The movement by 90 degrees is the first chain link of the Task
    object **t**. The second chain link prints the text ``done``.
  - Task **t** runs in its own thread in the background, therefore the
    motor type and busy state are printed some time before the
    movement has finished and ``done`` is printed.
  - A threadless start of Task **t** lets it behave like a standard
    callable. Replace *t.start()* by *t.start(thread=False)* and the
    program will wait until the movement has finished, then it will
    print type and busy state.

The next program really does two things parallel. It plays the song
*Frère Jacques* and it moves the motor at port *B* forwards and
backwards.
 
.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task, Repeated
  from time import sleep
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_jukebox = ev3.Jukebox(ev3_obj=my_motor)
  
  t_song = my_jukebox.song(ev3.FRERE_JACQUES)
  t_movements = Repeated(
      my_motor.task_move(90) + my_motor.task_move(-90)
  )
  t = Task(t_movements.start) + t_song + Task(t_movements.stop)
  
  t.start()
  
  sleep(3)
  t.stop()
  
  sleep(3)
  t.cont()

Some remarks:

  - *my_motor* and *my_jukebox* communicate with the same physical EV3
    brick. This is, what *ev3_obj=my_motor* means.
  - *t_song* is a `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    object.
  - *t_movements* is a `thread_task.Repeated
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#repeated>`_
    object.
  - Song and movements together also is a `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    object named *t*, that can be started, stopped and continued.
  - The timing is done by the song *Frère Jacques*. As long as it lasts, the motor moves
    forwards and backwards.
  - The movements are precise and smooth and have a measure of 90 degrees.
  - Stopping *t* stops the song and the movement and continuing *t*
    continues both.
  - There is no setting of *speed*, *ramp_up* or *ramp_down*, this
    program uses the defaults.


start_move_to
^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.start_move_to` moves a motor to a given position.

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
  
  my_motor.start_move_to(90, brake=False)
  sleep(5)
  my_motor.start_move_to(0, brake=False)

Some remarks:

  - The motor positions are relative to the position from where the first
    movement started. From then on class :py:class:`~ev3_dc.Motor`
    remembers this position as its zero point.
  - Use the timespan of 5 sec. between the two movements and move the
    motor by hand. Class Motor will realize the manual movement and
    will correctly move the motor to its zero position.
  - Modify the program and set *brake=True* in the first
    movement. This activates the brake and prevents manual movements.


task_move_to
^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.task_move_to` moves a motor to a given
position. The API is very similar to method
:py:meth:`~ev3_dc.Motor.start_move_to`, but it returns a
`thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object that controls the movement and allows parallel activities.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3

  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  
  t = (
      my_motor.task_move_to(90, brake=False, duration=5) +
      my_motor.task_move_to(0, brake=False)
  )
  t.start()
  
Some remarks:

  - The motor does the same movements as in the *start_move_to* example.
  - As before, you can move the motor by hand.
  - `thread_task.Task
    <https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
    objects are like LEGO bricks, a combination with other Task
    objects builds a new Task object and this growth of complexity is
    unlimited.
    movement. This activates the brake and prevents manual movements.


reset_position
^^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.reset_position` defines the current
motor position to be the new zero position of this motor.

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

  t = (
      my_motor.task_move_to(90) +
      my_motor.task_move_to(0, brake=False)
  )
  t.start(thread=False)
  
  print('Please move the motor to its new zero position.')
  sleep(5)
  my_motor.reset_position()
  
  t.start(thread=False)

Some remarks:

  - Starting a Task object with *thread=False* means, it behaves like
    a normal callable because it doesn't run in its own thread.
  - The manual movement changes the motor position.
  - Method :py:meth:`~ev3_dc.Motor.reset_position` sets the new zero position.
  - The second execution of Task *t* is relative to the new zero position.


Steady Motor Movements
~~~~~~~~~~~~~~~~~~~~~~

Another operating mode of a motor may be to start and steadily run it
until something happens that requires to stop it.

start, stop and cont
^^^^^^^^^^^^^^^^^^^^

Connect your EV3 brick with your computer via Bluetooth, replace the
MAC-address by the one of your EV3 brick, connect a motor (medium or
large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep

  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.BLUETOOTH,
      host='00:16:53:42:2B:99'
  )
  my_motor.verbosity = 1
  
  my_motor.start()
  sleep(1)
  my_motor.start(direction=-1)
  sleep(1)
  my_motor.stop()

Some remarks:

  - No speed was set, the default speed is used.
  - The second movement interrupts the first one.

The output:

.. code-block:: none

  10:19:30.481673 Sent 0x|18:00|2A:00|00|01:04|99:05:00:11:60:40:A2:00:02:B2:00:02:A5:00:02:0A:A6:00:02|
  10:19:30.526077 Recv 0x|04:00|2A:00|02|08|
  10:19:31.527809 Sent 0x|0C:00|2B:00|80|00:00|A5:00:02:36:A6:00:02|
  10:19:32.529746 Sent 0x|09:00|2C:00|80|00:00|A3:00:02:00|

Some remarks:

  - The first direct command asks for the device type at port B and starts the motor.
  - The reply of the first command tells, it is a medium motor.
  - The second command interrupts the current motor movement and starts a new
    movement in opposite direction.
  - The third command stops the motor movement.

If you like the idea of `thread_task
<https://thread-task.readthedocs.io/en/latest>`_, create a
`thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
object, that can be started, stopped and continued.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task
  from time import sleep
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.BLUETOOTH,
      host='00:16:53:42:2B:99',
  )
  my_motor.verbosity = 1
  
  t = Task(
      my_motor.start,
      duration=1
  ) + Task(
      my_motor.start,
      kwargs={'direction': -1},
      duration=1
  ) + Task(
      my_motor.stop
  )
  t.action_stop = my_motor.stop
  t.action_cont = my_motor.cont
  
  t.start()
  
  sleep(1.5)
  t.stop()
  
  sleep(3)
  t.cont(thread=False)
  
  print('\nFinal position (degrees):', my_motor.position)
    
Some remarks:

  - These movements are time driven and do not care about positions.
  - *t* is a chain with three links: forwards-movement,
    backwards-movement and stopping.
  - Method :py:meth:`~ev3_dc.Motor.stop` can be used to interrupt or
    to end the current movement.
  - Method :py:meth:`~ev3_dc.Motor.cont` continues a stopped movement.
  - Class :py:class:`~ev3_dc.Motor` remembers its current movement, therefore
    the continuation does not need any arguments.
  - Setting *thread=False* runs the continuation in the thread of the
    main program and causes the program to print the final position
    when the movement has finished.

The output:

.. code-block:: none

  10:59:56.619634 Sent 0x|18:00|2A:00|00|01:04|99:05:00:11:60:40:A2:00:02:B2:00:02:A5:00:02:0A:A6:00:02|
  10:59:56.688233 Recv 0x|04:00|2A:00|02|08|
  10:59:57.620112 Sent 0x|0C:00|2B:00|80|00:00|A5:00:02:36:A6:00:02|
  10:59:58.122279 Sent 0x|09:00|2C:00|80|00:00|A3:00:02:00|
  11:00:01.125592 Sent 0x|0C:00|2D:00|80|00:00|A5:00:02:36:A6:00:02|
  11:00:01.623877 Sent 0x|09:00|2E:00|80|00:00|A3:00:02:00|
  11:00:01.624467 Sent 0x|0D:00|2F:00|00|04:00|99:1D:00:11:08:00:01:60|
  11:00:01.663902 Recv 0x|07:00|2F:00|02|00:00:60:41|
  
  Final position (degrees): 14
  
Some remarks:

  - Stop and continue reduce the angle of the second movement. Here
    the timing is precise, not the movement. There is a difference
    between the original and the final position of 14 degrees.
  - You will identify the corresponding direct commands from the program output above.
  - Additional direct command with message counter 0x|2C:00| is the stopping.
  - Additional direct command with message counter 0x|2D:00| is the continuation.
  - Additional direct command with message counter 0x|2F:00| asks for the current position.

    
task_move_steady
^^^^^^^^^^^^^^^^

Method :py:meth:`~ev3_dc.Motor.task_move_steady` starts a steady
movement and controls it.  This says the movement has a positional
argument *degrees* and the thread task lasts as long as the movement.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect a motor
(medium or large) with PORT B, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task
  
  my_motor = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  my_motor.verbosity = 1
  
  (
      my_motor.task_move_steady(180, speed=20) +
      my_motor.task_move_steady(-180) +
      Task(my_motor.stop)
  ).start()
  
Some remarks:

  - A chain of thread tasks with three links. The last one is the stopping.
  - If the stopping is omitted, the task will end, but not the movement.
  - The first part of the movement is faster because we set *speed=20*. The second
    part is uses default speed, which is 10.

The output:

.. code-block:: none

  17:18:50.008564 Sent 0x|18:00|2A:00|00|01:04|99:05:00:11:60:40:A2:00:02:B2:00:02:A5:00:02:14:A6:00:02|
  17:18:50.021021 Recv 0x|04:00|2A:00|02|08|
  17:18:50.058820 Sent 0x|0D:00|2B:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.063003 Recv 0x|07:00|2B:00|02|00:00:A0:40|
  17:18:50.142708 Sent 0x|0D:00|2C:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.147030 Recv 0x|07:00|2C:00|02|00:00:F0:41|
  17:18:50.311020 Sent 0x|0D:00|2D:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.320993 Recv 0x|07:00|2D:00|02|00:00:A0:42|
  17:18:50.485352 Sent 0x|0D:00|2E:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.491962 Recv 0x|07:00|2E:00|02|00:00:08:43|
  17:18:50.552807 Sent 0x|0D:00|2F:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.563946 Recv 0x|07:00|2F:00|02|00:00:1E:43|
  17:18:50.589000 Sent 0x|0D:00|30:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.593874 Recv 0x|07:00|30:00|02|00:00:28:43|
  17:18:50.625268 Sent 0x|14:00|31:00|00|04:00|99:1D:00:11:08:00:01:60:A5:00:02:36:A6:00:02|
  17:18:50.633909 Recv 0x|07:00|31:00|02|00:00:34:43|
  17:18:50.675518 Sent 0x|0D:00|32:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.681892 Recv 0x|07:00|32:00|02|00:00:36:43|
  17:18:50.771538 Sent 0x|0D:00|33:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:50.780877 Recv 0x|07:00|33:00|02|00:00:22:43|
  17:18:51.065734 Sent 0x|0D:00|34:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:51.076815 Recv 0x|07:00|34:00|02|00:00:E0:42|
  17:18:51.397397 Sent 0x|0D:00|35:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:51.408836 Recv 0x|07:00|35:00|02|00:00:74:42|
  17:18:51.596295 Sent 0x|0D:00|36:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:51.601908 Recv 0x|07:00|36:00|02|00:00:F0:41|
  17:18:51.690048 Sent 0x|0D:00|37:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:51.697917 Recv 0x|07:00|37:00|02|00:00:70:41|
  17:18:51.738371 Sent 0x|0D:00|38:00|00|04:00|99:1D:00:11:08:00:01:60|
  17:18:51.745911 Recv 0x|07:00|38:00|02|00:00:00:41|
  17:18:51.793587 Sent 0x|09:00|39:00|00|00:00|A3:00:02:00|
  17:18:51.799789 Recv 0x|03:00|39:00|02|
  
Some remarks:

  - If you analyze the timesteps between the direct commands, you will
    realize, that they grow at the beginning of a movement
    and shrink at its end.
  - Compared with :py:meth:`~ev3_dc.Motor.task_move`, this type of
    movement costs less data traffic.
  - The movements are steady but less precise than
    :py:meth:`~ev3_dc.Motor.task_move`.
  - Additional direct command with message counter 0x|2F:00| asks for the current position.

    
Multiple Motors
~~~~~~~~~~~~~~~

If you try to use multiple motors, create multiple instances of class
:py:class:`~ev3_dc.Motor`.

Take an USB cable and connect your EV3 brick with your computer.
Replace the MAC-address by the one of your EV3 brick, connect two motors
(medium or large ones) with PORT B and PORT C, then start this program.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task
  
  my_motorB = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  my_motorC = ev3.Motor(
      ev3.PORT_C,
      ev3_obj=my_motorB,
      speed=100
  )
  
  (
      Task(my_motorC.start) +
      my_motorB.task_move_steady(180, speed=20) +
      my_motorB.task_move_steady(-180) +
      Task(my_motorB.stop) +
      Task(my_motorC.stop)
  ).start()
  
Some remarks:

  - The timing is done by the movement of motor B.
  - The full speed movement of motor C ends with a roll out.

The program started a `thread_task.Task
<https://thread-task.readthedocs.io/en/latest/api_documentation.html#task>`_
that was not ready for stopping and continuation. To add this
functionality, the unlimited movements must be handled carefully.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Task
  from time import sleep
  
  my_motorB = ev3.Motor(
      ev3.PORT_B,
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  my_motorC = ev3.Motor(
      ev3.PORT_C,
      ev3_obj=my_motorB,
      speed=100
  )
  
  t = (
      Task(my_motorC.start) +
      my_motorB.task_move_steady(180, speed=20) +
      my_motorB.task_move_steady(-180) +
      Task(my_motorB.stop) +
      Task(my_motorC.stop)
  )
  t.action_stop = my_motorC.stop
  t.action_cont = my_motorC.cont
  
  t.start()
  
  sleep(1)
  t.stop()
  
  sleep(5)
  t.cont()
  
