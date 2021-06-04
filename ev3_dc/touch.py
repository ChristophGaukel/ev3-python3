"""
LEGO Mindstorms EV3 direct commands - touch
"""

import struct
from .ev3 import EV3
from .constants import (
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    opInput_Device,
    READY_SI,
    CLR_CHANGES,
    NXT_TOUCH,
    EV3_TOUCH
)
from .functions import LCX, GVX
from .exceptions import SensorError, PortInUse


class Touch(EV3):
    """
    EV3 touch, controls a single touch sensor
    """

    def __init__(
            self,
            port: bytes,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            sync_mode: str = None,
            verbosity=0
    ):
        """
        Positional Arguments

          port
            port of touch sensor (PORT_1, PORT_2, PORT_3 or PORT_4)

        Keyword only Arguments (either protocol and host or ev3_obj)

          protocol
            either ev3_dc.BLUETOOTH, ev3_dc.USB or ev3_dc.WIFI
          host
            mac-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object (its connections will be used)
          sync mode (standard, asynchronous, synchronous)
            STD - if reply then use DIRECT_COMMAND_REPLY and
            wait for reply.

            ASYNC - if reply then use DIRECT_COMMAND_REPLY,
            but never wait for reply (it's the task of the calling program).

            SYNC - Always use DIRECT_COMMAND_REPLY and wait for reply,
            which may be empty.
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert port in (PORT_1, PORT_2, PORT_3, PORT_4), "incorrect port"
        self._port = port

        super().__init__(
                protocol=protocol,
                host=host,
                ev3_obj=ev3_obj,
                sync_mode=sync_mode,
                verbosity=verbosity
        )

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)
        
        if self.sensors_as_dict[self._port] not in (
                    NXT_TOUCH,
                    EV3_TOUCH
        ):
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise SensorError('no touch connected at ' + port_str)

        if self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] is not None:
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            host_str = self._physical_ev3._host
            raise PortInUse(f'{port_str} of {host_str} already in use')
        self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] = self
        
    def __str__(self):
        """description of the object in a str context"""
        type_str = (
                'EV3_TOUCH' if self.sensors_as_dict[self._port] == EV3_TOUCH 
                else 'NXT_TOUCH'
        )
        port_str = 'PORT_' + str(1 + struct.unpack("B", self._port)[0])
        return ' '.join((
                f'{type_str}',
                f'at {port_str}',
                f'of {super().__str__()}'
        ))

    def __del__(self):
        """
        handle specific logic for deletion
        """
        self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] = None
        super().__del__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        handle specific logic when exit with block
        """
        self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] = None
        super().__exit__(exc_type, exc_value, exc_traceback)

    @property
    def port(self) -> bytes:
        """
        port, where touch sensor is connected (PORT_1, PORT_2, PORT_3 or PORT_4)
        """
        return self._port

    @property
    def sensor_type(self) -> int:
        """
        type of sensor
        """
        return self.sensors_as_dict[self._port]

    @property
    def touched(self) -> bool:
        """
        flag, that tells if sensor is currently touched
        """

        reply = self.send_direct_cmd(
                b''.join((
                    opInput_Device,  # operation
                    READY_SI,  # CMD
                    LCX(0),  # LAYER
                    self._port,  # NO
                    LCX(self.sensors_as_dict[self._port]),  # TYPE
                    LCX(0),  # MODE (Touch)
                    LCX(1),  # VALUES
                    GVX(0)  # VALUE1 (output)
                )),
                global_mem=4
        )
        touched = struct.unpack('<f', reply[:4])[0]

        return bool(touched)

    @property
    def bumps(self) -> int:
        """
        number of bumps since last clearing of bump counter
        """
        reply = self.send_direct_cmd(
                b''.join((
                    opInput_Device,  # operation
                    READY_SI,  # CMD
                    LCX(0),  # LAYER
                    self._port,  # NO
                    LCX(self.sensors_as_dict[self._port]),  # TYPE
                    LCX(1),  # MODE (Touch)
                    LCX(1),  # VALUES
                    GVX(0)  # VALUE1 (output)
                )),
                global_mem=4
        )
        bumps = struct.unpack('<f', reply[:4])[0]
        
        return int(bumps)

    @bumps.setter
    def bumps(self, value: int):
        assert isinstance(value, int), \
            "bumps needs to be of type int"
        assert value == 0, \
            "value of bumps: " + str(value) + " is invalid (must be 0)"
        self.clear()

    def clear(self) -> None:
        """
        clears bump counter of touch sensor
        """
        self.send_direct_cmd(
                b''.join((
                    opInput_Device,  # operation
                    CLR_CHANGES,  # CMD
                    LCX(0),  # LAYER
                    self._port  # NO
                ))
         )
 