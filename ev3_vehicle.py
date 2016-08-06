#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 - vehicle
"""

# Copyright (C) 2016 Christoph Gaukel <christoph.gaukel@gmx.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import math
import struct
import time
import numbers
import ev3
import task

DRIVE_TYPE_STRAIGHT = "straight"
DRIVE_TYPE_TURN = "turn"
DRIVE_TYPE_ROTATE_TO = "rotate_to"
DRIVE_TYPE_DRIVE_TO = "drive_to"
DRIVE_TYPE_STOP = "stop"

# pylint: disable=too-many-instance-attributes
class TwoWheelVehicle(ev3.EV3):
    """
    ev3.EV3 vehicle with two drived Wheels
    """

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            radius_wheel: float,
            tread: float,
            protocol: str=None,
            host: str=None,
            ev3_obj: ev3.EV3=None
    ):
        """
        Establish a connection to a LEGO EV3 device

        Arguments:
        radius_wheel: radius of the wheels im meter
        tread: the vehicles tread in meter

        Keyword Arguments (either protocol and host or ev3_obj):
        protocol
          BLUETOOTH == 'Bluetooth'
          USB == 'Usb'
          WIFI == 'Wifi'
        host: mac-address of the LEGO EV3 (f.i. '00:16:53:42:2B:99')
        ev3_obj: an existing EV3 object (its connections will be used)
        """
        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._radius_wheel = radius_wheel
        self._tread = tread
        self._polarity = 1
        self._port_left = ev3.PORT_D
        self._port_right = ev3.PORT_A
        self._orientation = 0.0
        self._pos_x = 0.0
        self._pos_y = 0.0
        self._orig_diff = None
        self._pos = None        # 0: left, 1: right
        self._turn = None
        self._speed = None
        self._moves = False
        self._last_t = None
        self._last_o = None
        self._last_pos = None
        self._to_stop = False
        self._test_args = None
        # pylint: enable=too-many-arguments

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
        assert value in [ev3.PORT_A, ev3.PORT_B, ev3.PORT_C, ev3.PORT_D], \
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
        assert value in [ev3.PORT_A, ev3.PORT_B, ev3.PORT_C, ev3.PORT_D], \
            "value is not an allowed port"
        self._port_left = value


    @property
    def pos_x(self):
        """
        actual x-component of the position in meter
        """
        return self._pos_x

    @property
    def pos_y(self):
        """
        actual y-component of the position in meter
        """
        return self._pos_y

    @property
    def orientation(self):
        """
        actual orientation of the vehicle in degree, range [-180 - 180]
        """
        o_tmp = self._orientation + 180
        o_tmp %= 360
        return o_tmp - 180

    def _reaction(self):
        if self._protocol == ev3.BLUETOOTH:
            return 0.04
        elif self._protocol == ev3.WIFI:
            return 0.02
        else:
            return 0.01

    def _update(self, pos: list) -> None:
        """
        calculate new position of vehicle
        """
        if self._pos is None:
            self._orig_diff = pos[1] - pos[0]
            self._pos = pos
            return
        step = [self._polarity * (pos[0] - self._pos[0]),
                self._polarity * (pos[1] - self._pos[1])]
        self._pos = pos
        # orientation
        diff = self._pos[1] - self._pos[0] - self._orig_diff
        self._orientation = self._polarity * diff * self._radius_wheel / self._tread
        # location
        if step[0] == 0 and step[1] == 0:
            pass
        elif self._turn == 0 or step[0] == step[1]:
            # straight
            dist = step[0] * 2 * math.pi * self._radius_wheel / 360
            self._pos_x += dist * math.cos(math.radians(self._orientation))
            self._pos_y += dist * math.sin(math.radians(self._orientation))
        else:
            # turn
            if not self._moves:
                radius_turn = 0.5 * self._tread * (step[1] + step[0]) / (step[1] - step[0])
            elif self._turn > 0:
                radius_turn = self._tread * (100 / self._turn - 0.5)
            else:
                radius_turn = self._tread * (100 / self._turn + 0.5)
            angle = (step[1] - step[0]) * self._radius_wheel / self._tread
            angle += 180
            angle %= 360
            angle -= 180
            fact = 2.0 * radius_turn * math.sin(math.radians(0.5*angle))
            self._pos_x += fact * math.cos(math.radians(self._orientation - 0.5*angle))
            self._pos_y += fact * math.sin(math.radians(self._orientation - 0.5*angle))

    def _ops_pos(self):
        """
        read positions of the wheels (returns operations)
        """
        return b''.join([
            ev3.opInput_Device,
            ev3.READY_RAW,
            ev3.LCX(0),                             # LAYER
            ev3.port_motor_input(self._port_left),  # NO
            ev3.LCX(7),                             # TYPE - EV3-Large-Motor
            ev3.LCX(1),                             # MODE - Degree
            ev3.LCX(1),                             # VALUES
            ev3.GVX(0),                             # VALUE1
            ev3.opInput_Device,
            ev3.READY_RAW,
            ev3.LCX(0),                             # LAYER
            ev3.port_motor_input(self._port_right), # NO
            ev3.LCX(7),                             # TYPE - EV3-Large-Motor
            ev3.LCX(0),                             # MODE - Degree
            ev3.LCX(1),                             # VALUES
            ev3.GVX(4)                              # VALUE1
        ])

    def _test_o(self) -> float:
        (direction, final_o, final_pos) = self._test_args
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
            pos = struct.unpack('<ii', reply[5:])
            self._update(pos)
            if direction > 0 and self._orientation >= final_o or \
               direction < 0 and self._orientation <= final_o:
                self._last_t = None
                return -1
            delta_t = time.time() - self._last_t
            delta_o = self._orientation - self._last_o
        self._last_t = time.time()
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
        (direction, final_pos) = self._test_args
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
            pos = struct.unpack('<ii', reply[5:])
            self._update(pos)
            if direction > 0 and self._pos[0] >= final_pos[0] or \
               direction < 0 and self._pos[0] <= final_pos[0]:
                self._last_t = None
                return -1
            delta_t = time.time() - self._last_t
            delta_pos = [self._pos[0] - self._last_pos[0],
                         self._pos[1] - self._last_pos[1]]
        self._last_t = time.time()
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

    def move(self, speed: int, turn: int) -> None:
        """
        Start unlimited movement of the vehicle

        Arguments:
        speed: speed in percent [-100 - 100]
          > 0: forward
          < 0: backward
        turn: type of turn [-200 - 200]
          -200: circle right on place
          -100: turn right with unmoved right wheel
           0  : straight
           100: turn left with unmoved left wheel
           200: circle left on place
        """
        assert self._sync_mode != ev3.SYNC, 'no unlimited operations allowed in sync_mode SYNC'
        assert isinstance(speed, int), "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, "speed needs to be in range [-100 - 100]"
        assert isinstance(turn, int), "turn needs to be an integer value"
        assert -200 <= turn and turn <= 200, "turn needs to be in range [-200 - 200]"
        # if self._polarity_left is -1:
        #     if turn >= 0:
        #         turn = 200 - turn
        #     else:
        #         turn = -200 - turn
        #         speed *= -1
        # if self._polarity_right is -1:
        #     if turn >= 0:
        #         turn = 200 - turn
        #         speed *= -1
        #     else:
        #         turn = -200 - turn
        if self._polarity is -1:
            speed *= -1
        if self._port_left < self._port_right:
            turn *= -1
        ops = b''.join([
            ev3.opOutput_Step_Sync,
            ev3.LCX(0),                                  # LAYER
            ev3.LCX(self._port_left + self._port_right), # NOS
            ev3.LCX(speed),
            ev3.LCX(turn),
            ev3.LCX(0),                                  # STEPS
            ev3.LCX(0),                                  # BRAKE
            ev3.opOutput_Start,
            ev3.LCX(0),                                  # LAYER
            ev3.LCX(self._port_left + self._port_right)  # NOS
        ])
        reply = self.send_direct_cmd(ops + self._ops_pos(), global_mem=8)
        pos = struct.unpack('<ii', reply[5:])
        if self._port_left < self._port_right:
            turn *= -1
        self._update(pos)
        self._turn = turn
        self._speed = speed
        self._moves = True

    def stop(self, brake: bool=False) -> None:
        """
        Stop movement of the vehicle

        Arguments:
        brake: flag if activating brake
        """
        assert isinstance(brake, bool), "brake needs to be a boolean value"
        if brake:
            brake_int = 1
        else:
            brake_int = 0
        ops = b''.join([
            ev3.opOutput_Stop,
            ev3.LCX(0),                                  # LAYER
            ev3.LCX(self._port_left + self._port_right), # NOS
            ev3.LCX(brake_int)                           # BRAKE
        ])
        reply = self.send_direct_cmd(ops + self._ops_pos(), global_mem=8)
        pos = struct.unpack('<ii', reply[5:])
        self._update(pos)
        self._moves = False

    def drive_straight(self, speed: int, distance: float=None) -> None:
        """
        Drive the vehicle straight forward or backward.

        Attributes:
        speed: in percent [-100 - 100] (direction depends on its sign)
            positive sign: forwards
            negative sign: backwards

        Keyword Attributes:
        distance: in meter, needs to be positive
                  if None, unlimited movement
        """
        assert distance is None or isinstance(distance, numbers.Number), \
            "distance needs to be a number"
        assert distance is None or distance > 0, "distance needs to be positive"
        t_tmp = self.task_factory(
            DRIVE_TYPE_STRAIGHT,
            speed=speed,
            distance=distance
        )
        if distance is None:
            t_tmp.start()
        else:
            t_tmp.start().join()

    def _drive_straight(self, speed: int, distance: float) -> None:
        self.move(speed, 0)
        if distance != None:
            step = round(distance * 360 / (2 * math.pi * self._radius_wheel))
            direction = math.copysign(1, speed * self._polarity)
            final_pos = [self._pos[0] + direction * step,
                         self._pos[1] + direction * step]
            self._test_args = (direction, final_pos)

    def drive_turn(
            self,
            speed: int,
            radius_turn: float,
            angle: float=None,
            right_turn: bool=False
    ) -> None:
        """
        Drive the vehicle a turn with given radius.

        Attributes:
        speed: in percent [-100 - 100] (direction depends on its sign)
            positive sign: forwards
            negative sign: backwards
        radius_turn: in meter
            positive sign: turn to the left side
            negative sign: turn to the right side

        Keyword Attributes:
        angle: absolute angle (needs to be positive)
               if None, unlimited movement
        right_turn: flag of turn right (only in case of radius_turn == 0)
        """
        assert isinstance(radius_turn, numbers.Number), \
            "radius_turn needs to be a number"
        assert isinstance(right_turn, bool), "right_turn needs to be a boolean"
        assert not right_turn or radius_turn == 0, \
            "right_turn only can be set, when turning on place"
        assert angle is None or isinstance(angle, numbers.Number), \
            "angle needs to be a number"
        assert angle is None or angle > 0, "angle needs to be positive"
        t_tmp = self.task_factory(
            DRIVE_TYPE_TURN,
            speed=speed,
            radius_turn=radius_turn,
            angle=angle,
            right_turn=right_turn
        )
        if angle is None:
            t_tmp.start()
        else:
            t_tmp.start().join()

    def _drive_turn(
            self,
            speed: int,
            radius_turn: float,
            angle: float,
            right_turn: bool
    ) -> None:
        rad_right = radius_turn + 0.5 * self._tread
        rad_left = radius_turn - 0.5 * self._tread
        if radius_turn >= 0 and not right_turn:
            turn = round(100*(1 - rad_left / rad_right))
        else:
            turn = - round(100*(1 - rad_right / rad_left))
        if turn == 0:
            raise ValueError("radius_turn is too large")
        self.move(speed, turn)
        if angle != None:
            step_outer = self._polarity * angle * rad_right / self._radius_wheel
            step_inner = self._polarity * angle * rad_left / self._radius_wheel
            if radius_turn >= 0 and not right_turn:
                direction = math.copysign(1, speed)
                final_pos = [self._pos[0] + direction * step_inner,
                             self._pos[1] + direction * step_outer]
            else:
                direction = - math.copysign(1, speed)
                final_pos = [self._pos[0] - direction * step_outer,
                             self._pos[1] - direction * step_inner]
            final_o = self._orientation + direction * angle
            self._test_args = (direction, final_o, final_pos)

    def rotate_to(self, speed: int, orientation: float) -> None:
        """
        Rotate the vehicle to the given orientation.
        """
        assert isinstance(speed, int), "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, "speed needs to be in range [-100 - 100]"
        assert isinstance(orientation, numbers.Number), "orientation needs to be a number"
        self.task_factory(
            DRIVE_TYPE_ROTATE_TO,
            speed=speed,
            orientation=orientation
        ).start().join()

    def _rotate_to(self, speed: int, orientation: float) -> None:
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
        delta_pos = self._polarity * diff * 0.5 * self._tread / self._radius_wheel
        final_pos = [self._pos[0] - delta_pos,
                     self._pos[1] + delta_pos]
        self._test_args = (direction, o_orig + diff, final_pos)

    def drive_to(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> None:
        """
        Drive the vehicle to the given position.

        Attributes:
        speed: in percent [-100 - 100] (direction depends on its sign)
            positive sign: forwards
            negative sign: backwards
        pos_x: x-coordinate of target position
        pos_y: y-coordinate of target position
        """
        assert isinstance(speed, int), "speed needs to be an integer value"
        assert -100 <= speed and speed <= 100, "speed needs to be in range [-100 - 100]"
        assert isinstance(pos_x, numbers.Number), "pos_x needs to be a number"
        assert isinstance(pos_y, numbers.Number), "pos_y needs to be a number"
        self.task_factory(
            DRIVE_TYPE_DRIVE_TO,
            speed=speed,
            pos_x=pos_x,
            pos_y=pos_y
        ).start().join()

    def _drive_to_1(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> None:
        diff_x = pos_x - self._pos_x
        diff_y = pos_y - self._pos_y
        if abs(diff_x) > abs(diff_y):
            direct = math.degrees(math.atan(diff_y/diff_x))
        else:
            fract = diff_x / diff_y
            sign = math.copysign(1, fract)
            direct = sign * 90 - math.degrees(math.atan(fract))
        if diff_x < 0:
            direct += 180
        self._rotate_to(speed, direct)

    def _drive_to_2(
            self,
            speed: int,
            pos_x: float,
            pos_y: float
    ) -> None:
        diff_x = pos_x - self._pos_x
        diff_y = pos_y - self._pos_y
        dist = math.sqrt(diff_x**2 + diff_y**2)
        self._drive_straight(speed, dist)

    def task_factory(self, drive_type: str, **kwargs) -> task.Task:
        """
        Returns as Task object, which moves or stops the vehicle

        Arguments:
        drive_type: type of movement
          'straight':  keyword arguments are speed,
                       distance (optional for delimited movements)
          'turn':      keyword arguments are speed, radius_turn,
                       angle (optional for delimited movements),
                       right_turn (optional for turns on place)
          'stop':      keyword argument is brake (optional)
          'rotate_to': keyword arguments are speed, orientation
          'drive_to':  keyword arguments are speed, pos_x, pos_y

        Keyword Arguments:
        speed: int=None -- speed in percent [-100 - 100] (direction depends on its sign)
            positive sign: forwards
            negative sign: backwards
        distance: float=None -- distance in meter, needs to be positive
        radius_turn: float=None -- radius of turn in meter
            positive sign: turn to the left side
            negative sign: turn to the right side
        angle: float=None -- absolute angle (needs to be positive)
        right_turn: bool=False -- flag if turn right (only in case of radius_turn == 0)
        pos_x: float=None -- x-component of position in meter
        pos_y: float=None -- y-component of position in meter
        brake: bool=False -- flag if stopping with activated brake
        exc: ExceptionHandler=None -- exception handler to coordinate exceptions
        """
        speed = kwargs.pop('speed', None)
        distance = kwargs.pop('distance', None)
        radius_turn = kwargs.pop('radius_turn', None)
        angle = kwargs.pop('angle', None)
        right_turn = kwargs.pop('right_turn', False)
        orientation = kwargs.pop('orientation', None)
        pos_x = kwargs.pop('pos_x', None)
        pos_y = kwargs.pop('pos_y', None)
        brake = kwargs.pop('brake', False)
        exc = kwargs.pop('exc', None)
        assert isinstance(drive_type, str), 'drive_type needs to be a str type'
        assert drive_type in [
            DRIVE_TYPE_STRAIGHT,
            DRIVE_TYPE_TURN,
            DRIVE_TYPE_ROTATE_TO,
            DRIVE_TYPE_DRIVE_TO,
            DRIVE_TYPE_STOP
        ], 'unknown drive_type: ' + drive_type
        assert speed is None or isinstance(speed, int), \
            'speed needs to be an integer'
        assert speed != None or drive_type is DRIVE_TYPE_STOP, \
            drive_type + ' needs attribute speed'
        assert drive_type is DRIVE_TYPE_STOP or isinstance(speed, int), \
            drive_type + ' needs parameter speed'
        assert distance is None or isinstance(distance, numbers.Number), \
            "distance needs to be a number"
        assert distance is None or distance >= 0, \
            "distance needs to be positive"
        assert radius_turn is None or isinstance(radius_turn, numbers.Number), \
            "radius_turn needs to be a number"
        assert angle is None or isinstance(angle, numbers.Number), \
            "angle needs to be a number"
        assert isinstance(right_turn, bool), \
            "right_turn needs to be a bool value"
        assert orientation is None or isinstance(orientation, numbers.Number), \
            "orientation needs to be a number"
        assert pos_x is None or isinstance(pos_x, numbers.Number), \
            "pos_x needs to be a number"
        assert pos_y is None or isinstance(pos_y, numbers.Number), \
            "pos_y needs to be a number"
        assert drive_type != DRIVE_TYPE_TURN or radius_turn != None, \
            DRIVE_TYPE_TURN + ' needs parameter radius_turn'
        assert drive_type != DRIVE_TYPE_ROTATE_TO or orientation != None, \
            DRIVE_TYPE_ROTATE_TO + ' needs parameter orientation'
        assert drive_type != DRIVE_TYPE_DRIVE_TO or pos_x != None, \
            DRIVE_TYPE_DRIVE_TO + ' needs parameter pos_x'
        assert drive_type != DRIVE_TYPE_DRIVE_TO or pos_y != None, \
            DRIVE_TYPE_DRIVE_TO + ' needs parameter pos_y'
        assert isinstance(brake, bool), \
            "brake needs to be a bool value"
        assert exc is None or isinstance(exc, task.ExceptionHandler), \
            "exc needs to be an ExceptionHandler"
        if not exc:
            exc = task.Task.exc_default

        class _Drive(task.Task):
            def stop(self):
                super().stop()
                self._time_action = time.time()

        # pylint: disable=redefined-variable-type
        if drive_type == DRIVE_TYPE_STRAIGHT:
            t_inner = _Drive(
                self._drive_straight,
                args=(speed, distance),
                action_stop=self.stop,
                action_cont=self._vehicle_cont,
                exc=exc
            )
            if distance != None:
                t_inner.append(task.Repeated(self._test_pos))
        elif drive_type == DRIVE_TYPE_TURN:
            t_inner = _Drive(
                self._drive_turn,
                args=(speed, radius_turn, angle, right_turn),
                action_stop=self.stop,
                action_cont=self._vehicle_cont,
                exc=exc
            )
            if angle != None:
                t_inner.append(task.Repeated(self._test_o))
        elif drive_type == DRIVE_TYPE_ROTATE_TO:
            t_inner = task.concat(
                _Drive(
                    self._rotate_to,
                    args=(speed, orientation),
                    action_stop=self.stop,
                    action_cont=self._vehicle_cont,
                    exc=exc
                ),
                task.Repeated(self._test_o)
            )
        elif drive_type == DRIVE_TYPE_DRIVE_TO:
            t_inner = task.concat(
                _Drive(
                    self._drive_to_1,
                    args=(speed, pos_x, pos_y),
                    action_stop=self.stop,
                    action_cont=self._vehicle_cont,
                    exc=exc,
                ),
                task.Repeated(self._test_o),
                task.Task(
                    self._drive_to_2,
                    args=(speed, pos_x, pos_y)
                ),
                task.Repeated(self._test_pos)
            )
        elif drive_type == DRIVE_TYPE_STOP:
            t_inner = task.Task(
                self.stop,
                args=(brake,),
                exc=exc
            )
        # pylint: enable=redefined-variable-type
        if drive_type is DRIVE_TYPE_STRAIGHT and distance is None or \
           drive_type is DRIVE_TYPE_TURN and angle is None:
            return task.Task(t_inner.start, exc=exc)
        else:
            return task.Task(t_inner.start, join=True, exc=exc)

    def _vehicle_cont(self):
        self.move(self._speed, self._turn)
        self._to_stop = False
        self._last_t = None
