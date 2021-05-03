++++++++++++++
PID Controller
++++++++++++++

A `PID controller <https://en.wikipedia.org/wiki/PID_controller>`_
implements a control loop mechanism, which applies a correction based
on a (p)roportional, an (i)ntegrative and a (d)erivative term.  *PID
controllers* are widely used in industrial control systems.

Background
==========

Let's think of a system which is controlled by a single control
signal. E.g. the position of the gas pedal regulates the speed of a
car. Any normal car driver is not able to describe the dependency of
his car's velocity from the position of the gas pedal. The only thing
he does: he changes the pedal's position, when he wants to accelerate
or decelerate his car. If we try to analyze the dependency between the
gas pedal's position and the car's velocity, we will find it quite
complicated, the velocity depends on the position of the gas pedal and
on multiple other factors, e.g.:

  - the slope of the road,
  - the load of the car
  - the current acceleration, e.g. at the beginning of the
    acceleration phase, a car under full gas will have a low
    speed. The opposite in case of deceleration: high speed combined
    with low gas.
  - the aerodynamic drag of the car, which depends on the car's surface
    form.
  - the efficiency of the car's motor.
  - the mechanical and electronical mechanism, which connects the gas
    pedal with the fuel injector and the motor electronics.

The parametrization of the controller does not need an analysis of
these dependencies (as the human driver does not need it). It instead
is based on practical experience and some simple rules of thumb.

