'''
LEGO Mindstorms EV3 direct commands - vehicle
'''

from typing import Tuple, Callable
from math import pi, cos, sin, radians, copysign, sqrt
from decimal import Decimal
from struct import unpack
from numbers import Number
from collections import namedtuple
from thread_task import Task, Repeated
from .ev3 import EV3
from .constants import (
    BLUETOOTH,
    WIFI,
    EV3_LARGE_MOTOR,
    EV3_MEDIUM_MOTOR,
    opInput_Device,
    opOutput_Step_Sync,
    opOutput_Step_Speed,
    opOutput_Start,
    opOutput_Stop,
    opOutput_Reset,
    opOutput_Clr_Count,
    opOutput_Test,
    opMove32_32,
    opMove32_F,
    opOr8,
    opJr_False,
    opJr_Eq32,
    opJr_Neq32,
    opJr_Lt32,
    opJr_Gt32,
    opJr_Lteq32,
    opJr_Gteq32,
    opJr_GteqF,
    opAdd32,
    opSub32,
    opMul32,
    opDivF,
    opMath,
    ABS,
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
    READY_RAW
)
from .functions import (
    LCX,
    GVX,
    LVX,
    port_motor_input
)
from .exceptions import MotorError


VehiclePosition = namedtuple('VehiclePosition', [
        'x',
        'y',
        'o'
])
MotorPositions = namedtuple('MotorPositions', [
        'left',
        'right'
])


class _Tracking:
    '''
    does position and orientation tracking of a vehicle
    '''
    def __init__(
            self,
            radius_wheel: Number,
            tread: Number,
            motor_pos: Tuple[int],
            *,
            polarity_left: int = 1,
            polarity_right: int = 1,
            callback=None
    ):
        '''
        Mandatory positional arguments

          radius_wheel
            radius of the wheels [m]
          tread:
            the vehicles tread [m]
          motor_pos
            current positions of left and right motor [degree]

        Optional keyword only arguments

          polarity_left
            polarity of left motor rotation, values: -1, 1 (default)
          polarity_right
            polarity of right motor rotation, values: -1, 1 (default)
        '''
        assert isinstance(radius_wheel, Number), \
            "radius_wheel needs to be a number"
        assert radius_wheel > 0, \
            "radius_wheel needs to be positive"

        assert isinstance(tread, Number), \
            "tread needs to be a number"
        assert tread > 0, \
            "tread needs to be positive"

        assert isinstance(polarity_left, int), \
            'polarity_left must be an integer'
        assert polarity_left in (-1, 1), \
            "polarity_left needs to be -1 or 1"
        assert isinstance(polarity_right, int), \
            'polarity_right must be an integer'
        assert polarity_right in (-1, 1), \
            "polarity_right needs to be -1 or 1"
        assert callback is None or isinstance(callback, Callable), \
            "callback must be a callable"

        super().__init__()

        self._radius_wheel = radius_wheel
        self._tread = tread
        self._polarity_left = polarity_left
        self._polarity_right = polarity_right

        self._motor_pos = motor_pos
        self._position = 0., 0.
        self._callback = callback


    @property
    def position(self) -> VehiclePosition:
        '''
        current vehicle position (as named tuple)

        x and x-coordinates are in meters,
        orientation is in degrees [-180 - 180]
        '''
        return VehiclePosition(
            self._position[0],
            self._position[1],
            (
                (
                    self._polarity_right * self._motor_pos[1] -
                    self._polarity_left * self._motor_pos[0]
                ) *
                self._radius_wheel / self._tread +
                180
            ) % 360 - 180
        )


    @property
    def motor_pos(self) -> MotorPositions:
        '''
        current position of the left and right motor [degree]
        '''
        return MotorPositions(*self._motor_pos)


    def update(self, motor_pos: Tuple[int]) -> None:
        '''
        update vehicle position and orientation
        '''
        if (
                motor_pos[0] == self._motor_pos[0] and
                motor_pos[1] == self._motor_pos[1]
        ):
            # no movement
            return

        steps = (
            self._polarity_left * (motor_pos[0] - self._motor_pos[0]),
            self._polarity_right * (motor_pos[1] - self._motor_pos[1])
        )
        self._motor_pos = motor_pos

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
        if self._callback is not None:
            self._callback(self.position)


