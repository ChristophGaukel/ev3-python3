#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - vehicle
"""

from math import pi, cos, sin, atan, radians, copysign, degrees, sqrt
from struct import unpack
from time import time
from numbers import Number, Integral
from thread_task import Task, Repeated
from ev3_dc.ev3 import EV3
from .constants import (
    BLUETOOTH,
    WIFI,
    opInput_Device,
    opOutput_Step_Sync,
    opOutput_Start,
    opOutput_Stop,
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
    READY_RAW,
    SYNC
)
from .functions import (
    LCX,
    GVX,
    port_motor_input
)


class TwoWheelVehicle(EV3):
    """
    EV3 vehicle with two drived Wheels
    """

    def __init__(
            self,
            radius_wheel: float,
            tread: float,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None
    ):
        """
        Establish a connection to a LEGO EV3 device

        Positional Arguments
          radius_wheel
            radius of the wheels im meter
          tread:
            the vehicles tread in meter

        Keyword Arguments (either protocol and host or ev3_obj)
          protocol
            BLUETOOTH == 'Bluetooth'
            USB == 'Usb'
            WIFI == 'Wifi'
          host
            mac-address of the LEGO EV3 (f.i. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object (its connections will be used)
        """
        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._radius_wheel = radius_wheel
        self._tread = tread
        self._polarity = 1
        self._port_left = PORT_D
        self._port_right = PORT_A
        self._orientation = 0.0
        self._pos_x = 0.0
        self._pos_y = 0.0
        self._orig_diff = None
        self._pos = None  # 0: left, 1: right
        self._turn = None
        self._speed = None
        self._moves = False
        self._last_t = None
        self._last_o = None
        self._last_pos = None
        self._to_stop = False
        self._test_args = None

    @property
    def polarity(self):
        """
        polarity of motor rotation (values: -1, 1, default: 1)
        """
        return self._polarity

    @polarity.setter
    def polarity(self, value: int):
        assert isinstance(value, int), "polarity needs to be of type int"
        assert value in [1, -1], "allowed polarity values are: -1 or 1"
        self._polarity = value

    @property
    def port_right(self):
        """
        port of right wheel (default: PORT_A)
        """
        return self._port_right

    @port_right.setter
    def port_right(self, value: int):
        assert isinstance(value, int), "port needs to be of type int"
        assert value in [PORT_A, PORT_B, PORT_C, PORT_D], \
            "value is not an allowed port"
        self._port_right = value

    @property
    def port_left(self):
        """
        port of left wheel (default: PORT_D)
        """
        return self._port_left

    @port_left.setter
    def port_left(self, value: int):
        assert isinstance(value, int), "port needs to be of type int"
        assert value in [PORT_A, PORT_B, PORT_C, PORT_D], \
            "value is not an allowed port"
        self._port_left = value

    @property
    def pos_x(self):
        """
        current x-component of the position in meter
        """
        return self._pos_x

    @property
    def pos_y(self):
        """
        current y-component of the position in meter
        """
        return self._pos_y

    @property
    def orientation(self):
        """
        current orientation of the vehicle in degree, range [-180 - 180]
        """
        o_tmp = self._orientation + 180
        o_tmp %= 360
        return o_tmp - 180

    class _Drive(Task):
        """
        modification of Task,
        which updates positions, when stopped
        """
        def stop(self):
            super().stop()
            if self._current is not None:
                self._current._gap = None

    def _reaction(self):
        """of connection protocol"""
        if self._protocol == BLUETOOTH:
            return 0.04
        elif self._protocol == WIFI:
            return 0.02
        else:
            return 0.01

    def _update(self, pos: list) -> None:
        """calculate new position of vehicle"""
        if self._pos is None:
            self._orig_diff = pos[1] - pos[0]
            self._pos = pos
            return
        step = [self._polarity * (pos[0] - self._pos[0]),
                self._polarity * (pos[1] - self._pos[1])]
        self._pos = pos
        # orientation
        diff = self._pos[1] - self._pos[0] - self._orig_diff
        self._orientation = (
            self._polarity * diff * self._radius_wheel / self._tread
        )
        # location
        if step[0] == 0 and step[1] == 0:
            pass
        elif self._turn == 0 or step[0] == step[1]:
            # straight
            dist = step[0] * 2 * pi * self._radius_wheel / 360
            self._pos_x += dist * cos(radians(self._orientation))
            self._pos_y += dist * sin(radians(self._orientation))
        else:
            # turn
            if not self._moves:
                radius_turn = (
                    0.5 * self._tread * (step[1] + step[0]) /
                    (step[1] - step[0])
                )
            elif self._turn > 0:
                radius_turn = self._tread * (100 / self._turn - 0.5)
            else:
                radius_turn = self._tread * (100 / self._turn + 0.5)
            angle = (step[1] - step[0]) * self._radius_wheel / self._tread
            angle += 180
            angle %= 360
            angle -= 180
            fact = 2.0 * radius_turn * sin(radians(0.5*angle))
            self._pos_x += (
                fact * cos(radians(self._orientation - 0.5*angle))
            )
            self._pos_y += (
                fact * sin(radians(self._orientation - 0.5*angle))
            )

    def _ops_pos(self):
        """read positions of the wheels (returns operations)"""
        return b''.join([
            opInput_Device,
            READY_RAW,
            LCX(0),  # LAYER
            port_motor_input(self._port_left),  # NO
            LCX(7),  # TYPE - EV3-Large-Motor
            LCX(1),  # MODE - Degree
            LCX(1),  # VALUES
            GVX(0),  # VALUE1
            opInput_Device,
            READY_RAW,
            LCX(0),  # LAYER
            port_motor_input(self._port_right),  # NO
            LCX(7),  # TYPE - EV3-Large-Motor
            LCX(0),  # MODE - Degree
            LCX(1),  # VALUES
            GVX(4)  # VALUE1
        ])

    def _test_o(self) -> float:
        """tests orientation, returns timespan to next call [s]"""
        direction, final_o, final_pos = self._test_args
        if self._to_stop:
            self._to_stop = False
            self._last_t = None
            self._update(final_pos)
            return -1
        if not self._last_t:
            first_call = True
            wait = 0.1
        else:
            first_call = False
            reply = self.send_direct_cmd(self._ops_pos(), global_mem=8)
            pos = unpack('<ii', reply[5:])
            self._update(pos)
            if direction > 0 and self._orientation >= final_o or \
               direction < 0 and self._orientation <= final_o:
                self._last_t = None
                return -1
            delta_t = time() - self._last_t
            delta_o = self._orientation - self._last_o
        self._last_t = time()
        self._last_o = self._orientation
        self._last_pos = self._pos
        if first_call:
            if abs(final_o - self._orientation) < 1:
                self._last_t = None
                return -1
            else:
                pass
        elif abs(delta_o) < 0.5:
            wait = 2*delta_t
        else:
            rest_o = final_o - self._orientation
            rest_t = delta_t * rest_o / delta_o - self._reaction()
            delta_t_new = min(2, 2*delta_t)
            if rest_t < (delta_t_new + 0.1):
                self._to_stop = True
                wait = rest_t
            else:
                wait = delta_t_new
        return wait

    def _test_pos(self) -> float:
        """tests position, returns timespan to next call [s]"""
        direction, final_pos = self._test_args
        if self._to_stop:
            self._to_stop = False
            self._last_t = None
            self._update(final_pos)
            return -1
        if not self._last_t:
            first_call = True
            wait = 0.1
        else:
            first_call = False
            reply = self.send_direct_cmd(self._ops_pos(), global_mem=8)
            pos = unpack('<ii', reply[5:])
            self._update(pos)
            if direction > 0 and self._pos[0] >= final_pos[0] or \
               direction < 0 and self._pos[0] <= final_pos[0]:
                self._last_t = None
                return -1
            delta_t = time() - self._last_t
            delta_pos = [self._pos[0] - self._last_pos[0],
                         self._pos[1] - self._last_pos[1]]
        self._last_t = time()
        self._last_pos = self._pos
        if first_call:
            pass
        elif abs(delta_pos[0]) < 0.001:
            wait = 2*delta_t
        else:
            rest_pos = final_pos[0] - self._pos[0]
            rest_t = delta_t * rest_pos / delta_pos[0] - self._reaction()
            delta_t_new = min(2, 2*delta_t)
            if rest_t < (delta_t_new + 0.1):
                self._to_stop = True
                wait = rest_t
            else:
                wait = delta_t_new
        return wait

    def move_task(
        self,
        speed: Integral,
        turn: Integral,
        duration: Number = None
    ) -> Task:
        """
        Start unlimited movement of the vehicle

        Positional Arguments
          speed
            speed in percent [-100 - 100]
              > 0: forward

              < 0: backward
          turn
            type of turn [-200 - 200]
              -200: circle right on place

              -100: turn right with unmoved right wheel

               0  : straight

              100: turn left with unmoved left wheel

              200: circle left on place

        Keyword Arguments
          duration
            duration of movement [s]

        Returns
          Task, which needs to be started or combined with other tasks
        """
        assert duration is not None or self._sync_mode != SYNC, \
            'no unlimited operations allowed in sync_mode SYNC'
        assert isinstance(speed, Integral), \
            "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, \
            "speed needs to be in range [-100 - 100]"
        assert isinstance(turn, Integral), \
            "turn needs to be an integer value"
        assert -200 <= turn and turn <= 200, \
            "turn needs to be in range [-200 - 200]"
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a positive number"
        assert duration is None or duration > 0, \
            "duration needs to be a positive number"

        if duration is None:
            return Task(
                self.move(speed, turn)
            )
        else:
            return Task(
                self.move(speed, turn),
                duration=duration
            )

    def move(self, speed: int, turn: int) -> None:
        """
        Start unlimited movement of the vehicle

        Positional Arguments
          speed
            speed in percent [-100 - 100]
              > 0: forward

              < 0: backward
          turn
            type of turn [-200 - 200]
              -200: circle right on place

              -100: turn right with unmoved right wheel

               0  : straight

              100: turn left with unmoved left wheel

              200: circle left on place
        """
        assert isinstance(speed, Integral), \
            "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, \
            "speed needs to be in range [-100 - 100]"
        assert isinstance(turn, Integral), \
            "turn needs to be an integer value"
        assert -200 <= turn and turn <= 200, \
            "turn needs to be in range [-200 - 200]"

        if self._polarity is -1:
            speed *= -1
        if self._port_left < self._port_right:
            turn *= -1
        ops = b''.join((
            opOutput_Step_Sync,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
            LCX(speed),
            LCX(turn),
            LCX(0),  # STEPS
            LCX(0),  # BRAKE
            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right)  # NOS
        ))
        pos = unpack(
            '<ii',
            self.send_direct_cmd(
                ops + self._ops_pos(),
                global_mem=8,
                sync_mode=SYNC
            )[5:]
        )
        if self._port_left < self._port_right:
            turn *= -1
        self._update(pos)
        self._turn = turn
        self._speed = speed
        self._moves = True

    def stop_task(
        self,
        brake: bool = False,
        duration: Number = None
    ) -> Task:
        """
        Stop any movement of the vehicle

        Keyword Arguments
          brake
            flag if activating brake
          duration
            duration of movement [s]

        Returns
          Task, which needs to be started or combined with other tasks
        """
        assert isinstance(brake, bool), \
            "brake needs to be a boolean value"
        assert duration is None or duration > 0, \
            "duration needs to be a positive number"
        assert duration is None or isinstance(duration, Number), \
            "duration needs to be a number"

        if duration is None:
            return Task(
                self._stop,
                args=(brake,)
            )
        else:
            return Task(
                self._stop,
                args=(brake,),
                duration=duration
            )

    def stop(self, brake: bool) -> None:
        """
        Stop movement of the vehicle

        Positional Arguments
          brake
            flag if activating brake
        """
        assert isinstance(brake, bool), \
            "brake needs to be a boolean value"

        brake_int = 1 if brake else 0
        ops = b''.join((
            opOutput_Stop,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
            LCX(brake_int)  # BRAKE
        ))
        pos = unpack(
            '<ii',
            self.send_direct_cmd(
                ops + self._ops_pos(),
                global_mem=8,
                sync_mode=SYNC
            )[5:]
        )
        self._update(pos)
        self._moves = False

    def drive_straight(
            self,
            speed: int,
            distance: float = None
    ) -> Task:
        """
        Drive the vehicle straight forward or backward.
        Keep in mind, it never stops, even when distance was set.
        At the end of the movement, there must be a stop.

        Positional Arguments
          speed
            in percent [-100 - 100] (direction depends on its sign)
              positive sign: forwards
              negative sign: backwards

        Optional Arguments
          distance
            in meter, needs to be positive
              if None, unlimited movement, returns immediately
              if set, returns, when movement is finished, but does not stop

        Returns
          Task, which needs to be started or combined with other tasks
        """
        assert isinstance(speed, int), \
            "speed needs to be an interger"
        assert speed >= -100 and speed <= 100, \
            "speed needs to be in range from -100 to 100 (inclusive)"
        assert distance is None or isinstance(distance, Number), \
            "distance needs to be a number"
        assert distance is None or distance > 0, \
            "distance needs to be positive"
        t = self._Drive(
            self._drive_straight,
            args=(speed, distance),
            action_stop=self._stop,
            args_stop=(False,),
            action_cont=self._vehicle_cont
        )
        if distance is None:
            return Task(t.start)
        else:
            t.append(
                Repeated(self._test_pos),
                copy=False
            )
            return Task(t.start, join=True)

    def _drive_straight(self, speed: int, distance: float) -> None:
        """starts straight movement and sets test arguments"""
        self.move(speed, 0)
        if distance is not None:
            direction = copysign(1, speed * self._polarity)
            step = round(distance * 360 / (2 * pi * self._radius_wheel))
            final_pos = [
                self._pos[0] + direction * step,
                self._pos[1] + direction * step
            ]
            self._test_args = (direction, final_pos)

    def drive_turn(
            self,
            speed: int,
            radius_turn: Number,
            angle: Number = None,
            right_turn: bool = False
    ) -> Task:
        """
        Drive the vehicle a turn with given radius.
        Keep in mind, it never stops, even when angle was set.
        At the end of the movement, there must be a stop.

        Positional arguments
          speed
            in percent [-100 - 100] (direction depends on its sign)
              positive sign: forwards
              negative sign: backwards
          radius_turn [m]
            positive sign: turn to the left side
            negative sign: turn to the right side

        Optional arguments
          angle
            absolute angle (needs to be positive)
            if None, unlimited movement
          right_turn
            flag of turn right (only in case of radius_turn == 0)

        Returns
          Task, which needs to be started or combined with other tasks
        """
        assert isinstance(radius_turn, Number), \
            "radius_turn needs to be a number"
        assert isinstance(right_turn, bool), "right_turn needs to be a boolean"
        assert not right_turn or radius_turn == 0, \
            "right_turn only can be set, when turning on place"
        assert angle is None or isinstance(angle, Number), \
            "angle needs to be a number"
        assert angle is None or angle > 0, "angle needs to be positive"
        t = self._Drive(
            self._drive_turn,
            args=(speed, radius_turn, angle, right_turn),
            action_stop=self._stop,
            args_stop=(False,),
            action_cont=self._vehicle_cont
        )
        if angle is None:
            return Task(t.start)
        else:
            t.append(
                Repeated(self._test_o),
                copy=False
            )
            return Task(t.start, join=True)

    def _drive_turn(
            self,
            speed: int,
            radius_turn: Number,
            angle: Number,
            right_turn: bool
    ) -> None:
        """starts turn movement and sets test arguments"""
        rad_right = radius_turn + 0.5 * self._tread
        rad_left = radius_turn - 0.5 * self._tread
        if radius_turn >= 0 and not right_turn:
            turn = round(100*(1 - rad_left / rad_right))
        else:
            turn = - round(100*(1 - rad_right / rad_left))
        if turn == 0:
            raise ValueError("radius_turn is too large")
        print(radius_turn, right_turn, speed, turn)
        self.move(speed, turn)
        if angle is not None:
            step_outer = (
                self._polarity * angle * rad_right / self._radius_wheel
            )
            step_inner = self._polarity * angle * rad_left / self._radius_wheel
            if radius_turn >= 0 and not right_turn:
                direction = copysign(1, speed)
                final_pos = [self._pos[0] + direction * step_inner,
                             self._pos[1] + direction * step_outer]
            else:
                direction = - copysign(1, speed)
                final_pos = [self._pos[0] - direction * step_outer,
                             self._pos[1] - direction * step_inner]
            final_o = self._orientation + direction * angle
            self._test_args = (direction, final_o, final_pos)

    def rotate_to(
            self,
            speed: int,
            orientation: float
    ) -> Task:
        """
        Rotate the vehicle to the given orientation.
        Keep in mind, it never stops.
        At the end of the movement, there must be a stop.

        Positional arguments
          speed
            in percent [-100 - 100] (direction depends on its sign)
              positive sign: forwards
              negative sign: backwards
          orientation
            in degrees, mathematical and relative to starting one
              positive: anti clockwise
              negative: clockwise

        Returns
          Task, which needs to be started or combined with other tasks
        """
        assert isinstance(speed, int), "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, \
            "speed needs to be in range [-100 - 100]"
        assert isinstance(orientation, Number), \
            "orientation needs to be a number"
        return Task(
            self._Drive(
                self._rotate_to,
                args=(speed, orientation),
                action_stop=self._stop,
                args_stop=(False,),
                action_cont=self._vehicle_cont
            ).append(
                Repeated(self._test_o),
                copy=False
            ).start,
            join=True
        )

    def _rotate_to(self, speed: int, orientation: float) -> None:
        """starts rotation movement and sets test arguments"""
        diff = orientation - self._orientation
        diff += 180
        diff %= 360
        diff -= 180
        if diff >= 0:
            right_turn = False
            direction = 1
        else:
            right_turn = True
            direction = -1
        if abs(diff) >= 1:
            o_orig = self._orientation
            self.drive_turn(speed, radius_turn=0, right_turn=right_turn)
            if diff > 0 and self._orientation > o_orig + diff:
                diff += 360
            elif diff < 0 and self._orientation < o_orig + diff:
                diff -= 360
        delta_pos = (
            self._polarity * diff * 0.5 * self._tread / self._radius_wheel
        )
        final_pos = [self._pos[0] - delta_pos,
                     self._pos[1] + delta_pos]
        self._test_args = (direction, o_orig + diff, final_pos)

    def drive_to(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> Task:
        """
        Drive the vehicle to the given position.
        Keep in mind, it never stops.
        At the end of the movement, there must be a stop.

        Positional Arguments
          speed
            in percent [-100 - 100] (direction depends on its sign)
              positive sign: forwards
              negative sign: backwards
          pos_x
            x-coordinate of target position
          pos_y
            y-coordinate of target position
        """
        assert isinstance(speed, int), "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, \
            "speed needs to be in range [-100 - 100]"
        assert isinstance(pos_x, Number), "pos_x needs to be a number"
        assert isinstance(pos_y, Number), "pos_y needs to be a number"
        return Task(
            self._Drive(
                self._drive_to_1,
                args=(speed, pos_x, pos_y),
                action_stop=self._stop,
                args_stop=(False,),
                action_cont=self._vehicle_cont
            ).append(
                Repeated(self._test_o),
                self._Drive(
                    self._drive_to_2,
                    args=(speed, pos_x, pos_y),
                    action_stop=self._stop,
                    args_stop=(False,),
                    action_cont=self._vehicle_cont
                ),
                Repeated(self._test_pos),
                copy=False
            ).start,
            join=True
        )

    def _drive_to_1(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> None:
        """first part: rotation"""
        diff_x = pos_x - self._pos_x
        diff_y = pos_y - self._pos_y
        if abs(diff_x) > abs(diff_y):
            direct = degrees(atan(diff_y/diff_x))
        else:
            fract = diff_x / diff_y
            sign = copysign(1, fract)
            direct = sign * 90 - degrees(atan(fract))
        if diff_x < 0:
            direct += 180
        self._rotate_to(speed, direct)

    def _drive_to_2(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> None:
        """second part: drive straight"""
        diff_x = pos_x - self._pos_x
        diff_y = pos_y - self._pos_y
        dist = sqrt(diff_x**2 + diff_y**2)
        self._drive_straight(speed, dist)

    def _vehicle_cont(self):
        """continue the stopped movement"""
        self.move(self._speed, self._turn)
        self._to_stop = False
        self._last_t = None


__all__ = [
    TwoWheelVehicle
]