Let's take a look on the mechanism: The controller modifies a control
signal (e.g. the position of the gas pedal) in dependency of a
measurement (e.g. the car's velocity). Using a controller needs a
sensor, which does the measurement and this measurement becomes the
controller's input. The output of the controller, the signal,
regulates the process, which says it is used as an input argument of a
regulating function or method.

Let's describe it as a formalism:

  - In a setup step, a controller is parametrized.
  - The parametrized controller is used inside a loop, where the following steps are
    executed repeatedly:

    - a measurement is done, which returns a value,
    - the controller takes the measurement value as its single input
      argument and returns a control signal.
    - the control signal is used as an input argument of a regulation.

With this formalism the PID controller is able to adjust the control
signal and this adaption often is astonishing close to the reaction of
an intelligent observer. We take a closer look on the setup step,
which needs:

  - A *setpoint*, which is the target measurement value (e.g. the
    target velocity of a car),
  - A *gain*, which describes the (proportional) relation between the
    error (deviation of the measured value from the *setpoint*) and
    the control signal (e.g. the position of the gas pedal). High
    gains help for fast adaption to the *setpoint*, but produce
    fluctuations.
  - An *integration time* (optional), which approx. is the time to
    eliminate deviations from the past. Be carefull, high integration
    times produce fluctuations.
  - A *deviation time* (optional), which approx. is the forecast
    time. This forecast says: if the car already accelerates, the gas
    pedal may stay unchanged, even when the velocity still is lower
    than the *setpoint*. A high forecast time helps to prevent nervous
    changes of the gas but reacts sensible on measurement noise. If
    the velocity measurement shows random fluctuations, the forecast's
    result will change to the opposite and will itself produce a
    nervous driving style.

Determing the *setpoint* often is easy, the rest needs some experience
and/or trial and error. Probably you will fastly learn to do it step
by step with some simple rules of thumb.


Close but not too Close
=======================

A few lines of code are worth a thousand words. We start with a quite
simple regulation. A vehicle drives towards a barrier and a controller
has to regulate this process. The measurement value is the current
distance from the barrier, the control signal ist the vehicle's
speed. The *setpoint* is the target distance from the barrier and it
is obvious, what the controller has to do. If the current distance is
higher than the *setpoint*, then the speed has to be positive. If the
distance is too small, then the velocity has to be negative. The
controller needs not more than a *setpoint* and a *gain* and is a P
controller (a proportional controller without any intergational or
deviative term).

Construct a vehicle with two drived wheels, connect the left wheel
motor (medium or large) with PORT A and the right wheel motor with
PORT D. Place an ifrared sensor on your vehicle, which directs
forwards. Connect the infrared sensor with port 2, then connect your
EV3 brick and your computer via WiFi, replace the MAC-address by the
one of your EV3 brick. If your vehicle is not calibrated, then measure
the diameter of the drived wheels and take half of the diameter as
value of radius_wheel (in meter). Then start this program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  # proportional controller for vehicle speed
  speed_ctrl =  ev3.pid(0.2, 100)
  
  with ev3.TwoWheelVehicle(
      0.01518,  # radius_wheel
      0.11495,  # tread
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99'
  ) as vehicle:
      infrared = ev3.Infrared(ev3.PORT_2, ev3_obj=vehicle)
      while True:
          dist = infrared.distance  # read distance
          if dist is None:
              print('\n' + '**** seen nothing ****')
	      vehicle.stop()
              break
  
          # get speed from speed controller
          speed = round(-speed_ctrl(dist))
          if speed > 100:
              speed = 100
          elif speed < -100:
              speed = -100
  
          vehicle.move(speed, 0)
          print(f'\rdistance: {dist:3.2f} m, speed: {speed:4d} %', end='')

          if speed == 0:
              break
  
          sleep(0.1)

Some remarks:
  - Line ``speed_ctrl = ev3.pid(0.2, 100)`` does the setup by calling
    :py:func:`~ev3_dc.pid`. *setpoint* is set to *0.2 m*, *gain* is
    set to *100*. The rule of thumb for setting *gain*: the sensor's
    measurement accuracy is *1 cm*, therefore a deviation of *1 cm*
    will result in a speed setting to *1* (percent of maximum speed).
  - A *setpoint* of *0.2 m* means: the vehicle adjusts to stand off
    this distance.
  - Line ``dist = infrared.distance`` does te measurement.
  - Line ``speed = round(-speed_ctrl(dist))`` calls the controller and
    gets *speed* as its signal setting. This programs inverts the
    signal because the controller regulates high values with small
    signals which in our situation is counterproductive.
  - The controller returns float values, but speed must be an integer.
    This is why the program rounds the controller's signal. It also
    restricts the signal (speed) to the range, which method
    :py:meth:`~ev3_dc.TwoWheelVehicle.move` accepts.
  - Line ``print(f'\rdistance: {dist:3.2f} m, speed: {speed:4d} %',
    end='')`` prints the measured *value* and the *signal* from the
    controller. This helps to quantify the visual impression.
  - A *P controller* is a quite simple thing. If you replace
    ``speed_ctrl(dist)`` by ``100 * (0.2 - dist)`` (or ``gain *
    (setpoint - value)``), you will see the very same behaviour of the
    vehicle.
  - The controller is called inside a loop and this loop sleeps 0.1
    sec. between each of its cycles. This time step is small enough
    to get the impression of a smooth adjustment.
  - Make your own experience, vary the *gain* and vary the time steps
    of the loop. High values of both result in overshooting and you
    will see the vehicle oscillating around the *setpoint*.


Keep the Distance
=================

We modify the program above. Now we add an integrative term to the
controller, which makes it a PI controller. We want the vehicle to
adjust to a dynamic situation. The vehicle has to follow the movements
of the barrier (e.g. your hand) in a constant distance.

The preparation is the same as above.  Place your hand in front of the
infrared sensor, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  # PI controller for vehicle speed
  speed_ctrl =  ev3.pid(0.2, 500, time_int=5)
  
  with ev3.TwoWheelVehicle(
      0.01518,  # radius_wheel
      0.11495,  # tread
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99'
  ) as vehicle:
      infrared = ev3.Infrared(ev3.PORT_2, ev3_obj=vehicle)
      while True:
          dist = infrared.distance  # read distance
          if dist is None:
              print('\n' + '**** seen nothing ****')
	      vehicle.stop()
              break
  
          # get speed from speed controller
          speed = round(-speed_ctrl(dist))
          if speed > 100:
              speed = 100
          elif speed < -100:
              speed = -100
  
          vehicle.move(speed, 0)
          print(f'\rdistance: {dist:3.2f} m, speed: {speed:4d} %', end='')
  
          sleep(0.1)

Some remarks:

  - A PI controller (here with an additional integrative term
    ``time_int=5``) helps to keep the distance at ``setpoint = 0.1
    m``, even when the barrier moves steady.
  - A P controller would not accomplish this. Let's say, the barrier
    moves with a speed of 50 (percent of the vehicles maximum
    speed). The P controller's balance distance will be larger than
    0.1 m. When we solve equation ``50 = -500 * (0.1 - dist)``, we get
    ``dist = 0.2``. This says: balanced state (vehicle and barrier
    move with the same speed) is reached at a distance of *0.20 m* and
    not at setpoint distance 0.1 m.
  - Again my advice: make your own experience, play around, vary the
    controller setup and compare the results.


Follow Me
=========

We modify the program once again and add a second controller, which
controls argument turn.

The preparation is the same as above. Additionally use a beacon,
select its channel 1 and switch it on. Place the beacon in front of
the infrared sensor, then start this program (switching off the beacon
ends this program):

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  speed_ctrl =  ev3.pid(0.1, 500, time_int=5)
  turn_ctrl = ev3.pid(0, 10)
  
  with ev3.TwoWheelVehicle(
      0.01518,  # radius_wheel
      0.11495,  # tread
      protocol=ev3.WIFI,
      host='00:16:53:42:2B:99'
  ) as vehicle:
      infrared = ev3.Infrared(ev3.PORT_2, ev3_obj=vehicle, channel=1)
      while True:
          beacon = infrared.beacon  # read position of infrared beacon
          if beacon is None:
              print('\n' + '**** lost connection ****')
              vehicle.stop()
              break
  
          # get speed from speed controller
          speed = round(-speed_ctrl(beacon.distance))
          if speed > 100:
              speed = 100
          elif speed < -100:
              speed = -100
  
          # get turn from turn controller
          turn = round(turn_ctrl(beacon.heading))
          if turn > 200:
              turn = 200
          elif turn < -200:
              turn = -200
  
          vehicle.move(speed, turn)
          print(
              f'\rspeed: {speed:4d} %, turn: {turn:4d}',
              end=''
          )
  
          sleep(0.1)

Some remarks:

  - This program uses two controllers, PI controller *speed_ctrl*
    regulates argument *speed*, P controller *turn_ctrl* regulates
    argument *turn*.
  - The balanced state of argument *turn* is zero. This is a clear hint
    to use a simple P controller.
  - As before, vary the setup, probably you will find a
    parametrization, which fits better than mine and results in a
    faster or smoother or even better adjustment.
  

