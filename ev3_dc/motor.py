#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - motor
"""

import math
from numbers import Number
from thread_task import Task, Periodic
import struct
import time
from datetime import datetime
from .ev3 import EV3
from .constants import (
    BLUETOOTH,
    WIFI,
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
    EV3_LARGE_MOTOR,
    EV3_MEDIUM_MOTOR,
    opOutput_Reset,
    opOutput_Step_Speed,
    opOutput_Time_Speed,
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
    ABS
)
from .functions import LCX, LVX, GVX, port_motor_input
from .exceptions import MotorError


class Motor(EV3):
    """
    EV3 motor, moves a single motor
    """

    def __init__(
            self,
            port: int,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            speed: int = 10,
            ramp_up: int = 15,
            ramp_up_time: float = 0.15,
            ramp_down: int = 15,
            ramp_down_time: float = 0.15,
            delta_time: Number = None,
            verbosity: int = 0
    ):
        """
        Mandatory positional arguments

          port
            port of motor (PORT_A, PORT_B, PORT_C or PORT_D)

        Keyword only arguments (either protocol and host or ev3_obj)

          protocol
            BLUETOOTH == 'Bluetooth'
            USB == 'Usb'
            WIFI == 'WiFi'
          host
            mac-address of the LEGO EV3 (f.i. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object (its connections will be used)
          speed
            percentage of maximum speed [1 - 100] (default is 10)
          ramp_up
            degrees for ramp-up (default is 15)
          ramp_up_time
            duration of ramp-up (used by move_for, default is 0.1 sec.)
          ramp_down
            degrees for ramp-down (default is 15)
          ramp_down_time
            duration of ramp-down (used by move_for, default is 0.1 sec.)
          delta_time
            timespan between  introspections [s]
            (default depends on protocol,
            USB: 0.2 sec., WIFI: 0.1 sec., USB: 0.05 sec.)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert port in (PORT_A, PORT_B, PORT_C, PORT_D), "incorrect port"

        assert isinstance(speed, int), \
            "speed must be an int"
        assert speed > 0, \
            "speed must be positive"
        assert speed <= 100, \
            "speed must be lower or equal 100"

        assert isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up >= 0, \
            "ramp_up must be positive"

        assert isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down >= 0, \
            "ramp_down must be positive"

        assert ramp_up_time is None or isinstance(ramp_up_time, Number), \
            "ramp_up_time must be a number"
        assert ramp_up_time is None or ramp_up_time >= 0, \
            "ramp_up_time must be positive"

        assert ramp_down_time is None or isinstance(ramp_down_time, Number), \
            "ramp_down_time must be a number"
        assert ramp_down_time is None or ramp_down_time >= 0, \
            "ramp_down_time must be positive"

        assert delta_time is None or isinstance(delta_time, Number), \
            "delta_time must be a number"
        assert delta_time is None or delta_time > 0, \
            "delta_time must be positive"

        self._port = port
        self._speed = speed
        self._ramp_up = ramp_up
        self._ramp_down = ramp_down
        self._ramp_up_time = ramp_up_time
        self._ramp_down_time = ramp_down_time

        super().__init__(protocol=protocol, host=host, ev3_obj=ev3_obj)

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)
        
        if self.sensors_as_dict[port_motor_input(self._port)] not in (
                    EV3_LARGE_MOTOR,
                    EV3_MEDIUM_MOTOR
        ):
            if self._port == PORT_A:
                port_str = 'PORT_A'
            elif self._port == PORT_B:
                port_str = 'PORT_B'
            elif self._port == PORT_C:
                port_str = 'PORT_C'
            else:
                port_str = 'PORT_D'
            raise MotorError('no motor connected at ' + port_str)
            
        # reset counter
        self.send_direct_cmd(
                b''.join((
                    opOutput_Reset,
                    LCX(0),  # LAYER
                    LCX(self._port),  # NOS
        
                    opOutput_Clr_Count,
                    LCX(0),  # LAYER
                    LCX(self._port),  # NO
                ))
        )

        self._target_position = 0
        self._current_movement = None
        if delta_time is not None:
            self._delta_time = delta_time
        elif self._physical_ev3._protocol == BLUETOOTH:
            self._delta_time = .2
        elif self._physical_ev3._protocol == WIFI:
            self._delta_time = .1
        else:
            self._delta_time = .05

    def __str__(self):
        '''
        description of the object in a str context
        '''
        if self.sensors_as_dict[port_motor_input(self._port)] == EV3_LARGE_MOTOR:
            type_str = 'EV3_LARGE_MOTOR'
        else:
            type_str = 'EV3_MEDIUM_MOTOR'

        if self._port == PORT_A:
            port_str = 'PORT_A'
        elif self._port == PORT_B:
            port_str = 'PORT_B'
        elif self._port == PORT_C:
            port_str = 'PORT_C'
        else:
            port_str = 'PORT_D'

        return ' '.join((
                type_str,
                f'at {port_str}',
                f'of {super().__str__()}'
        ))

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
    def speed(self, value: int):
        assert isinstance(value, int), "speed must to be an int"
        assert value > 0, \
            "speed must be positive"
        assert value <= 100, \
            "speed must be lower or equal 100"
        self._speed = value

    @property
    def ramp_up(self):
        """
        degrees for ramp-up (default is 15)
        """
        return self._ramp_up

    @ramp_up.setter
    def ramp_up(self, value: int):
        assert isinstance(value, int), \
            "ramp_up must be an int"
        assert value >= 0, \
            "ramp_up must be positive"
        self._ramp_up = value

    @property
    def ramp_down(self):
        """
        degrees for ramp-down (default is 15)
        """
        return self._ramp_down

    @ramp_down.setter
    def ramp_down(self, value: int):
        assert isinstance(value, int), \
            "ramp_down must be an int"
        assert value >= 0, \
            "ramp_down must be positive"
        self._ramp_down = value

    @property
    def ramp_up_time(self):
        """
        seconds for ramp-up of timed movements (default is 0.1)
        """
        return self._ramp_up_time

    @ramp_up_time.setter
    def ramp_up_time(self, value: Number):
        assert isinstance(value, Number), \
            "ramp_up_time must be an number"
        assert value >= 0, \
            "ramp_up_time must be positive"
        self._ramp_up_time = value

    @property
    def ramp_down_time(self):
        """
        seconds for ramp-down of timed movements (default is 0.1)
        """
        return self._ramp_up_time

    @ramp_down_time.setter
    def ramp_down_time(self, value: Number):
        assert isinstance(value, Number), \
            "ramp_down_time must be an number"
        assert value >= 0, \
            "ramp_down_time must be positive"
        self._ramp_down_time = value

    @property
    def delta_time(self):
        """
        timespan between introspections [s]
        """
        return self._delta_time

    @delta_time.setter
    def delta_time(self, value: Number):
        assert isinstance(value, Number), "delta_time must be a number"
        assert value > 0, \
            "delta_time must be positive"
        self._delta_time = value

    @property
    def motor_type(self):
        """
        type of motor (7: EV3-Large, 8: EV3-Medium, )
        """
        return self.sensors_as_dict[port_motor_input(self._port)]

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
        busy = struct.unpack('B', reply)[0]
        return True if busy else False

    @property
    def position(self) -> Number:
        """
        current position of motor [degree]
        """
        ops = b''.join((
            opInput_Device,
            READY_SI,  # CMD
            LCX(0),  # LAYER
            port_motor_input(self._port),  # NO
            LCX(self.motor_type),  # TYPE
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
            
    @position.setter
    def position(self, value: int) -> None:
        '''
        makes current position the new zero position
        '''
        assert isinstance(value, int), 'value must be an integer'
        assert value == 0, 'position can be set to zero only' 
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


    def stop(self, *, brake: bool = False) -> None:
        '''
        stops the current motor movement, sets or releases brake

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
            if self._current_movement['op'] == 'Time_Speed':
                self._current_movement['duration_rest'] = (
                        self._current_movement['duration'] - (
                                datetime.now() -
                                self._current_movement['started_at']
                        ).total_seconds()
                )
                if self._current_movement['duration_rest'] < 0.001:
                    self._current_movement = None

    def stop_as_task(self, *, brake: bool = False) -> Task:
        '''
        stops the current motor movement, with or without brake
        (can be used to release brake)

        Optional keyword arguments

          brake
            flag if stopping with active brake
            
        Returns
        
          thread_task.Task object, which does the stopping
        '''
        assert isinstance(brake, bool), \
            'brake must be a boolean'
        return Task(
                self.stop,
                kwargs={'brake': brake}
        )

    def cont(self) -> None:
        '''
        continues a stopped movement
        '''
        if self._current_movement is None:
            # movement already has been finished
            return

        assert 'stopped' in self._current_movement, \
            "can't continue unstopped movement"

        if self._current_movement['op'] == 'Time_Speed':
            self.start_move_for(
                self._current_movement['duration_rest'],
                speed=self._current_movement['speed'],
                direction=self._current_movement['direction'],
                ramp_up_time=self._current_movement['ramp_up_time'],
                ramp_down_time=self._current_movement['ramp_down_time'],
                brake=self._current_movement['brake'],
                _control=True
            )
            return

        if self._current_movement['op'] == 'Step_Speed':
            self.start_move_to(
                self._current_movement['target_position'],
                speed=self._current_movement['speed'],
                ramp_up=self._current_movement['ramp_up'],
                ramp_down=self._current_movement['ramp_down'],
                brake=self._current_movement['brake'],
                _control=True
            )
            return

        if (
            self._current_movement['op'] == 'Speed' and
            'unlimited' in self._current_movement
        ):
            self.start(
                speed=abs(self._current_movement['speed']),
                direction=int(
                        math.copysign(1, self._current_movement['speed'])
                )
            )
            return

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
        self._current_movement['last_time'] = time.time()
        del self._current_movement['stopped']

    def cont_as_task(self) -> Task:
        '''
        continues a stopped movement
            
        Returns
        
          thread_task.Task object, which does the continuing
        '''
        return Task(self.cont)

    def _control_repeated(self):
        '''
        returns timespan to next call [s]
        '''
        if self._current_movement is None:
            # prevent needless data traffic
            return -1
        if self._current_movement['op'] != 'Speed':
            RuntimeError('concurrent movements')
        if 'last' in self._current_movement:
            # last one
            self._target_position = (
                self._current_movement['target_position']
            )
            self._current_movement = None
            return -1

        position = self.position
        now = time.time()

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

        if (
                delta_pos == 0 or
                math.copysign(1, speed) * delta_pos < 0
        ):
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


    def start_move_by(
        self,
        degrees: int,
        *,
        speed: int = None,
        ramp_up: int = None,
        ramp_down: int = None,
        brake: bool = False,
        _control: bool = False
    ) -> None:
        '''
        starts moving the motor by a given angle (without time control).

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
        assert isinstance(degrees, int), \
            'degrees must be an int value'

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up must be positive"

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'
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
                _control=_control
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

        speed *= round(
                math.copysign(1, degrees)
        )

        ops = b''.join((
            opInput_Device,
            READY_SI,
            LCX(0),  # LAYER
            port_motor_input(self._port),  # NO
            LCX(self.sensors_as_dict[port_motor_input(self._port)]),  # TYPE
            LCX(0),  # MODE (Degree)
            LCX(1),  # VALUES
            GVX(0),  # VALUE1 (output)

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS

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

        if _control:
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
        '''
        Periodic needs inverse flag of property busy
        '''
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

    def move_by(
        self,
        degrees: int,
        *,
        speed: int = None,
        ramp_up: int = None,
        ramp_down: int = None,
        brake: bool = False,
        duration: Number = None
    ) -> Task:
        '''
        exact and smooth movement of the motor by a given angle.

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
        assert isinstance(degrees, int), \
            'degrees must be an int value'

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up must be positive"

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'
        assert self._current_movement is None, \
            'concurrent movement in progress'

        assert duration is None or isinstance(duration, Number), \
            'duration must be a number'
        assert duration is None or duration > 0, \
            'duration must be positive'

        if speed is None:
            speed = self._speed
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down

        return Task(
                self.start_move_by,
                args=(degrees,),
                kwargs={
                    'speed': speed,
                    'ramp_up': ramp_up,
                    'ramp_down': ramp_down,
                    'brake': brake,
                    '_control': True
                },
                duration=self._delta_time,
                action_stop=self.stop,
                kwargs_stop={'brake': False},
                action_cont=self.cont
        ) + Periodic(
                self._delta_time,
                self._control_periodic,
                action_stop=self.stop,
                kwargs_stop={'brake': False},
                action_cont=self.cont               
        )

    def start_move_to(
        self,
        position: int,
        *,
        speed: int = None,
        ramp_up: int = None,
        ramp_down: int = None,
        brake: bool = False,
        _control: bool = False
    ):
        '''
        start moving the motor to a given position (without time control).

        Mandatory positional arguments

          position
            target position (degrees)

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          ramp_up
            degrees for ramp-up
          ramp_down
            degrees for ramp-down
          brake
            flag if ending with floating motor (False) or active brake (True).
        '''
        assert isinstance(position, int), \
            'position must be an int value'

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up must be positive"

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'

        assert isinstance(_control, bool), \
            '_control must be a boolean'

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
        ops = b''.join((

            opOutput_Reset,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS

            # current position

            opInput_Device,
            READY_SI,
            LCX(0),  # LAYER
            port_motor_input(self._port),  # NO
            LCX(self.sensors_as_dict[port_motor_input(self._port)]),  # TYPE (EV3-Medium-Motor)
            LCX(0),  # MODE (Degree)
            LCX(1),  # VALUES
            LVX(0),  # VALUE1 - from_position (DATAF)

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

        if self.sensors_as_dict[port_motor_input(self._port)] is None:
            reply = self.send_direct_cmd(ops, local_mem=24, global_mem=1)
            self.sensors_as_dict[port_motor_input(self._port)] = struct.unpack('<b', reply)[0]
        else:
            self.send_direct_cmd(ops, local_mem=24)

        if _control:
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

    def move_to(
        self,
        position: int,
        *,
        speed: int = None,
        ramp_up: int = None,
        ramp_down: int = None,
        brake: bool = False,
        duration: Number = None
    ) -> Task:
        '''
        move the motor to a given position.

        Mandatory positional arguments

          position
            target position (degrees)

        Optional keyword only arguments

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

          Task object, which can be started, stopped and continued.
        '''
        assert isinstance(position, int), \
            'position must be an int value'

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert ramp_up is None or isinstance(ramp_up, int), \
            "ramp_up must be an int"
        assert ramp_up is None or ramp_up >= 0, \
            "ramp_up must be positive"

        assert ramp_down is None or isinstance(ramp_down, int), \
            "ramp_down must be an int"
        assert ramp_down is None or ramp_down >= 0, \
            "ramp_down must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'

        assert duration is None or isinstance(duration, Number), \
            'duration must be a number'
        assert duration is None or duration > 0, \
            'duration must be positive'

        if speed is None:
            speed = self._speed
        if ramp_up is None:
            ramp_up = self._ramp_up
        if ramp_down is None:
            ramp_down = self._ramp_down
            
        if duration is not None:
            duration = max(0., duration - self._delta_time)

        return Task(
                self.start_move_to,
                args=(position,),
                kwargs={
                    'speed': speed,
                    'ramp_up': ramp_up,
                    'ramp_down': ramp_down,
                    'brake': brake,
                    '_control': True
                },
                duration=self._delta_time,
                action_stop=self.stop,
                kwargs_stop={'brake': False},
                action_cont=self.cont
        ) + Periodic(
                self._delta_time,
                self._control_periodic,
                duration=duration,
                action_stop=self.stop,
                kwargs_stop={'brake': False},
                action_cont=self.cont
        )

        
    def start_move_for(
        self,
        duration: float,
        *,
        speed: int = None,
        direction: int = 1,
        ramp_up_time: float = None,
        ramp_down_time: float = None,
        brake: bool = False,
        _control: bool = False
    ) -> None:
        '''
        start moving the motor for a given duration.

        Mandatory positional arguments

          duration
            duration of the movement [sec.]

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          direction
            direction of movement (-1 or 1)
          ramp_up_time
            duration time for ramp-up [sec.]
          ramp_down_time
            duration time for ramp-down [sec.]
          brake
            flag if ending with floating motor (False) or active brake (True).
        '''
        assert isinstance(duration, Number), \
            "duration must be a number"
        assert duration >= 0.001, \
            "duration must be at least one millisecond"

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert isinstance(direction, int), \
            'direction must be an int value'
        assert direction in (-1, 1), \
            'direction must be 1 (forwards) or -1 (backwards)'

        assert ramp_up_time is None or isinstance(ramp_up_time, Number), \
            "ramp_up_time must be a number"
        assert ramp_up_time is None or ramp_up_time >= 0, \
            "ramp_up_time must be positive"

        assert ramp_down_time is None or isinstance(ramp_down_time, Number), \
            "ramp_down_time must be a number"
        assert ramp_down_time is None or ramp_down_time >= 0, \
            "ramp_down_time must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if speed is None:
            speed = self._speed
        if ramp_up_time is None:
            ramp_up_time = self._ramp_up_time
        if ramp_down_time is None:
            ramp_down_time = self._ramp_down_time

        steady_ms = int(
                1000 *
                (duration - ramp_up_time - ramp_down_time)
        )
        if steady_ms < 0:
            speed = int(speed * duration / (ramp_up_time + ramp_down_time))
            steady_ms = 0
            ramp_up_ms = int(
                    1000 *
                    duration *
                    ramp_up_time /
                    (ramp_up_time + ramp_down_time)
            )
            ramp_down_ms = int(1000 * duration - ramp_up_ms)
        else:
            ramp_up_ms = int(1000 * ramp_up_time)
            ramp_down_ms = int(1000 * ramp_down_time)

        ops = b''.join((
            opOutput_Time_Speed,
            LCX(0),  # LAYER
            LCX(self._port),  # NOS
            LCX(direction * speed),  # SPEED
            LCX(ramp_up_ms),  # STEP1
            LCX(steady_ms),  # STEP2
            LCX(ramp_down_ms),  # STEP3
            LCX(1 if brake else 0),  # BRAKE - 1 (yes) or 0 (no)

            opOutput_Start,
            LCX(0),  # LAYER
            LCX(self._port)  # NOS
        ))
        self.send_direct_cmd(ops)

        if _control:
            self._current_movement = {
                'op': 'Time_Speed',
                'duration': duration,
                'speed': speed,
                'direction': direction,
                'ramp_up_time': ramp_up_time,
                'ramp_down_time': ramp_down_time,
                'brake': brake,
                'started_at': datetime.now()
            }
        else:
            self._target_position = None
            self._current_movement = None

        
    def move_for(
        self,
        duration: float,
        *,
        speed: int = None,
        direction: int = 1,
        ramp_up_time: float = None,
        ramp_down_time: float = None,
        brake: bool = False
    ) -> Task:
        '''
        start moving the motor for a given duration.

        Mandatory positional arguments

          duration
            duration of the movement [sec.]

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          direction
            direction of movement (-1 or 1)
          ramp_up_time
            duration time for ramp-up [sec.]
          ramp_down_time
            duration time for ramp-down [sec.]
          brake
            flag if ending with floating motor (False) or active brake (True).

        Returns

          Task object, which can be started, stopped and continued.
        '''
        assert isinstance(duration, Number), \
            "duration must be a number"
        assert duration >= 0.001, \
            "duration must be at least one millisecond"

        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert isinstance(direction, int), \
            'direction must be an int value'
        assert direction in (-1, 1), \
            'direction must be 1 (forwards) or -1 (backwards)'

        assert ramp_up_time is None or isinstance(ramp_up_time, Number), \
            "ramp_up_time must be a number"
        assert ramp_up_time is None or ramp_up_time >= 0, \
            "ramp_up_time must be positive"

        assert ramp_down_time is None or isinstance(ramp_down_time, Number), \
            "ramp_down_time must be a number"
        assert ramp_down_time is None or ramp_down_time >= 0, \
            "ramp_down_time must be positive"

        assert isinstance(brake, bool), \
            'brake must be a boolean'

        if speed is None:
            speed = self._speed
        if ramp_up_time is None:
            ramp_up_time = self._ramp_up_time
        if ramp_down_time is None:
            ramp_down_time = self._ramp_down_time

        return Task(
                self.start_move_for,
                args=(duration,),
                kwargs={
                    'speed': speed,
                    'direction': direction,
                    'ramp_up_time': ramp_up_time,
                    'ramp_down_time': ramp_down_time,
                    'brake': brake,
                    '_control': True
                },
                duration=duration,
                action_stop=self.stop,
                kwargs_stop={'brake': False},
                action_cont=self.cont
        ) + Task(
                self._final_move_for
        )

    
    def _final_move_for(self) -> None:
        '''
        correctly finishes a controlled movement move_for
        '''
        assert self._current_movement is not None, \
            'no controlled movement'
        assert self._current_movement['op'] == 'Time_Speed', \
            'not the expected movement: ' + self._current_movement['op']

        self._current_movement = None
        self._target_position = None

        
    def start_move(
        self,
        *,
        speed: int = None,
        direction: int = 1,
        ramp_up_time: float = None
    ) -> None:
        '''
        starts unlimited movement of the motor.

        Optional keyword only arguments

          speed
            percentage of maximum speed [1 - 100]
          direction
            direction of movement (-1 or 1)
          ramp_up_time
            duration time for ramp-up [sec.]
        '''
        assert speed is None or isinstance(speed, int), \
            'speed must be an int value'
        assert speed is None or 0 < speed and speed <= 100, \
            'speed  must be in range [1 - 100]'

        assert isinstance(direction, int), \
            'direction must be an int value'
        assert direction in (-1, 1), \
            'direction must be 1 (forwards) or -1 (backwards)'

        assert ramp_up_time is None or isinstance(ramp_up_time, Number), \
            "ramp_up_time must be a number"
        assert ramp_up_time is None or ramp_up_time >= 0, \
            "ramp_up_time must be positive"

        assert (
            self._current_movement is None or
            'stopped' in self._current_movement
        ), "concurrent movement in progress"

        if ramp_up_time is None:
            ramp_up_time = self._ramp_up_time

        self.start_move_for(
                2147483.847 - ramp_up_time,  # ~ 596.5 hours
                speed=speed,
                direction=direction,
                ramp_up_time=ramp_up_time,
                ramp_down_time=0
        )