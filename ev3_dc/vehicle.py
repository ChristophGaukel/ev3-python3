#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - vehicle
"""

from math import pi, cos, sin, atan, radians, copysign, degrees, sqrt
from struct import unpack
from time import time
from numbers import Number, Integral
from thread_task import Task, Repeated, Periodic
from .ev3 import EV3
from .constants import (
    BLUETOOTH,
    WIFI,
    opInput_Device,
    opOutput_Step_Sync,
    opOutput_Start,
    opOutput_Stop,
    opOutput_Reset,
    opOutput_Clr_Count,
    opOutput_Test,
    opMove32_32,
    opMove8_8,
    opMove32_F,
    opMoveF_16,
    opJr_Gteq32,
    opJr_Gteq8,
    opJr_Eq32,
    opJr_Lt32,
    opAdd32,
    opSub32,
    opSubF,
    opMul32,
    opMul16,
    opMul8,
    opMulF,
    opDivF,
    opMath,
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
    READY_RAW,
    GET_TYPEMODE,
    SYNC,
    ROUND
)
from .functions import (
    LCX,
    GVX,
    LVX,
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
            ev3_obj: EV3 = None,
            speed: Integral = 10,
            delta_time: Number = None,
            port_left: bytes = PORT_A,
            port_right: bytes = PORT_D,
            polarity_left: Integral = 1,
            polarity_right: Integral = 1
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
          speed
            percentage of maximum speed [1 - 100] (default is 10)
          delta_time
            timespan between  introspections [s]
            (default depends on protocol,
            USB: 0.2 sec., WIFI: 0.1 sec., USB: 0.05 sec.)
          port_left
            port of left motor (PORT_A, PORT_B, PORT_C or PORT_D)
          port_right
            port of right motor (PORT_A, PORT_B, PORT_C or PORT_D)
          polarity_left
            polarity of left motor rotation (values: -1, 1, default: 1)
          polarity_right
            polarity of right motor rotation (values: -1, 1, default: 1)
        """
        assert isinstance(speed, Integral), \
            "speed needs to be an integer"
        assert speed > 0, \
            "speed needs to be positive"
        assert speed <= 100, \
            "speed needs to be lower or equal 100"

        assert delta_time is None or isinstance(delta_time, Number), \
            "delta_time needs to be a number"
        assert delta_time is None or delta_time > 0, \
            "delta_time needs to be positive"

        assert isinstance(port_left, int), \
            "port_left needs to be an integer"
        assert port_left in (PORT_A, PORT_B, PORT_C, PORT_D), \
            "port_left needs to be one of (PORT_A, PORT_B, PORT_C, PORT_D)"

        assert isinstance(port_right, int), \
            "port_right needs to be an integer"
        assert port_right in (PORT_A, PORT_B, PORT_C, PORT_D), \
            "port_right needs to be one of (PORT_A, PORT_B, PORT_C, PORT_D)"
        assert port_left != port_right, \
            'port_left must be different from port_right'

        assert polarity_left in (-1, 1), \
            "polarity_left needs to be -1 or 1"
        assert polarity_right in (-1, 1), \
            "polarity_right needs to be -1 or 1"

        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._radius_wheel = radius_wheel
        self._tread = tread

        self._type_left = None
        self._type_right = None
        self._motor_pos = None

        self._speed = speed
        self._current_movement = None
        self._target_motor_pos = None
        self._motor_pos = None
        self._position = 0., 0.

        if delta_time is not None:
            self._delta_time = delta_time
        elif self._physical_ev3._protocol == BLUETOOTH:
            self._delta_time = .2
        elif self._physical_ev3._protocol == WIFI:
            self._delta_time = .1
        else:
            self._delta_time = .05

        self._port_left = port_left
        self._port_right = port_right

        self._polarity_left = polarity_left
        self._polarity_right = polarity_right

    @property
    def polarity_left(self):
        """
        polarity of left motor rotation (values: -1, 1, default: 1)
        """
        return self._polarity_left

    @polarity_left.setter
    def polarity_left(self, value: int):
        assert isinstance(value, int), "polarity_left needs to be of type int"
        assert value in (1, -1), "allowed polarity_left values are: -1 or 1"
        self._polarity_left = value

    @property
    def polarity_right(self):
        """
        polarity of left motor rotation (values: -1, 1, default: 1)
        """
        return self._polarity_right

    @polarity_right.setter
    def polarity_right(self, value: int):
        assert isinstance(value, int), "polarity_right needs to be of type int"
        assert value in (1, -1), "allowed polarity_right values are: -1 or 1"
        self._polarity_right = value

    @property
    def port_right(self):
        """
        port of right wheel (default: PORT_A)
        """
        return self._port_right

    @port_right.setter
    def port_right(self, value: int):
        assert isinstance(value, int), "port needs to be of type int"
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
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
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
            "value is not an allowed port"
        self._port_left = value

    @property
    def position(self):
        """
        current vehicle position (x- and y-components) in meters
        """
        return self._position

    @property
    def orientation(self):
        """
        current orientation of the vehicle in degrees, range [-180 - 180]
        """
        return (
            (
                self._polarity_right * self._motor_pos[1] -
                self._polarity_left * self._motor_pos[0]
            ) *
            self._radius_wheel / self._tread +
            180
        ) % 360 - 180

    @property
    def busy(self) -> bool:
        """
        Flag if motors are currently busy
        """
        data = unpack(
            '<2i2B',
            self.send_direct_cmd(
                self._ops_pos() + self._ops_busy(global_offset=8),
                global_mem=10,
                sync_mode=SYNC
            )
        )
        self._update_vehicle_pos((data[0], data[1]))

        return True if data[2] or data[3] else False

    def _ops_busy(self, global_offset=0):
        """reads busy state of motors (returns operations)
        GVX(global_offset) - busy state of left motor (DATA8)
        GVX(global_offset + 1) - busy state of right motor (DATA9)
        """
        return b''.join((
            opOutput_Test,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NOS
            GVX(global_offset),  # BUSY (DATA8) - output

            opOutput_Test,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NOS
            GVX(global_offset + 1)  # BUSY (DATA8) - output
        ))

    def _ops_pos(self, global_offset=0):
        """read positions of the wheels (returns operations)
        GVX(global_offset) - position of left motor (DATA32)
        GVX(global_offset + 4) - position of right motor (DATA32)
        """
        return b''.join((
            opInput_Device,
            READY_RAW,
            LCX(0),  # LAYER
            port_motor_input(self._port_left),  # NO
            LCX(7),  # TYPE - EV3-Large-Motor
            LCX(1),  # MODE - Degree
            LCX(1),  # VALUES
            GVX(global_offset),  # VALUE1

            opInput_Device,
            READY_RAW,
            LCX(0),  # LAYER
            port_motor_input(self._port_right),  # NO
            LCX(7),  # TYPE - EV3-Large-Motor
            LCX(0),  # MODE - Degree
            LCX(1),  # VALUES
            GVX(global_offset + 4)  # VALUE1
        ))

    def _ops_init(self, local_offset=0, global_offset=0):
        """read positions of the wheels (returns operations)
        GVX(global_offset) - type of left motor (DATA8)
        GVX(global_offset + 1) - type of right motor (DATA8)
        """
        return b''.join((
            opInput_Device,
            GET_TYPEMODE,  # CMD
            LCX(0),  # LAYER
            port_motor_input(self._port_left),  # NO
            GVX(global_offset),  # TYPE (output)
            LVX(local_offset),  # MODE (output)

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NOS

            opOutput_Clr_Count,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NO

            opInput_Device,
            GET_TYPEMODE,  # CMD
            LCX(0),  # LAYER
            port_motor_input(self._port_right),  # NO
            GVX(global_offset + 1),  # TYPE (output)
            LVX(local_offset + 1),  # MODE (output)

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NOS

            opOutput_Clr_Count,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NO
        ))

    def _update_vehicle_pos(self, motor_pos: tuple) -> None:
        """update vehicle position and orientation"""
        steps = (
            self._polarity_left * (motor_pos[0] - self._motor_pos[0]),
            self._polarity_right * (motor_pos[1] - self._motor_pos[1])
        )
        self._motor_pos = motor_pos

        if steps[0] == 0 and steps[1] == 0:
            # no movement
            return

        # current orientation
        orientation = (
            (
                self._polarity_right * self._motor_pos[1] -
                self._polarity_left * self._motor_pos[0]
            ) *
            self._radius_wheel / self._tread +
            180
        ) % 360 - 180

        if steps[0] == steps[1]:
            # straight
            dist = steps[0] * 2 * pi * self._radius_wheel / 360

            vehicle_pos_x, vehicle_pos_y = self._position
            vehicle_pos_x += dist * cos(radians(orientation))
            vehicle_pos_y += dist * sin(radians(orientation))
            self._position = vehicle_pos_x, vehicle_pos_y
            return

        angle = (
            (steps[1] - steps[0]) *
            self._radius_wheel / self._tread +
            180
        ) % 360 - 180
        radius_turn = (
            0.5 * self._tread * (steps[1] + steps[0]) /
            (steps[1] - steps[0])
        )
        fact = 2.0 * radius_turn * sin(radians(0.5 * angle))

        vehicle_pos_x, vehicle_pos_y = self._position
        vehicle_pos_x += (
            fact * cos(radians(orientation - 0.5 * angle))
        )
        vehicle_pos_y += (
            fact * sin(radians(orientation - 0.5 * angle))
        )
        self._position = vehicle_pos_x, vehicle_pos_y

    def stop(self, brake: bool = False) -> None:
        '''stops the current motor movements, sets or releases brake

        Keyword Arguments

          brake
            flag if stopping with active brake
        '''
        assert isinstance(brake, bool), \
            'brake must be a boolean'

        ops_stop = b''.join((
            opOutput_Stop,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
            LCX(1 if brake else 0),  # BRAKE - 0 (no), 1 (yes)
        ))
        data = unpack(
            '<2i',
            self.send_direct_cmd(
                self._ops_pos() + ops_stop,
                global_mem=8,
                sync_mode=SYNC
            )
        )
        self._update_vehicle_pos((data[0], data[1]))

        if self._current_movement is not None:
            self._current_movement['stopped'] = True

    def cont(self):
        if self._current_movement is None:
            # movement was already finished
            return

        assert 'stopped' in self._current_movement, \
            "can't continue unstopped movement"

        if self._current_movement['op'] == 'Step_Sync':
            self._move_motors_to(
                self._current_movement['target_motor_pos'],
                speed=self._current_movement['speed'],
                brake=self._current_movement['brake'],
                _controlled=True
            )

        else:
            raise RuntimeError('unknown operation in current movement')

    def start_straight(
        self,
        distance: Number,
        speed: Integral = None,
        brake: bool = True,
        _controlled: bool = False
    ) -> None:
        '''start moving the vehicle straight by a given distance
        (without time control).

        Positional Arguments

          distance
            direction (sign) and distance (meters) of straight movement

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]

          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        assert isinstance(distance, Number), \
            'distance needs to be a number'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        steps = round(distance * 360 / (2 * pi * self._radius_wheel))

        if self._target_motor_pos is not None:
            self._move_motors_to(
                (
                    self._target_motor_pos[0] + self._polarity_left * steps,
                    self._target_motor_pos[1] + self._polarity_right * steps
                ),
                speed=speed,
                brake=brake,
                _controlled=_controlled
            )
        else:
            self._move_motors_by(
                (
                    self._polarity_left * steps,
                    self._polarity_right * steps
                ),
                speed=speed,
                brake=brake,
                _controlled=_controlled
            )

    def start_turn(
            self,
            angle: Number,
            radius: Number,
            back: bool = False,
            speed: Integral = None,
            brake: bool = True,
            _controlled: bool = False
    ) -> None:
        '''start moving the vehicle in a turn of given radius and angle
        (without time control).

        Positional Arguments

          angle
            angle of turn (degrees),
            positive sign: to the left,
            negative sign: to the right
          radius
            radius of turn (meters)

        Keyword Arguments

          back
            flag if backwards (reverse movement of radius, -angle)
          speed
            percentage of maximum speed [1 - 100]
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        assert isinstance(radius, Number) and radius >= 0, \
            'radius needs to be a positive number'

        assert isinstance(angle, Number), \
            'angle needs to be a number'

        assert isinstance(back, bool), \
            'back needs to be a boolean'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'

        assert self._current_movement is None, \
            'concurrent movement in progress'
        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        radius_outer = radius + 0.5 * self._tread
        radius_inner = radius - 0.5 * self._tread

        turn = round(100 * (1 - radius_outer / radius_inner))
        if turn == 0:
            raise ValueError("radius is too large")

        if not back and angle >= 0 or back and angle < 0:
            radius_left = radius_inner
            radius_right = radius_outer
        else:
            radius_left = radius_outer
            radius_right = radius_inner

        steps_left = round(
            self._polarity_left * abs(angle) * radius_left /
            self._radius_wheel
        )
        steps_right = round(
            self._polarity_right * abs(angle) * radius_right /
            self._radius_wheel
        )
        if back:
            steps_left *= -1
            steps_right *= -1

        if self._target_motor_pos is not None:
            self._move_motors_to(
                (
                    self._target_motor_pos[0] +
                    self._polarity_left * steps_left,
                    self._target_motor_pos[1] +
                    self._polarity_right * steps_right
                ),
                speed=speed,
                brake=brake,
                _controlled=_controlled
            )
        else:
            self._move_motors_by(
                (
                    self._polarity_left * steps_left,
                    self._polarity_right * steps_right
                ),
                speed=speed,
                brake=brake,
                _controlled=_controlled
            )

    def task_turn(
            self,
            angle: Number,
            radius: Number,
            back: bool = False,
            speed: Integral = None,
            brake: bool = True,
            duration: Number = None
    ) -> Task:
        '''start moving the vehicle in a turn of given radius and angle
        (without time control).

        Positional Arguments

          angle
            angle of turn (degrees),
            positive sign: to the left,
            negative sign: to the right
          radius
            radius of turn (meters)

        Keyword Arguments

          back
            flag if backwards (reverse movement of radius, -angle)
          speed
            percentage of maximum speed [1 - 100]
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        assert isinstance(radius, Number) and radius >= 0, \
            'radius needs to be a positive number'

        assert isinstance(angle, Number), \
            'angle needs to be a number'

        assert isinstance(back, bool), \
            'back needs to be a boolean'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        t_start = Task(
            self.start_turn,
            args=(angle, radius),
            kwargs={
                'back': back,
                'speed': speed,
                'brake': brake,
                '_controlled': True
            },
            duration=self._delta_time,
            action_stop=self.stop,
            args_stop=(False,),
            action_cont=self.cont
        )

        return Task(
            t_start + Periodic(self._delta_time, self._control_periodic),
            duration=duration
        )

    def _control_periodic(self):
        '''Periodic needs inverse flag of property busy'''
        if self._current_movement is None:
            # prevent needless data traffic
            return True
        if self._current_movement['op'] != 'Step_Sync':
            RuntimeError('concurrent movements')

        if self.busy:
            print('0.0 inside _control_periodic', self._current_movement)
            return False
        else:
            self._target_motor_pos = (
                self._current_movement['target_motor_pos']
            )
            self._current_movement = None
            return True

    def task_straight(
        self,
        distance: Number,
        speed: Integral = None,
        brake: bool = True,
        duration: Number = None
    ) -> Task:
        '''start moving the vehicle straight by a given distance
        (without time control).

        Positional Arguments

          distance
            direction (sign) and distance (meters) of straight movement

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]

          brake
            Flag if ending with floating motors (False) or active brake (True).

        Returns

          Task object, that can be started, stopped and continued.
        '''
        assert isinstance(distance, Number), \
            'distance needs to be a number'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        assert duration is None or isinstance(duration, Number), \
            'duration needs to be a number'
        assert duration is None or duration > 0, \
            'duration needs to be positive'

        t_start = Task(
            self.start_straight,
            args=(distance,),
            kwargs={
                'speed': speed,
                'brake': brake,
                '_controlled': True
            },
            duration=self._delta_time,
            action_stop=self.stop,
            args_stop=(False,),
            action_cont=self.cont
        )

        return Task(
            t_start + Periodic(self._delta_time, self._control_periodic),
            duration=duration
        )

    def _move_motors_by(
            self,
            diff_motor_pos: tuple,
            speed: Integral = None,
            brake: bool = True,
            _controlled: bool = False
    ):
        '''start moving the motors to given positions (without time control).

        Positional Arguments

          diff_motor_pos
            difference of motor positions (degrees), left and right

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]
          brake
            flag if ending with floating motor (False) or active brake (True).
        '''
        assert (
            isinstance(diff_motor_pos, tuple) and
            len(diff_motor_pos) == 2 and
            isinstance(diff_motor_pos[0], Integral) and
            isinstance(diff_motor_pos[1], Integral)
        ), 'diff_motor_pos needs to be a tuple of two integer numbers'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'

        assert isinstance(_controlled, bool), \
            '_controlled needs to be a boolean'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        steps_left = diff_motor_pos[0]
        steps_right = diff_motor_pos[1]

        if abs(steps_left) + abs(steps_right) == 0:
            # no movement
            return

        # steps and turn
        if abs(steps_right) >= abs(steps_left):
            steps = abs(steps_right)
            if steps_right < 0:
                speed *= -1
            turn = round(100*(1 - steps_left / steps_right))
        else:
            steps = abs(steps_left)
            if steps_left < 0:
                speed *= -1
            turn = round(100*(steps_right / steps_left - 1))

        # if reverse ports then reverse turn
        if self._port_left < self._port_right:
            turn *= -1

        if self._type_left is None:
            ops = self._ops_init()
        else:
            ops = b''.join((
                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port_left),  # NOS

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port_right),  # NOS
            )) + self._ops_pos()

        ops += b''.join((
            opOutput_Step_Sync,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
            LCX(speed),
            LCX(turn),
            LCX(steps),
            LCX(0),  # BRAKE

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right)  # NOS
        ))

        if self._type_left is None:
            self._type_left, self._type_right = unpack(
                '<BB',
                self.send_direct_cmd(
                    ops,
                    local_mem=2,
                    global_mem=2,
                    sync_mode=SYNC
                )
            )
            self._motor_pos = (0, 0)
        else:
            motor_pos = unpack(
                '<ii',
                self.send_direct_cmd(ops, global_mem=8, sync_mode=SYNC)
            )
            self._update_vehicle_pos(motor_pos)

        if _controlled:
            self._current_movement = {
                'op': 'Step_Sync',
                'speed': speed,
                'brake': brake,
                'target_motor_pos': (
                    self._motor_pos[0] + diff_motor_pos[0],
                    self._motor_pos[1] + diff_motor_pos[1]
                )
            }
        else:
            self._target_motor_pos = None
            self._current_movement = None

    def _move_motors_to(
            self,
            target_motor_pos: tuple,
            speed: Integral = None,
            brake: bool = True,
            _controlled: bool = False
    ):
        '''start moving the motors to given positions (without time control).

        Positional Arguments

          target_motor_pos
            target motor positions (degrees), left and right

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]
          brake
            flag if ending with floating motor (False) or active brake (True).
        '''
        assert (
            isinstance(target_motor_pos, tuple) and
            len(target_motor_pos) == 2 and
            isinstance(target_motor_pos[0], Integral) and
            isinstance(target_motor_pos[1], Integral)
        ), 'target_motor_pos needs to be a tuple of two integer numbers'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'

        assert isinstance(_controlled, bool), \
            '_controlled needs to be a boolean'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        if self._type_left is None:
            return self._move_motors_by(
                target_motor_pos,
                speed=speed,
                brake=brake,
                _controlled=_controlled
            )

        ops = b''.join((
            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NOS

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NOS
        )) + self._ops_pos()
        ops += b''.join((
            opMove32_F,
            LCX(1),  # SOURCE
            LVX(24),  # DESTINATION - const 1.0 (DATAF)

            opSub32,
            LCX(target_motor_pos[0]),  # SOURCE1 - target_pos_left (DATA32)
            GVX(0),  # SOURCE2 - pos_left (DATA32)
            LVX(0),  # DESTINATION - steps_left (DATA32)

            opSub32,
            LCX(target_motor_pos[1]),  # SOURCE1 - target_pos_right
            GVX(4),  # SOURCE2 - pos_right (DATA32)
            LVX(4),  # DESTINATION - steps_right (DATA32)

            opMove32_32,
            LVX(0),  # SOURCE - steps_left (DATA32)
            LVX(8),  # DESTINATION - steps_left (DATA32)

            opJr_Gteq32,
            LVX(0),  # LEFT - steps_left (DATA32)
            LCX(0),  # RIGHT
            LCX(4),  # OFFSET

            opMul32,
            LVX(0),  # SOURCE1 - steps_left (DATA32)
            LCX(-1),  # SOURCE2
            LVX(8),  # DESTINATION - abs(steps_left) (DATA32)

            opMove32_32,
            LVX(4),  # SOURCE - steps_left (DATA32)
            LVX(12),  # DESTINATION - steps_left (DATA32)

            opJr_Gteq32,
            LVX(4),  # LEFT - steps_right (DATA32)
            LCX(0),  # RIGHT
            LCX(4),  # OFFSET

            opMul32,
            LVX(4),  # SOURCE1 - steps_right (DATA32)
            LCX(-1),  # SOURCE2
            LVX(12),  # DESTINATION - abs(steps_right) (DATA32)

            opAdd32,
            LVX(8),  # SOURCE1 - abs(steps_left) (DATA32)
            LVX(12),  # SOURCE2 - abs(steps_right) (DATA32)
            LVX(16),  # DESTINATION - abs(steps_left) + abs(steps_right)

            opMove8_8,
            LCX(speed),  # SOURCE
            LVX(20),  # DESTINATION - speed (DATA8)

            opJr_Eq32,  # 0x6E
            LVX(16),  # LEFT - abs(steps_left) + abs(steps_right)
            LCX(0),  # RIGHT
            LCX(91),  # OFFSET

            # === abs(steps_left) + abs(steps_right) != 0

            opJr_Lt32,  # 0x66
            LVX(12),  # LEFT - abs(steps_right) (DATA32)
            LVX(8),  # RIGHT - abs(steps_left) (DATA32)
            LCX(25),  # OFFSET

            # === abs(steps_right) >= abs(steps_left)

            opMove32_32,  # 0x3A
            LVX(12),  # SOURCE - abs(steps_right) (DATA32)
            LVX(16),  # DESTINATION - steps (DATA32)

            opJr_Gteq32,  # 0x7A
            LVX(4),  # LEFT - steps_right (DATA32)
            LCX(0),  # RIGHT
            LCX(4),  # OFFSET

            opMul8,
            LVX(20),  # SOURCE1 - speed (DATA8)
            LCX(-1),  # SOURCE2
            LVX(20),  # DESTINATION - speed (DATA8)

            opMove32_F,
            LVX(0),  # SOURCE - steps_left (DATA32)
            LVX(0),  # DESTINATION - steps_left (DATAF)

            opMove32_F,
            LVX(4),  # SOURCE - steps_right (DATA32)
            LVX(4),  # DESTINATION - steps_right (DATAF)

            opDivF,
            LVX(0),  # SOURCE1 - steps_left (DATAF)
            LVX(4),  # SOURCE2 - steps_right (DATAF)
            LVX(4),  # DESTINATION - tmp (DATAF)

            opSubF,
            LVX(24),  # SOURCE1 - const 1.0 (DATAF)
            LVX(4),  # SOURCE2 - tmp (DATAF)
            LVX(4),  # DESTINATION - tmp (DATAF)

            opJr_Gteq32,  # 0x7A
            LVX(12),  # LEFT - abs(steps_right) (DATA32)
            LVX(8),  # RIGHT - abs(steps_left) (DATA32)
            LCX(25),  # OFFSET

            # === abs(steps_right) < abs(steps_left)

            opMove32_32,  # 0x3A
            LVX(8),  # SOURCE - abs(steps_left) (DATA32)
            LVX(16),  # DESTINATION - steps (DATA32)

            opJr_Gteq32,
            LVX(0),  # LEFT - steps_left (DATA32)
            LCX(0),  # RIGHT
            LCX(4),  # OFFSET

            opMul8,
            LVX(20),  # SOURCE1 - speed (DATA8)
            LCX(-1),  # SOURCE2
            LVX(20),  # DESTINATION - speed (DATA8)

            opMove32_F,
            LVX(0),  # SOURCE - steps_left (DATA32)
            LVX(0),  # DESTINATION - steps_left (DATAF)

            opMove32_F,
            LVX(4),  # SOURCE - steps_right (DATA32)
            LVX(4),  # DESTINATION - steps_right (DATAF)

            opDivF,
            LVX(4),  # SOURCE1 - steps_right (DATAF)
            LVX(0),  # SOURCE2 - steps_left (DATAF)
            LVX(4),  # DESTINATION - tmp (DATAF)

            opSubF,
            LVX(4),  # SOURCE1 - tmp (DATAF)
            LVX(24),  # SOURCE2 - const 1.0 (DATAF)
            LVX(4),  # DESTINATION - tmp (DATAF)

            opMove32_F,  # 0x3B
            LCX(100),  # SOURCE
            LVX(0),  # DESTINATION - const 100.0 (DATAF)

            opMulF,  # 0x1B
            LVX(0),  # SOURCE1 - const 100.0 (DATAF)
            LVX(4),  # SOURCE2 - tmp (DATAF)
            LVX(4),  # DESTINATION - tmp (DATAF)

            opMath,  # 0x8D
            ROUND,  # CMD
            LVX(4),  # DATA X - tmp (DATAF)
            LVX(4),  # RESULT - turn (DATAF)

            opMoveF_16,  # 0x3D
            LVX(4),  # SOURCE - tmp (DATAF)
            LVX(4),  # DESTINATION - turn (DATA16)

            # === if reverse ports then reverse turn

            opJr_Gteq8,  # 0x78
            LCX(self._port_left),  # LEFT
            LCX(self._port_right),  # RIGHT
            LCX(4),  # OFFSET

            opMul16,
            LCX(-1),  # SOURCE1
            LVX(4),  # SOURCE2 - turn (DATA16)
            LVX(4),  # DESTINATION - turn (DATA16)

            # === start movement

            opOutput_Step_Sync,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
            LVX(20),  # SPEED
            LVX(4),  # TURN
            LVX(16),  # STEPS
            LCX(1 if brake else 0),  # BRAKE

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS
        ))

        motor_pos = unpack(
            '<ii',
            self.send_direct_cmd(
                ops,
                local_mem=28,
                global_mem=8,
                sync_mode=SYNC
            )
        )
        self._update_vehicle_pos(motor_pos)

        if _controlled:
            self._current_movement = {
                'op': 'Step_Sync',
                'speed': speed,
                'brake': brake,
                'target_motor_pos': target_motor_pos
            }
        else:
            self._target_motor_pos = None
            self._current_movement = None


class TwoWheelVehicleOld(EV3):
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
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
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
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
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
        current orientation of the vehicle in degrees, range [-180 - 180]
        """
        return (self._orientation + 180) % 360 - 180

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
            pos = unpack(
                '<ii',
                self.send_direct_cmd(
                    self._ops_pos(),
                    global_mem=8,
                    sync_mode=SYNC
                )
            )
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
            pos = unpack(
                '<ii',
                self.send_direct_cmd(
                    self._ops_pos(),
                    global_mem=8,
                    sync_mode=SYNC
                )
            )
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

        if self._polarity == -1:
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
            )
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
            )
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