class TwoWheelVehicle(EV3):
    '''
    EV3 vehicle with two drived wheels
    '''

    def __init__(
            self,
            radius_wheel: Number,
            tread: Number,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            speed: int = 10,
            ramp_up: int = 30,
            ramp_down: int = 30,
            delta_time: Number = None,
            port_left: bytes = PORT_A,
            port_right: bytes = PORT_D,
            polarity_left: int = 1,
            polarity_right: int = 1,
            tracking_callback: Callable = None,
            verbosity: int = 0
    ):
        '''
        Establishes a connection to a LEGO EV3 device

        Mandatory positional arguments

          radius_wheel
            radius of the wheels [m]
          tread:
            the vehicles tread [m]

        Keyword only arguments (either protocol and host or ev3_obj)

          protocol
            BLUETOOTH == 'Bluetooth',
            USB == 'Usb',
            WIFI == 'WiFi'
          host
            mac-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object (its connections will be used)
          speed
            percentage of maximum speed [1 - 100] (default is 10)
          ramp_up
            degrees for ramp-up (default is 30)
          ramp_down
            degrees for ramp-down (default is 30)
          delta_time
            timespan between  introspections [s]
            (default depends on protocol,
            USB: 0.2 sec., WIFI: 0.1 sec., USB: 0.05 sec.)
          port_left
            port of left motor (PORT_A, PORT_B, PORT_C or PORT_D)
          port_right
            port of right motor (PORT_A, PORT_B, PORT_C or PORT_D)
          polarity_left
            polarity of left motor rotation, values: -1, 1 (default)
          polarity_right
            polarity of right motor rotation, values: -1, 1 (default)
          tracking_callback
            callable, which frequently tells current position,
            its single argument must be of type VehiclePosition
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout)
        '''
        assert isinstance(radius_wheel, Number), \
            "radius_wheel needs to be a number"
        assert radius_wheel > 0, \
            "radius_wheel needs to be positive"

        assert isinstance(tread, Number), \
            "tread needs to be a number"
        assert tread > 0, \
            "tread needs to be positive"

        assert isinstance(speed, int), \
            "speed needs to be an integer"
        assert speed > 0, \
            "speed needs to be positive"
        assert speed <= 100, \
            "speed needs to be lower or equal 100"

        assert isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up >= 0, \
            "ramp_up must be positive"

        assert isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down >= 0, \
            "ramp_down must be positive"

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

        assert isinstance(polarity_left, int), \
            'polarity_left must be an integer'
        assert polarity_left in (-1, 1), \
            "polarity_left needs to be -1 or 1"
        assert isinstance(polarity_right, int), \
            'polarity_right must be an integer'
        assert polarity_right in (-1, 1), \
            "polarity_right needs to be -1 or 1"
        assert (
            tracking_callback is None or
            isinstance(tracking_callback, Callable)
        ), "tracking_callback must be a callable"

        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)

        self._radius_wheel = radius_wheel
        self._tread = tread

        self._speed = speed
        self._current_movement = None
        self._target_motor_pos = None

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

        self._ramp_up = ramp_up
        self._ramp_down = ramp_down

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)

        if self.sensors_as_dict[port_motor_input(self._port_left)] not in (
                EV3_LARGE_MOTOR,
                EV3_MEDIUM_MOTOR
        ):
            if self._port_left == PORT_A:
                port_str = 'PORT_A'
            elif self._port_left == PORT_B:
                port_str = 'PORT_B'
            elif self._port_left == PORT_C:
                port_str = 'PORT_C'
            else:
                port_str = 'PORT_D'
            raise MotorError('no motor connected at ' + port_str)

        if self.sensors_as_dict[port_motor_input(self._port_right)] not in (
                EV3_LARGE_MOTOR,
                EV3_MEDIUM_MOTOR
        ):
            if self._port_right == PORT_A:
                port_str = 'PORT_A'
            elif self._port_right == PORT_B:
                port_str = 'PORT_B'
            elif self._port_right == PORT_C:
                port_str = 'PORT_C'
            else:
                port_str = 'PORT_D'
            raise MotorError('no motor connected at ' + port_str)

        self.send_direct_cmd(
            b''.join((
                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port_left + self._port_right),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port_left + self._port_right)  # NO
            ))
        )

        self._tracking = _Tracking(
            self._radius_wheel,
            self._tread,
            (0, 0),  # motor_pos
            polarity_left=self._polarity_left,
            polarity_right=self._polarity_right,
            callback=tracking_callback
        )


    def __str__(self):
        '''
        description of the object in a str context
        '''
        return ' '.join((
            'TwoWheelVehicle',
            f'of {super().__str__()}'
        ))

    @property
    def speed(self) -> int:
        '''
        speed as percentage of maximum speed [1 - 100]
        '''
        return self._speed

    @speed.setter
    def speed(self, value: int):
        assert isinstance(value, int), \
            "speed needs to be an integer"
        assert value > 0, \
            "speed needs to be positive"
        assert value <= 100, \
            "speed needs to be lower or equal 100"
        self._speed = value

    @property
    def ramp_up(self) -> int:
        '''
        degrees for ramp-up
        '''
        return self._ramp_up

    @ramp_up.setter
    def ramp_up(self, value: int):
        assert isinstance(value, int), \
            "ramp_up must be an int"
        assert value >= 0, \
            "ramp_up must be positive"
        self._ramp_up = value

    @property
    def ramp_down(self) -> int:
        '''
        degrees for ramp-down
        '''
        return self._ramp_down

    @ramp_down.setter
    def ramp_down(self, value: int):
        assert isinstance(value, int), \
            "ramp_down must be an int"
        assert value >= 0, \
            "ramp_down must be positive"
        self._ramp_down = value

    @property
    def polarity_left(self) -> int:
        '''
        polarity of left motor rotation (values: -1, 1, default: 1)
        '''
        return self._polarity_left

    @polarity_left.setter
    def polarity_left(self, value: int):
        assert isinstance(value, int), "polarity_left needs to be of type int"
        assert value in (1, -1), "allowed polarity_left values are: -1 or 1"
        self._polarity_left = value

    @property
    def polarity_right(self) -> int:
        '''
        polarity of left motor rotation (values: -1, 1, default: 1)
        '''
        return self._polarity_right

    @polarity_right.setter
    def polarity_right(self, value: int):
        assert isinstance(value, int), "polarity_right needs to be of type int"
        assert value in (1, -1), "allowed polarity_right values are: -1 or 1"
        self._polarity_right = value

    @property
    def port_right(self) -> bytes:
        '''
        port of right wheel (default: PORT_A)
        '''
        return self._port_right

    @port_right.setter
    def port_right(self, value: int):
        assert isinstance(value, int), "port needs to be of type int"
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
            "value is not an allowed port"
        self._port_right = value

    @property
    def port_left(self) -> bytes:
        '''
        port of left wheel (default: PORT_D)
        '''
        return self._port_left

    @port_left.setter
    def port_left(self, value: int):
        assert isinstance(value, int), "port needs to be of type int"
        assert value in (PORT_A, PORT_B, PORT_C, PORT_D), \
            "value is not an allowed port"
        self._port_left = value

    @property
    def position(self) -> VehiclePosition:
        '''
        current vehicle position (as named tuple)

        x and x-coordinates are in meter,
        orientation is in degree [-180 - 180]
        '''
        self._tracking.update(
            unpack(
                '<2i',
                self.send_direct_cmd(
                    self._ops_pos(),
                    global_mem=8
                )
            )
        )
        return self._tracking.position

    @property
    def motor_pos(self) -> MotorPositions:
        '''
        current positions of left and right motor [degree] (as named tuple)
        '''
        self._tracking.update(
            unpack(
                '<2i',
                self.send_direct_cmd(
                    self._ops_pos(),
                    global_mem=8
                )
            )
        )
        return self._tracking.motor_pos

    @property
    def busy(self) -> bool:
        '''
        Flag if motors are currently busy
        '''
        data = unpack(
            '<2i2B',
            self.send_direct_cmd(
                self._ops_pos() + self._ops_busy(global_offset=8),
                global_mem=10
            )
        )
        self._tracking.update(data[:2])
        return any(data[2:])

    @property
    def tracking_callback(self) -> Callable:
        '''
        callable, which frequently tells current vehicle position,
        its single argument must be of type VehiclePosition
        '''
        return self._tracking_callback
    
    @tracking_callback.setter
    def tracking_callback(self, value):
        assert (
            value is None or
            isinstance(value, Callable)
        ), "tracking_callback must be a callable"
        self._tracking_callback = value

    def _ops_busy(self, global_offset=0) -> bytes:
        '''reads busy state of motors (returns operations)
        GVX(global_offset) - busy state of left motor (DATA8)
        GVX(global_offset + 1) - busy state of right motor (DATA9)
        '''
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

    def _ops_pos(self, global_offset=0) -> bytes:
        '''
        read positions of the wheels (returns operations)
        GVX(global_offset) - position of left motor (DATA32)
        GVX(global_offset + 4) - position of right motor (DATA32)
        '''
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
        self._tracking.update(
            unpack(
                '<2i',
                self.send_direct_cmd(
                    self._ops_pos() + ops_stop,
                    global_mem=8
                )
            )
        )
        if self._current_movement is not None:
            self._current_movement['stopped'] = True


    def cont(self) -> None:
        '''
        continues stopped movement
        '''
        if self._current_movement is None:
            # movement was already finished
            return

        assert 'stopped' in self._current_movement, \
            "can't continue unstopped movement"

        if self._current_movement['op'] == 'Step_Speed':
            self._start_move_to(
                self._current_movement['target_motor_pos'],
                speed=self._current_movement['speed'],
                ramp_up=self._current_movement['ramp_up'],
                ramp_down=self._current_movement['ramp_down'],
                brake=self._current_movement['brake'],
                _control=True
            )
        else:
            raise RuntimeError('unknown op in current movement')


    def move(
            self,
            speed: int,
            turn: int
    ) -> None:
        """
        Starts unlimited synchronized movement of the vehicle

        Mandatory positional arguments

          speed
            direction (sign) and speed of movement 
            as percentage of maximum speed [-100 - 100]

          turn
            type of turn [-200 - 200]
              -200: circle right on place

              -100: turn right with unmoved right wheel

               0  : straight

              100: turn left with unmoved left wheel

              200: circle left on place
        """
        assert isinstance(turn, int), \
            "turn needs to be an integer"
        assert -200 <= turn <= 200, \
            "turn needs to be in range [-200 - 200]"

        assert isinstance(speed, int), \
            "speed needs to be an integer"
        assert -100 <= speed <= 100, \
            "speed needs to be in range [-100 - 100]"

        if self._polarity_left == -1 and self._polarity_left == -1:
            speed *= -1
        elif self._polarity_left == -1:
            if turn >= 0:
                turn = 200 - turn
            else:
                speed *= -1
                turn = -200 - turn
        elif self._polarity_right == -1:
            if turn >= 0:
                speed *= -1
                turn = 200 - turn
            else:
                turn = -200 - turn

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
        data = unpack(
            '<2i',
            self.send_direct_cmd(
                self._ops_pos() + ops,
                global_mem=8
            )
        )
        self._tracking.update(data)


    def _control(self):
        '''
        controls current movement (must be called by a Repeated)
        '''

        def direct_cmd():
            '''
            reads current motor positions and busy state,
            then modifies the speed of the inner wheel, which needs to do
            a number of calculations.

            The speed is lowered down if:
                - abs(done_inner / done_outer) is too high and
                  abs(last_inner / last_outer) also is too high.

            The speed is accelerated if:
                - abs(done_inner / done_outer) is too low and
                  abs(last_inner / last_outer) also is too low.

            In both cases abs(all_inner / all_outer) is the reference.
            Whenever the speed changes, step2 must be recalculated and
            finally opOutput_Step_Speed does the change of the movement.
            All this is done in a single direct command,
            which minimizes the communication
            '''
            ops = b''.join((
                # input --> global_mem
                opMove32_32,
                LCX(speed),
                GVX(8),

                # input --> local_mem
                opMove32_32,  # b'\x3A'
                LCX(start_pos_inner),
                LVX(0),
                opMove32_32,  # b'\x3A'
                LCX(start_pos_outer),
                LVX(4),
                opMove32_32,  # b'\x3A'
                LCX(target_pos_inner),
                LVX(8),
                opMove32_32,  # b'\x3A'
                LCX(target_pos_outer),
                LVX(12),
                opMove32_32,  # b'\x3A'
                LCX(last_pos_inner),
                LVX(16),
                opMove32_32,  # # b'\x3A'
                LCX(last_pos_outer),
                LVX(20),
                opMove32_32,  # b'\x3A'
                LCX(step1),
                LVX(24),
                opMove32_32,  # b'\x3A'
                LCX(step2),
                LVX(28),
                opMove32_32,  # b'\x3A'
                LCX(step3),
                LVX(32),
                opMove32_32,  # b'\x3A'
                LCX(speed),
                LVX(56),  # speed_orig

                opInput_Device,  # b'\x98'
                READY_RAW,
                LCX(0),  # LAYER
                port_motor_input(port_inner),  # NO
                LCX(7),  # TYPE - EV3-Large-Motor
                LCX(1),  # MODE - Degree
                LCX(1),  # VALUES
                GVX(0),  # VALUE1

                opInput_Device,  # b'\x98'
                READY_RAW,
                LCX(0),  # LAYER
                port_motor_input(port_outer),  # NO
                LCX(7),  # TYPE - EV3-Large-Motor
                LCX(0),  # MODE - Degree
                LCX(1),  # VALUES
                GVX(4),  # VALUE1

                opOutput_Test,  # b'\xA9'
                LCX(0),  # LAYER
                LCX(port_inner),  # NOS
                GVX(12),  # BUSY (DATA8) - output

                opOutput_Test,  # b'\xA9'
                LCX(0),  # LAYER
                LCX(port_outer),  # NOS
                GVX(13),  # BUSY (DATA8) - output

                # if not (busy_inner or busy_outer): return

                opOr8,  # b'\x20'
                GVX(12),  # SOURCE1
                GVX(13),  # SOURCE2
                LVX(60),  # busy_inner or busy_outer

                opJr_False,  # b'\x41'
                LVX(60),  # FLAG
                LCX(263),  # OFFSET

                opSub32,  # b'\x16'
                GVX(0),
                LVX(0),
                LVX(36),  # done_inner = pos_inner - start_pos_inner

                opMove32_32,  # b'\x3A'
                LVX(36),
                LVX(40),  # will become abs(done_inner)

                opJr_Gteq32,  # b'\x7A'
                LVX(36),  # done_inner
                LCX(0),
                LCX(6),  # OFFSET

                opMul32,  # b'\x1A'
                LVX(36),
                LCX(-1),
                LVX(40),  # abs(done_inner)

                # if abs(done_inner) < step1: return

                opJr_Lt32,  # b'\x66'
                LVX(40),  # abs(done_inner)
                LVX(24),  # step1
                LCX(235),  # OFFSET

                # if abs(done_inner) > (step1 + step2): return

                opAdd32,  # b'\x12'
                LVX(24),  # step1
                LVX(28),  # step2
                LVX(44),  # step1 + step2

                opJr_Gt32,  # b'\x6A'
                LVX(40),  # abs(done_inner)
                LVX(44),  # step1 + step2
                LCX(222),  # OFFSET

                opSub32,  # b'\x16'
                GVX(4),
                LVX(4),
                LVX(40),  # done_outer = pos_outer - start_pos_outer

                opMove32_F,  # b'\x3B'
                LVX(40),
                LVX(40),  # done_outer as DATAF

                opMove32_F,  # b'\x3B'
                LVX(36),
                LVX(44),  # done_inner as DATAF

                opDivF,  # b'\x1F'
                LVX(44),
                LVX(40),
                LVX(40),  # done_inner / done_outer

                opMath,  # b'\x8D'
                ABS,
                LVX(40),
                LVX(40),  # ratio_done

                opSub32,  # b'\x16'
                GVX(0),
                LVX(16),
                LVX(44),  # last_inner = pos_inner - last_pos_inner

                opMove32_F,  # b'\x3B'
                LVX(44),
                LVX(44),  # last_inner as DATAF

                opSub32,  # b'\x16'
                GVX(4),
                LVX(20),
                LVX(48),  # last_outer = pos_outer - last_pos_outer

                opMove32_F,  # b'\x3B'
                LVX(48),
                LVX(48),  # last_outer as DATAF

                opDivF,  # b'\x1F'
                LVX(44),
                LVX(48),
                LVX(44),  # last_inner / last_outer

                opMath,  # b'\x8D'
                ABS,
                LVX(44),
                LVX(44),  # ratio_last

                opSub32,  # b'\x16'
                LVX(8),
                LVX(0),
                LVX(48),  # all_inner = target_pos_inner - start_pos_inner

                opMove32_F,  # b'\x3B'
                LVX(48),
                LVX(52),  # all_inner as DATAF

                opSub32,  # b'\x16'
                LVX(12),
                LVX(4),
                LVX(56),  # all_outer = target_pos_outer - start_pos_outer

                opMove32_F,  # b'\x3B'
                LVX(56),
                LVX(56),  # all_outer as DATAF

                opDivF,  # b'\x1F'
                LVX(52),
                LVX(56),
                LVX(52),  # all_inner / all_outer

                opMath,  # b'\x8D'
                ABS,
                LVX(52),
                LVX(52),  # ratio_all

                # skip slow down

                opJr_GteqF,  # b'\x7B'
                LVX(52),  # ratio_all
                LVX(44),  # ratio_last
                LCX(22),

                opJr_GteqF,  # b'\x7B'
                LVX(52),  # ratio_all
                LVX(40),  # ratio_done
                LCX(16),

                # slow down speed

                opJr_Lteq32,  # b'\x76'
                GVX(8),  # speed
                LCX(0),
                LCX(4),  # OFFSET

                opSub32,  # b'\x16'
                GVX(8),
                LCX(1),
                GVX(8),  # speed -= 1

                opJr_Gteq32,  # b'\x7A'
                GVX(8),  # speed
                LCX(0),
                LCX(4),

                opAdd32,  # b'\x12'
                GVX(8),
                LCX(1),
                GVX(8),  # speed += 1

                # skip accelerate

                opJr_Eq32,  # b'\x6E'
                GVX(8),  # speed
                LCX(100),
                LCX(54),  # OFFSET

                opJr_Eq32,  # b'\x6E'
                GVX(8),  # speed
                LCX(-100),
                LCX(48),  # OFFSET

                opJr_GteqF,  # b'\x7B'
                LVX(44),  # ratio_last
                LVX(52),  # ratio_all
                LCX(41),  # OFFSET

                opJr_GteqF,  # b'\x7B'
                LVX(40),  # ratio_done
                LVX(52),  # ratio_all
                LCX(34),  # OFFSET

                # accelerate speed

                opJr_Neq32,  # b'\x72'
                GVX(8),  # speed
                LCX(0),
                LCX(5),  # OFFSET

                opJr_Lt32,  # b'\x66'
                LVX(48),  # all_inner
                LCX(0),
                LCX(9),  # OFFSET

                opJr_Lt32,  # b'\x66'
                GVX(8),  # speed
                LCX(0),
                LCX(4),  # OFFSET

                opAdd32,  # b'\x12'
                GVX(8),
                LCX(1),
                GVX(8),  # speed += 1

                opJr_Neq32,  # b'\x72'
                GVX(8),  # speed
                LCX(0),
                LCX(5),  # OFFSET

                opJr_Gt32,  # b'\x6A'
                LVX(48),  # all_inner
                LCX(0),
                LCX(8),  # OFFSET

                opJr_Gt32,  # b'\x6A'
                GVX(8),  # speed
                LCX(0),
                LCX(4),  # OFFSET

                opSub32,  # b'\x16'
                GVX(8),
                LCX(1),
                GVX(8),  # speed -= 1

                # if speed == speed_orig: return

                opJr_Eq32,  # b'\x6E'
                GVX(8),  # speed
                LVX(56),
                LCX(34),  # OFFSET

                # determine step2

                opSub32,  # b'\x16'
                LVX(48),
                LVX(36),
                LVX(0),  # all_inner - done_inner

                opJr_Gteq32,  # b'\x7A'
                LVX(0),  # all_inner - done_inner
                LCX(0),
                LCX(4),  # OFFSET

                opMul32,  # b'\x1A'
                LVX(0),
                LCX(-1),
                LVX(0),  # abs(all_inner - done_inner)

                opSub32,  # b'\x16'
                LVX(0),  # abs(all_inner - done_inner)
                LVX(32),  # step3
                LVX(28),  # step2

                # modify movement

                opOutput_Reset,  # b'\xA2'
                LCX(0),  # LAYER
                LCX(port_inner),  # NOS

                opOutput_Step_Speed,  # b'\xAE'
                LCX(0),  # LAYER
                LCX(port_inner),  # NOS
                GVX(8),  # SPEED
                LCX(0),  # STEP1
                LVX(28),  # STEP2
                LVX(32),  # STEP3
                LCX(1 if cur_mov['brake'] else 0),  # BRAKE

                opOutput_Start,  # b'\xA6'
                LCX(0),  # LAYER
                LCX(port_inner),  # NOS
            ))
            return unpack(
                '<3i2B',
                self.send_direct_cmd(
                    ops,
                    global_mem=14, local_mem=61
                )
            )

        if self._current_movement is None:
            # prevent needless data traffic
            return True
        if self._current_movement['op'] != 'Step_Speed':
            RuntimeError('unknown movement')

        cur_mov = self._current_movement
        all_left = (
            round(cur_mov['target_motor_pos'][0]) -
            cur_mov['start_motor_pos'][0]
        )
        all_right = (
            round(cur_mov['target_motor_pos'][1]) -
            cur_mov['start_motor_pos'][1]
        )
        if 'last_motor_pos' not in cur_mov:
            cur_mov['last_motor_pos'] = cur_mov['start_motor_pos']

        if abs(all_left) < abs(all_right):
            # regulate left motor
            port_inner = self._port_left
            port_outer = self._port_right
            speed = cur_mov['speed_left']
            step1 = cur_mov['step1_left']
            step2 = cur_mov['step2_left']
            step3 = cur_mov['step3_left']
            start_pos_inner = cur_mov['start_motor_pos'][0]
            start_pos_outer = cur_mov['start_motor_pos'][1]
            last_pos_inner = cur_mov['last_motor_pos'][0]
            last_pos_outer = cur_mov['last_motor_pos'][1]
            target_pos_inner = cur_mov['target_motor_pos'][0]
            target_pos_outer = cur_mov['target_motor_pos'][1]
        else:
            # regulate right motor
            port_inner = self._port_right
            port_outer = self._port_left
            speed = cur_mov['speed_right']
            step1 = cur_mov['step1_right']
            step2 = cur_mov['step2_right']
            step3 = cur_mov['step3_right']
            start_pos_inner = cur_mov['start_motor_pos'][1]
            start_pos_outer = cur_mov['start_motor_pos'][0]
            last_pos_inner = cur_mov['last_motor_pos'][1]
            last_pos_outer = cur_mov['last_motor_pos'][0]
            target_pos_inner = cur_mov['target_motor_pos'][1]
            target_pos_outer = cur_mov['target_motor_pos'][0]

        speed_orig = speed

        pos_inner, pos_outer, speed, busy_inner, busy_outer = direct_cmd()

        # update tracking
        if abs(all_left) < abs(all_right):
            # regulate left motor
            motor_pos = (pos_inner, pos_outer)
            cur_mov['speed_left'] = speed
        else:
            # regulate right motor
            motor_pos = (pos_outer, pos_inner)
            cur_mov['speed_right'] = speed

        self._tracking.update(motor_pos)

        if not busy_inner and not busy_outer:
            # all done
            self._current_movement = None
            return True

        if speed_orig != speed:
            cur_mov['last_motor_pos'] = motor_pos

        return self._delta_time


    def _start_move_by(
            self,
            diff_pos: Tuple[Decimal],
            *,
            speed: int,
            ramp_up: int,
            ramp_down: int,
            brake: bool,
            _control: bool = False
    ) -> None:
        '''
        starts moving the motors to given positions

        Mandatory positional arguments

          diff_positions
            difference in positions [degree] of left and right motor

        Mandatory keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        diff_left = round(diff_pos[0])
        diff_right = round(diff_pos[1])

        if abs(diff_left) >= abs(diff_right):
            # left is outer, right is inner
            factor = abs(diff_right) / abs(diff_left)
            speed_left = copysign(speed, diff_left)
            step2_left = abs(diff_left) - ramp_up - ramp_down
            if step2_left < 0:
                step1_left = round(abs(diff_left) * (
                    ramp_up / (ramp_up + ramp_down)
                ))
                step3_left = abs(diff_left) - step1_left
                step2_left = 0
                speed_left *= min(
                    sqrt(step1_left / ramp_up) if ramp_up > 0 else 1,
                    sqrt(step3_left / ramp_down) if ramp_down > 0 else 1
                )
                speed_left = round(speed_left)
            else:
                step1_left = ramp_up
                step3_left = ramp_down
                speed_left = round(speed_left)
            step1_right = int(factor**2 * step1_left)
            step3_right = int(factor**2 * step3_left)
            step2_right = abs(diff_right) - step1_right - step3_right
            speed_right = round(copysign(factor * abs(speed_left), diff_right))
        else:
            # right is outer, left is inner
            factor = abs(diff_left) / abs(diff_right)
            speed_right = copysign(speed, diff_right)
            step2_right = abs(diff_right) - ramp_up - ramp_down
            if step2_right < 0:
                step1_right = round(abs(diff_right) * (
                    ramp_up / (ramp_up + ramp_down)
                ))
                step2_right = 0
                step3_right = abs(diff_right) - step1_right
                speed_right *= min(
                    (step1_right / ramp_up)**2 if ramp_up > 0 else 1,
                    (step3_right / ramp_down)**2 if ramp_down > 0 else 1
                )
                speed_right = round(speed_right)
            else:
                step1_right = ramp_up
                step3_right = ramp_down
                speed_right = round(speed_right)
            step1_left = int(factor**2 * step1_right)
            step3_left = int(factor**2 * step3_right)
            step2_left = abs(diff_left) - step1_left - step3_left
            speed_left = round(copysign(factor * abs(speed_right), diff_left))

        ops_move = b''.join((
            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS

            opOutput_Step_Speed,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NOS
            LCX(speed_left),  # SPEED
            LCX(step1_left),  # STEP1
            LCX(step2_left),  # STEP2
            LCX(step3_left),  # STEP3
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Step_Speed,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NOS
            LCX(speed_right),  # SPEED
            LCX(step1_right),  # STEP1
            LCX(step2_right),  # STEP2
            LCX(step3_right),  # STEP3
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right)  # NOS
        ))
        data = unpack(
            '<2i',
            self.send_direct_cmd(
                self._ops_pos() + ops_move,
                global_mem=8
            )
        )
        self._tracking.update(data)

        if _control:
            if self._target_motor_pos is None:
                self._target_motor_pos = MotorPositions(
                    self._tracking._motor_pos[0] + diff_pos[0],
                    self._tracking._motor_pos[1] + diff_pos[1]
                )
            else:
                self._target_motor_pos = MotorPositions(
                    self._target_motor_pos.left + diff_pos[0],
                    self._target_motor_pos.right + diff_pos[1]
                )
            self._current_movement = {
                'op': 'Step_Speed',
                'start_motor_pos': data,
                'speed_left': speed_left,
                'step1_left': step1_left,
                'step2_left': step2_left,
                'step3_left': step3_left,
                'speed_right': speed_right,
                'step1_right': step1_right,
                'step2_right': step2_right,
                'step3_right': step3_right,
                'target_motor_pos': (
                    round(self._target_motor_pos.left),
                    round(self._target_motor_pos.right)
                ),
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake
            }
        else:
            self._target_motor_pos = None
            self._current_movement = None


    def _start_move_to(
            self,
            target_pos: Tuple[Decimal],
            *,
            speed: int,
            ramp_up: int,
            ramp_down: int,
            brake: bool,
            _control: bool = False
    ) -> None:
        '''
        starts moving the motors to given positions

        Mandatory positional arguments

          target_positions
            target positions [degree] of left and right motor

        Mandatory keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        if _control:
            self._target_motor_pos = MotorPositions(
                target_pos[0],
                target_pos[1]
            )
        else:
            self._target_motor_pos = None

        current_pos = self.motor_pos
        diff_left = round(target_pos[0] - current_pos.left)
        diff_right = round(target_pos[1] - current_pos.right)

        if abs(diff_left) >= abs(diff_right):
            # left is outer, right is inner
            factor = abs(diff_right) / abs(diff_left)
            speed_left = copysign(speed, diff_left)
            step2_left = abs(diff_left) - ramp_up - ramp_down
            if step2_left < 0:
                step1_left = round(abs(diff_left) * (
                    ramp_up / (ramp_up + ramp_down)
                ))
                step3_left = abs(diff_left) - step1_left
                step2_left = 0
                speed_left *= min(
                    sqrt(step1_left / ramp_up) if ramp_up > 0 else 1,
                    sqrt(step3_left / ramp_down) if ramp_down > 0 else 1
                )
                speed_left = round(speed_left)
            else:
                step1_left = ramp_up
                step3_left = ramp_down
                speed_left = round(speed_left)
            step1_right = int(factor**2 * step1_left)
            step3_right = int(factor**2 * step3_left)
            step2_right = abs(diff_right) - step1_right - step3_right
            speed_right = round(copysign(factor * abs(speed_left), diff_right))
        else:
            # right is outer, left is inner
            factor = abs(diff_left) / abs(diff_right)
            speed_right = copysign(speed, diff_right)
            step2_right = abs(diff_right) - ramp_up - ramp_down
            if step2_right < 0:
                step1_right = round(abs(diff_right) * (
                    ramp_up / (ramp_up + ramp_down)
                ))
                step2_right = 0
                step3_right = abs(diff_right) - step1_right
                speed_right *= min(
                    (step1_right / ramp_up)**2 if ramp_up > 0 else 1,
                    (step3_right / ramp_down)**2 if ramp_down > 0 else 1
                )
                speed_right = round(speed_right)
            else:
                step1_right = ramp_up
                step3_right = ramp_down
                speed_right = round(speed_right)
            step1_left = int(factor**2 * step1_right)
            step3_left = int(factor**2 * step3_right)
            step2_left = abs(diff_left) - step1_left - step3_left
            speed_left = round(copysign(factor * abs(speed_right), diff_left))

        ops_move = b''.join((
            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right),  # NOS

            opOutput_Step_Speed,
            LCX(0),  # LAYER
            LCX(self._port_left),  # NOS
            LCX(speed_left),  # SPEED
            LCX(step1_left),  # STEP1
            LCX(step2_left),  # STEP2
            LCX(step3_left),  # STEP3
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Step_Speed,
            LCX(0),  # LAYER
            LCX(self._port_right),  # NOS
            LCX(speed_right),  # SPEED
            LCX(step1_right),  # STEP1
            LCX(step2_right),  # STEP2
            LCX(step3_right),  # STEP3
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port_left + self._port_right)  # NOS
        ))
        data = unpack(
            '<2i',
            self.send_direct_cmd(
                self._ops_pos() + ops_move,
                global_mem=8
            )
        )
        self._tracking.update(data)

        if _control:
            self._current_movement = {
                'op': 'Step_Speed',
                'start_motor_pos': data,
                'speed_left': speed_left,
                'step1_left': step1_left,
                'step2_left': step2_left,
                'step3_left': step3_left,
                'speed_right': speed_right,
                'step1_right': step1_right,
                'step2_right': step2_right,
                'step3_right': step3_right,
                'target_motor_pos': (
                    round(self._target_motor_pos.left),
                    round(self._target_motor_pos.right)
                ),
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake
            }
        else:
            self._current_movement = None


    def _start_drive_straight(
            self,
            distance: Number,
            *,
            speed: int = None,
            ramp_up: int = None,
            ramp_down: int = None,
            brake: bool = False,
            _control: bool = False
    ) -> None:
        '''
        starts driving the vehicle straight by a given distance

        Mandatory positional arguments

          distance
            direction (sign) and distance (meters) of straight movement

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        assert isinstance(distance, Number), \
            'distance needs to be a number'

        assert speed is None or isinstance(speed, int), \
            'speed needs to be an integer'
        assert speed is None or 0 < speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

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
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        step = distance * 360 / (2 * pi * self._radius_wheel)
        step_left = Decimal(
            self._polarity_left * step
        ).quantize(Decimal('1.0000'))
        step_right = Decimal(
            self._polarity_right * step
        ).quantize(Decimal('1.0000'))

        if self._target_motor_pos is None:
            self._start_move_by(
                (step_left, step_right),
                speed=speed,
                ramp_up=ramp_up,
                ramp_down=ramp_down,
                brake=brake,
                _control=_control
            )
        else:
            self._start_move_to(
                (
                    self._target_motor_pos.left + step_left,
                    self._target_motor_pos.right + step_right
                ),
                speed=speed,
                ramp_up=ramp_up,
                ramp_down=ramp_down,
                brake=brake,
                _control=_control
            )


    def drive_straight(
            self,
            distance: Number,
            *,
            speed: int = None,
            ramp_up: int = None,
            ramp_down: int = None,
            brake: bool = False
    ) -> Task:
        '''
        drives the vehicle straight by a given distance

        Mandatory positional arguments

          distance
            direction (sign) and distance (meters) of straight movement

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).

        Returns

          Task object, which can be started, stopped and continued.
        '''
        assert isinstance(distance, Number), \
            'distance needs to be a number'

        assert speed is None or isinstance(speed, int), \
            'speed needs to be an integer'
        assert speed is None or 0 < speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

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
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        return Task(
            self._start_drive_straight,
            args=(distance,),
            kwargs={
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake,
                '_control': True
            },
            duration=self._delta_time,
            action_stop=self.stop,
            action_cont=self.cont
        ) + Repeated(
            self._control,
            action_stop=self.stop,
            action_cont=self.cont
        )


    def _start_drive_turn(
            self,
            angle: Number,
            radius: Number,
            *,
            speed: int = None,
            back: bool = False,
            ramp_up: int = None,
            ramp_down: int = None,
            brake: bool = False,
            _control: bool = False
    ) -> None:
        '''
        starts driving the vehicle a turn by given angle and radius

        Mandatory positional arguments

          angle
            angle of turn (degrees),
            positive sign: to the left,
            negative sign: to the right
          radius
            radius of turn (meters)

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          back
            flag if backwards
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).
        '''
        assert isinstance(angle, Number), \
            'angle needs to be a number'

        assert isinstance(radius, Number) and radius >= 0, \
            'radius needs to be a positive number'

        assert speed is None or isinstance(speed, int), \
            'speed needs to be an integer'
        assert speed is None or 0 < speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(back, bool), \
            'back must be a bool'

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

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
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        radius_outer = radius + 0.5 * self._tread
        radius_inner = radius - 0.5 * self._tread

        ratio = radius_inner / radius_outer

        step_outer = (
            (-1 if back else 1) *
            abs(angle) *
            radius_outer /
            self._radius_wheel
        )
        step_inner = ratio * step_outer
        if any((
                angle > 0 and not back,
                angle < 0 and back
        )):
            step_left = Decimal(
                self._polarity_left * step_inner
            ).quantize(Decimal('1.0000'))
            step_right = Decimal(
                self._polarity_right * step_outer
            ).quantize(Decimal('1.0000'))
        else:
            step_left = Decimal(
                self._polarity_left * step_outer,
            ).quantize(Decimal('1.0000'))
            step_right = Decimal(
                self._polarity_right * step_inner
            ).quantize(Decimal('1.0000'))

        if self._target_motor_pos is None:
            self._start_move_by(
                (step_left, step_right),
                speed=speed,
                ramp_up=ramp_up,
                ramp_down=ramp_down,
                brake=brake,
                _control=_control
            )
        else:
            self._start_move_to(
                (
                    self._target_motor_pos.left + step_left,
                    self._target_motor_pos.right + step_right
                ),
                speed=speed,
                ramp_up=ramp_up,
                ramp_down=ramp_down,
                brake=brake,
                _control=_control
            )


    def drive_turn(
            self,
            angle: Number,
            radius: Number,
            *,
            speed: int = None,
            back: bool = False,
            ramp_up: int = None,
            ramp_down: int = None,
            brake: bool = False
    ) -> Task:
        '''
        starts driving the vehicle a turn by given angle and radius

        Mandatory positional arguments

          angle
            angle of turn (degrees),
            positive sign: to the left,
            negative sign: to the right
          radius
            radius of turn (meters)

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          back
            flag if backwards
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            Flag if ending with floating motors (False) or active brake (True).

        Returns

          Task object, which can be started, stopped and continued.
        '''
        assert isinstance(radius, Number) and radius >= 0, \
            'radius needs to be a positive number'

        assert isinstance(angle, Number), \
            'angle needs to be a number'

        assert speed is None or isinstance(speed, int), \
            'speed needs to be an integer'
        assert speed is None or 0 < speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(back, bool), \
            'back must be a bool'

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

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
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        return Task(
            self._start_drive_turn,
            args=(angle, radius),
            kwargs={
                'speed': speed,
                'back': back,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake,
                '_control': True
            },
            duration=self._delta_time,
            action_stop=self.stop,
            action_cont=self.cont
        ) + Repeated(
            self._control,
            action_stop=self.stop,
            action_cont=self.cont
        )
