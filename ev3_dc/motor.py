#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - motor
"""

from math import copysign
from numbers import Integral, Number
from thread_task import Task, Periodic, Repeated
import struct
from time import time
from .ev3 import EV3
from .constants import (
    BLUETOOTH,
    WIFI,
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
    opOutput_Reset,
    opOutput_Step_Speed,
    opOutput_Start,
    opOutput_Test,
    opOutput_Stop,
    opOutput_Clr_Count,
    opOutput_Speed,
    opInput_Device,
    opMove32_F,
    opMove32_32,
    opMoveF_8,
    opMoveF_32,
    opAdd32,
    opSub32,
    opMul32,
    opDiv32,
    opSubF,
    opDivF,
    opMulF,
    opMath,
    opJr_Gteq32,
    READY_SI,
    GET_TYPEMODE,
    ABS
)
from .functions import (
    LCX,
    LVX,
    GVX,
    port_motor_input
)


class Motor(EV3):
    """
    EV3 motor, moves a single motor
    """

    def __init__(
            self,
            port: Integral,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            speed: Integral = 10,
            ramp_up: Integral = 15,
            ramp_down: Integral = 15,
            delta_time: Number = None
    ):
        """
        Positional Arguments

          port
            port of motor (PORT_A, PORT_B, PORT_C or PORT_D)

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
          ramp_up
            degrees for ramp-up (default is 15)
          ramp_down
            degrees for ramp-down (default is 15)
          delta_time
            timespan between  introspections [s]
            (default depends on protocol,
            USB: 0.2 sec., WIFI: 0.1 sec., USB: 0.05 sec.)
        """
        assert port in (PORT_A, PORT_B, PORT_C, PORT_D), "incorrect port"

        assert isinstance(speed, Integral), \
            "speed needs to be an integer"
        assert speed > 0, \
            "speed needs to be positive"
        assert speed <= 100, \
            "speed needs to be lower or equal 100"

        assert isinstance(ramp_up, Integral), \
            "ramp_up needs to be an integer"
        assert ramp_up >= 0, \
            "ramp_up needs to be positive"

        assert isinstance(ramp_down, Integral), \
            "ramp_down needs to be an integer"
        assert ramp_down >= 0, \
            "ramp_down needs to be positive"

        assert delta_time is None or isinstance(delta_time, Number), \
            "delta_time needs to be a number"
        assert delta_time is None or delta_time > 0, \
            "delta_time needs to be positive"

        self._port = port
        self._speed = speed
        self._ramp_up = ramp_up
        self._ramp_down = ramp_down

        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)
        self._type = None
        self._target_position = None
        self._current_movement = None
        if delta_time is not None:
            self._delta_time = delta_time
        elif self._physical_ev3._protocol == BLUETOOTH:
            self._delta_time = .2
        elif self._physical_ev3._protocol == WIFI:
            self._delta_time = .1
        else:
            self._delta_time = .05

    @property
    def port(self):
        """
        port of motor (default: PORT_A)
        """
        return self._port

    @property
    def speed(self):
        """
        speed of movements in percentage of maximum speed [1 - 100]
        (default is 10)
        """
        return self._speed

    @speed.setter
    def speed(self, value: Integral):
        assert isinstance(value, Integral), "speed needs to be an integer"
        assert value > 0, \
            "speed needs to be positive"
        assert value <= 100, \
            "speed needs to be lower or equal 100"
        self._speed = value

    @property
    def ramp_up(self):
        """
        degrees for ramp-up (default is 15)
        """
        return self._ramp_up

    @ramp_up.setter
    def ramp_up(self, value: Integral):
        assert isinstance(value, Integral), \
            "ramp_up needs to be an integer"
        assert value >= 0, \
            "ramp_up needs to be positive"
        self._ramp_up = value

    @property
    def ramp_down(self):
        """
        degrees for ramp-down (default is 15)
        """
        return self._ramp_down

    @ramp_down.setter
    def ramp_down(self, value: Integral):
        assert isinstance(value, Integral), \
            "ramp_down needs to be an integer"
        assert value >= 0, \
            "ramp_down needs to be positive"
        self._ramp_down = value

    @property
    def delta_time(self):
        """
        timespan between introspections [s]
        """
        return self._delta_time

    @delta_time.setter
    def delta_time(self, value: Number):
        assert isinstance(value, Number), "delta_time needs to be a number"
        assert value > 0, \
            "delta_time needs to be positive"
        self._delta_time = value

    @property
    def type(self):
        """
        type of motor (7: EV3-Large, 8: EV3-Medium, )
        """
        if self._type is not None:
            return self._type
        else:
            ops = b''.join((
                opInput_Device,
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                GVX(0),  # TYPE (output)
                LVX(0),  # MODE (output)

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO
            ))
            reply = self.send_direct_cmd(ops, local_mem=1, global_mem=1)
            self._type = struct.unpack('<b', reply)[0]
            return self._type

    @property
    def position(self) -> Number:
        """
        current position of motor
        """
        ops = b''.join((
            opInput_Device,
            READY_SI,  # CMD
            LCX(0),  # LAYER
            port_motor_input(self._port),  # NO
            LCX(self.type),  # TYPE
            LCX(0),  # MODE (Degree)
            LCX(1),  # VALUES
            GVX(0)  # VALUE1 (output)
        ))
        return round(
            struct.unpack(
                '<f',
                self.send_direct_cmd(ops, global_mem=4)
            )[0]
        )

    @property
    def busy(self) -> bool:
        """
        Flag if motor is currently busy
        """
        reply = self.send_direct_cmd(
            b''.join((
                opOutput_Test,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                GVX(0)  # BUSY
            )),
            global_mem=1
        )
        busy = struct.unpack('<B', reply)[0]
        return True if busy else False

    def reset_position(self) -> None:
        """makes the motor's current position the new zero position"""
        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), 'current movement in progress'

        self._target_position = None
        self._current_movement = None
        self.send_direct_cmd(
            b''.join((
                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO
            ))
        )

    def start(
        self,
        speed: Integral = None,
        direction: Integral = 1
    ) -> None:
        '''starts unlimited movement with constant speed

        Keyword Arguments

          speed
            speed of movement
          direction
            direction of movement (-1 or 1)
        '''
        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert direction is None or isinstance(direction, Integral), \
            'direction needs to be an integer value'
        assert direction in (-1, 1), \
            'direction needs to be 1 (forwards) or -1 (backwards)'

        if speed is None:
            speed = self._speed

        speed *= direction

        if self._type is None:
            ops = b''.join((
                opInput_Device,
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                GVX(0),  # TYPE (output)
                LVX(0),  # MODE (output)

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO

                opOutput_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            reply = self.send_direct_cmd(ops, local_mem=1, global_mem=1)
            self._type = struct.unpack('<b', reply)[0]
        else:
            ops = b''.join((
                opOutput_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            self.send_direct_cmd(ops)

        self._target_position = None
        self._current_movement = {
            'op': 'Speed',
            'speed': speed,
            'unlimited': True
        }

    def stop(self, brake: bool = False) -> None:
        '''stops the current motor movement, sets or releases brake

        Keyword Arguments

          brake
            flag if stopping with active brake
        '''
        assert isinstance(brake, bool), \
            'brake must be a boolean'

        self.send_direct_cmd(
            b''.join((
                opOutput_Stop,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(1 if brake else 0),  # BRAKE - 0 (no), 1 (yes)
            ))
        )

        if self._current_movement is None:
            pass
        else:
            self._current_movement['stopped'] = True

    def cont(self):
        if self._current_movement is None:
            # movement was already finished
            return

        assert 'stopped' in self._current_movement, \
            "can't continue unstopped movement"

        if self._current_movement['op'] == 'Step_Speed':
            return self.start_move_to(
                self._current_movement['target_position'],
                speed=self._current_movement['speed'],
                ramp_up=self._current_movement['ramp_up'],
                ramp_down=self._current_movement['ramp_down'],
                brake=self._current_movement['brake'],
                _controlled=True
            )

        if (
            self._current_movement['op'] == 'Speed' and
            'unlimited' in self._current_movement
        ):
            return self.start(
                speed=abs(self._current_movement['speed']),
                direction=int(copysign(1, self._current_movement['speed']))
            )

        current_position = self.position

        # calculate rest and test if overshooted
        speed = self._current_movement['speed']
        rest = self._current_movement['target_position'] - current_position

        if rest == 0:
            # exact in target position
            self._current_movement = None
            return

        if speed * rest < 0:
            # overshooted
            speed *= -1
        ops = b''.join((
            opOutput_Speed,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS
            LCX(speed),  # SPEED

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port)  # NOS
        ))
        self.send_direct_cmd(ops)

        self._current_movement['last_position'] = current_position
        self._current_movement['last_time'] = time()
        del self._current_movement['stopped']

    def _start_move_steady(
        self,
        degrees: Integral,
        speed: Integral = None,
        _controlled: bool = False
    ):
        '''start movement with constant speed
        '''
        assert isinstance(degrees, Integral), \
            'degrees needs to be an integer value'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed

        speed *= round(copysign(1, degrees))

        if self._type is None:
            ops = b''.join((
                opInput_Device,
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                GVX(0),  # TYPE (output)
                LVX(0),  # MODE (output)

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO

                opOutput_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            reply = self.send_direct_cmd(ops, local_mem=1, global_mem=1)
            self._type = struct.unpack('<b', reply)[0]
            self._target_position = 0
            position = 0
        else:
            ops = b''.join((
                opInput_Device,
                READY_SI,
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                LCX(self._type),  # TYPE
                LCX(0),  # MODE (Degree)
                LCX(1),  # VALUES
                GVX(0),  # VALUE1 (output)

                opOutput_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            reply = self.send_direct_cmd(ops, global_mem=4)
            position = round(struct.unpack('<f', reply)[0])

        if self._target_position is None:
            target_position = position + degrees
        else:
            target_position = (
                self._target_position + degrees
            )
            self._target_position = None

        if _controlled:
            self._current_movement = {
                'op': 'Speed',
                'speed': speed,
                'target_position': target_position,
                'last_position': position,
                'last_time': time()
            }
        else:
            self._current_movement = None

    def _control_repeated(self):
        '''returns timespan to next call [s]'''
        if self._current_movement is None:
            # prevent needless data traffic
            return -1
        if self._current_movement['op'] != 'Speed':
            RuntimeError('concurrent movements')
        print('0.0 inside _control_repeated', self._current_movement)
        # last one
        if 'last' in self._current_movement:
            self._target_position = (
                self._current_movement['target_position']
            )
            self._current_movement = None
            return -1

        position = self.position
        now = time()

        speed = self._current_movement['speed']
        target_position = self._current_movement['target_position']

        # already overshooted?
        if (speed > 0 and position >= target_position):
            self._target_position = (
                self._current_movement['target_position']
            )
            self._current_movement = None
            return -1

        if (speed < 0 and position <= target_position):
            self._target_position = (
                self._current_movement['target_position']
            )
            self._current_movement = None
            return -1

        delta_t = now - self._current_movement['last_time']
        delta_pos = position - self._current_movement['last_position']

        if delta_pos == 0 or copysign(1, speed) * delta_pos < 0:
            return 2*delta_t

        rest_pos = target_position - position
        rest_t = delta_t / delta_pos * rest_pos

        if rest_t < self._delta_time or abs(rest_pos) < 10:
            wait = rest_t
            self._current_movement['last'] = True
        else:
            wait = min(2*delta_t, 0.5*rest_t, 2)

        self._current_movement['last_position'] = position
        self._current_movement['last_time'] = now

        return wait

    def task_move_steady(
        self,
        degrees: Integral,
        speed: Integral = None
    ) -> Task:
        '''steady movement of the motor by a given angle.
        Does not stop, but the Task ends, just when the movement is done.

        Positional Arguments

          degrees
            angle of constant speed movement in degrees.

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]

        Returns

          Task object, that can be started, stopped and continued.
        '''
        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert isinstance(degrees, Integral), \
            'degrees needs to be an integer value'

        t_start = Task(
            self._start_move_steady,
            args=(degrees,),
            kwargs={
                'speed': speed,
                '_controlled': True
            },
            duration=self._delta_time,
            action_stop=self.stop,
            args_stop=(False,),
            action_cont=self.cont
        )

        return Task(
            t_start + Repeated(self._control_repeated)
        )

    def start_move(
        self,
        degrees: Integral,
        speed: Integral = None,
        ramp_up: Integral = None,
        ramp_down: Integral = None,
        brake: bool = True,
        _controlled: bool = False
    ):
        '''start moving the motor by a given angle (without time control).

        Positional Arguments

          degrees
            direction (sign) and angle (degrees) of movement

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]

          ramp_up
            degrees for ramp-up

          ramp_down
            degrees for ramp-down

          brake
            Flag if ending with floating motor (False) or active brake (True).
        '''
        assert isinstance(degrees, Integral), \
            'degrees needs to be an integer value'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, Integral), \
            "ramp_up needs to be an integer"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up needs to be positive"

        assert ramp_down is None or isinstance(ramp_down, Integral), \
            "ramp_down needs to be an integer"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down needs to be positive"

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if self._target_position is not None:
            return self.start_move_to(
                round(self._target_position + degrees),
                speed=speed,
                ramp_up=ramp_up,
                ramp_down=ramp_down,
                brake=brake,
                _controlled=_controlled
            )

        if speed is None:
            speed = self._speed
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        step1 = ramp_up
        step2 = abs(degrees) - ramp_up - ramp_down
        step3 = ramp_down

        if step2 < 0:
            step1 = round(abs(degrees) * ramp_up / (ramp_up + ramp_down))
            step2 = 0
            step3 = round(abs(degrees) - step1)

        speed *= round(copysign(1, degrees))

        if self._type is None:
            self._initialized = True
            ops = b''.join((
                opInput_Device,
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                GVX(0),  # TYPE (output)
                LVX(0),  # MODE (output)

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO

                opOutput_Step_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED
                LCX(step1),  # STEP1
                LCX(step2),  # STEP2
                LCX(step3),  # STEP3
                LCX(brake),  # BRAKE - 1 (yes) or 0 (no)

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            reply = self.send_direct_cmd(ops, local_mem=1, global_mem=1)
            self._type = struct.unpack('<b', reply)[0]
            position = 0
        else:
            ops = b''.join((
                opInput_Device,
                READY_SI,
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                LCX(self._type),  # TYPE
                LCX(0),  # MODE (Degree)
                LCX(1),  # VALUES
                GVX(0),  # VALUE1 (output)

                opOutput_Step_Speed,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS
                LCX(speed),  # SPEED
                LCX(step1),  # STEP1
                LCX(step2),  # STEP2
                LCX(step3),  # STEP3
                LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

                opOutput_Start,
                LCX(0),  # LAYER
                LCX(self._port)  # NOS
            ))
            reply = self.send_direct_cmd(ops, global_mem=4)
            position = round(struct.unpack('<f', reply)[0])

        if _controlled:
            self._current_movement = {
                'op': 'Step_Speed',
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake,
                'target_position': position + degrees
            }
        else:
            self._target_position = None
            self._current_movement = None

    def _control_periodic(self):
        '''Periodic needs inverse flag of property busy'''
        if self._current_movement is None:
            # prevent needless data traffic
            return True
        if self._current_movement['op'] != 'Step_Speed':
            RuntimeError('concurrent movements')

        if self.busy:
            return False
        else:
            self._target_position = self._current_movement['target_position']
            self._current_movement = None
            return True

    def task_move(
        self,
        degrees: Integral,
        speed: Integral = None,
        ramp_up: Integral = None,
        ramp_down: Integral = None,
        brake: bool = True,
        duration: Number = None
    ) -> Task:
        '''exact and smooth movement of the motor by a given angle.

        Positional Arguments

          degrees
            direction (sign) and angle (degrees) of movement

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]

          ramp_up
            degrees for ramp-up

          ramp_down
            degrees for ramp-down

          brake
            Flag if ending with floating motor (False) or active brake (True).

          duration
            duration of Task execution [s] (waits if movement lasts shorter)

        Returns

          Task object, that can be started, stopped and continued.
        '''
        assert isinstance(degrees, Integral), \
            'degrees needs to be an integer value'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, Integral), \
            "ramp_up needs to be an integer"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up needs to be positive"

        assert ramp_down is None or isinstance(ramp_down, Integral), \
            "ramp_down needs to be an integer"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down needs to be positive"

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert duration is None or isinstance(duration, Number), \
            'duration needs to be a number'
        assert duration is None or duration > 0, \
            'duration needs to be positive'

        t_start = Task(
            self.start_move,
            args=(degrees,),
            kwargs={
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
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

    def start_move_to(
        self,
        position: Integral,
        speed: Integral = None,
        ramp_up: Integral = None,
        ramp_down: Integral = None,
        brake: bool = True,
        _controlled: bool = False
    ):
        '''start moving the motor to a given position (without time control).

        Positional Arguments

          position
            target position (degrees)

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            flag if ending with floating motor (False) or active brake (True).
        '''
        assert isinstance(position, Integral), \
            'position needs to be an integer value'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, Integral), \
            "ramp_up needs to be an integer"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up needs to be positive"

        assert ramp_down is None or isinstance(ramp_down, Integral), \
            "ramp_down needs to be an integer"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down needs to be positive"

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
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        step1 = ramp_up
        step3 = ramp_down

        if self._type is None:
            ops = b''.join((
                opInput_Device,
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                GVX(0),  # TYPE (output)
                LVX(0),  # MODE (output)

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                opOutput_Clr_Count,
                LCX(0),  # LAYER
                LCX(self._port),  # NO

                # current position

                opMove32_F,
                LCX(0),  # SOURCE
                LVX(0),  # DESTINATION - from_position (DATAF)
            ))
        else:
            ops = b''.join((

                opOutput_Reset,
                LCX(0),  # LAYER
                LCX(self._port),  # NOS

                # current position

                opInput_Device,
                READY_SI,
                LCX(0),  # LAYER
                port_motor_input(self._port),  # NO
                LCX(self._type),  # TYPE (EV3-Medium-Motor)
                LCX(0),  # MODE (Degree)
                LCX(1),  # VALUES
                LVX(0),  # VALUE1 - from_position (DATAF)
            ))

        ops += b''.join((

            # speed and step2

            opMove32_F,
            LCX(position),  # SOURCE
            LVX(4),  # DESTINATION - to_position (DATAF)

            opSubF,
            LVX(4),  # SOURCE1 - to_position (DATAF)
            LVX(0),  # SOURCE2 - from_position (DATAF)
            LVX(0),  # DESTINATION - diff (DATAF)

            opMath,
            ABS,  # CMD
            LVX(0),  # DATA X - diff (DATAF)
            LVX(4),  # RESULT - abs(diff) (DATAF)

            opDivF,
            LVX(0),  # SOURCE1 - diff (DATAF)
            LVX(4),  # SOURCE2 - abs(diff) (DATAF)
            LVX(0),  # DESTINATION - sign of diff (DATAF)

            opMove32_F,
            LCX(speed),  # SOURCE
            LVX(8),  # DESTINATION - speed (DATAF)

            opMulF,
            LVX(0),  # SOURCE1 - sign of diff (DATAF)
            LVX(8),  # SOURCE2 - speed (DATAF)
            LVX(0),  # DESTINATION - signed_speed (DATAF)

            opMoveF_8,
            LVX(0),  # SOURCE - signed_speed (DATAF)
            LVX(0),  # DESTINATION - signed_speed (DATA8)

            opMoveF_32,
            LVX(4),  # SOURCE - abs(diff) (DATAF)
            LVX(8),  # DESTINATION - step2 (DATA32)

            # step1 and step2, subtraction from step2

            opMove32_32,
            LCX(step1),  # SOURCE
            LVX(4),  # DESTINATION - step1 (DATA32)

            opMove32_32,
            LCX(step3),  # SOURCE
            LVX(12),  # DESTINATION - step3 (DATA32)

            opAdd32,
            LVX(4),  # SOURCE1 - step1 (DATA32)
            LVX(12),  # SOURCE1 - step3 (DATA32)
            LVX(16),  # DESTINATION - step1 + step3 (DATA32)

            opMove32_32,
            LVX(8),  # SOURCE - step2 (DATA32)
            LVX(20),  # DESTINATION - step2_orig (DATA32)

            opSub32,
            LVX(8),  # SOURCE1 - step2 (DATA32)
            LVX(16),  # SOURCE2 - step1 + step3 (DATA32)
            LVX(8),  # DESTINATION - step2 (DATA32)

            # if step2 is not positive

            opJr_Gteq32,
            LVX(8),  # LEFT - step2 (DATA32)
            LCX(0),  # RIGHT
            LCX(15),  # OFFSET

            opMul32,
            LVX(20),  # SOURCE1 - step2_orig (DATA32)
            LVX(4),  # SOURCE2 - step1 (DATA32)
            LVX(4),  # DESTINATION - step1 (DATA32)

            opDiv32,
            LVX(4),  # SOURCE1 - step1 (DATA32)
            LVX(16),  # SOURCE2 - step1 + step3 (DATA32)
            LVX(4),  # DESTINATION - step1 (DATA32)

            opSub32,
            LVX(20),  # SOURCE1 - step2_orig (DATA32)
            LVX(4),  # SOURCE2 - step1 (DATA32)
            LVX(12),  # DESTINATION - step3 (DATA32)

            opMove32_32,
            LCX(0),  # SOURCE
            LVX(8),  # DESTINATION - step2 (DATA32)

            # do the movement

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS

            opOutput_Step_Speed,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS
            LVX(0),  # SPEED - signed_speed (DATA8)
            LVX(4),  # STEP1 (DATA32)
            LVX(8),  # STEP2 (DATA32)
            LVX(12),  # STEP3 (DATA32)
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port)  # NOS
        ))

        if self._type is None:
            reply = self.send_direct_cmd(ops, local_mem=24, global_mem=1)
            self._type = struct.unpack('<b', reply)[0]
        else:
            self.send_direct_cmd(ops, local_mem=24)

        if _controlled:
            self._current_movement = {
                'op': 'Step_Speed',
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
                'brake': brake,
                'target_position': position
            }
        else:
            self._target_position = None
            self._current_movement = None

    def task_move_to(
        self,
        position: Integral,
        speed: Integral = None,
        ramp_up: Integral = None,
        ramp_down: Integral = None,
        brake: bool = True,
        duration: Number = None
    ) -> Task:
        '''move the motor to a given position.

        Positional Arguments

          position
            target position (degrees)

        Keyword Arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            flag if ending with floating motor (False) or active brake (True).
          duration
            duration of Task execution [s] (waits if movement lasts shorter)

        Returns

          Task object, that can be started, stopped and continued.
        '''
        assert isinstance(position, Integral), \
            'position needs to be an integer value'

        assert speed is None or isinstance(speed, Integral), \
            'speed needs to be an integer value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  needs to be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, Integral), \
            "ramp_up needs to be an integer"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up needs to be positive"

        assert ramp_down is None or isinstance(ramp_down, Integral), \
            "ramp_down needs to be an integer"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down needs to be positive"

        assert isinstance(brake, bool), \
            'brake needs to be a boolean'

        assert duration is None or isinstance(duration, Number), \
            'duration needs to be a number'
        assert duration is None or duration > 0, \
            'duration needs to be positive'

        t_start = Task(
            self.start_move_to,
            args=(position,),
            kwargs={
                'speed': speed,
                'ramp_up': ramp_up,
                'ramp_down': ramp_down,
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
