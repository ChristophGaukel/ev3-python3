"""
LEGO Mindstorms EV3 direct commands - gyro
"""

import struct
from collections import namedtuple
from .ev3 import EV3
from .constants import (
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    opInput_Device,
    READY_RAW,
    EV3_GYRO
)
from .functions import LCX, GVX
from .exceptions import SensorError, PortInUse
    
GyroState = namedtuple('GyroState', [
        'angle',
        'rate'
])


class Gyro(EV3):
    """
    controls a single gyro sensor
    """

    def __init__(
            self,
            port: bytes,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            verbosity=0
    ):
        """
        Positional Arguments

          port
            port of gyro sensor (PORT_1, PORT_2, PORT_3 or PORT_4)

        Keyword only Arguments (either protocol and host or ev3_obj)

          protocol
            either ev3_dc.BLUETOOTH, ev3_dc.USB or ev3_dc.WIFI
          host
            mac-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object 
            (its already established connection will be used)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert port in (PORT_1, PORT_2, PORT_3, PORT_4), "incorrect port"
        self._port = port

        super().__init__(
                protocol=protocol,
                host=host,
                ev3_obj=ev3_obj,
                verbosity=verbosity
        )

        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(verbosity)
        
        if self.sensors_as_dict[self._port] != EV3_GYRO:
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise SensorError('no gyrosensor connected at ' + port_str)
        if self._physical_ev3._introspection["sensors"][self._port]['used_by'] is not None:
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            host_str = self._physical_ev3._host
            raise PortInUse(f'{port_str} of {host_str} already in use')
        
        # current angle is defined to be angle 0
        self._offset = 0
        self._offset = self.angle

        
    def __str__(self):
        """description of the object in a str context"""
        type_str = 'EV3_GYRO'
        port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
        return ' '.join((
                type_str,
                f'at {port_str}',
                f'of {super().__str__()}'
        ))

    def __del__(self):
        """
        handle specific logic for deletion
        """
        if self._physical_ev3 is not None:
            self._physical_ev3._introspection["sensors"][self._port]['used_by'] = None
            super().__del__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        handle specific logic when exit with block
        """
        self._physical_ev3._introspection["sensors"][self._port]['used_by'] = None
        super().__exit__(exc_type, exc_value, exc_traceback)

    @property
    def port(self) -> bytes:
        """
        port, where sensor is connected (PORT_1, PORT_2, PORT_3 or PORT_4)
        """
        return self._port

    @property
    def sensor_type(self) -> int:
        """
        type of sensor
        """
        return self.sensors_as_dict[self._port]

    @property
    def angle(self) -> int:
        """
        angle [degree] measured by gyro sensor
        """
        return self.state.angle

    @property
    def rate(self) -> int:
        """
        rate [degree/second] measured by gyro sensor
        """
        return self.state.rate

    @property
    def state(self) -> GyroState:
        """
        angle [degree] and rate [degree/second] measured by gyro sensor        
        """

        reply = self.send_direct_cmd(
                b''.join((
                    opInput_Device,  # operation
                    READY_RAW,  # CMD
                    LCX(0),  # LAYER
                    self._port,  # NO
                    LCX(self.sensors_as_dict[self._port]),  # TYPE
                    LCX(3),  # MODE
                    LCX(2),  # VALUES
                    GVX(0),  # VALUE1 (output)
                    GVX(4)  # VALUE2 (output)
                )),
                global_mem=8
        )
        angle, rate = struct.unpack('<2i', reply)
        return GyroState(angle - self._offset, rate)

    def reset(self, angle=0) -> int:
        """
        define current angle to be angle 0 (or another given value)

        Optional keyword only arguments

          angle
            sets the current angle to this value
            
        Returns
        
            current angle in previous normalization
        """
        cur_angle = self.angle
        self._offset += cur_angle - angle
        
        return cur_angle
