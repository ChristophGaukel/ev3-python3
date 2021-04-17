"""
LEGO Mindstorms EV3 direct commands - color
"""

import struct
from .ev3 import EV3
from .constants import (
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    opInput_Device,
    READY_PCT,
    READY_RAW,
    EV3_COLOR,
    NXT_COLOR
)
from .functions import LCX, GVX
from .exceptions import SensorError


class Color(EV3):
    """
    controls a single color sensor
    """

    def __init__(
            self,
            port: bytes,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: EV3 = None,
            channel: int = None,
            verbosity=0
    ):
        """
        Mandatory positional Arguments

          port
            port of color sensor (PORT_1, PORT_2, PORT_3 or PORT_4)

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
        
        if self.sensors_as_dict[self._port] not in (
                EV3_COLOR,
                NXT_COLOR
        ):
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise SensorError('no color sensor connected at ' + port_str)
        
    def __str__(self):
        """description of the object in a str context"""
        port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
        if self.sensors_as_dict[self._port] == EV3_COLOR:
            sensor_str = 'EV3_Color'
        else:
            sensor_str = 'NXT_Color'
        return ' '.join((
                sensor_str,
                f'at {port_str}',
                f'of {super().__str__()}'
        ))

    @property
    def port(self) -> bytes:
        """
        port, where sensor is connected (PORT_1, PORT_2, PORT_3 or PORT_4)
        """
        return self._port

    @property
    def reflected(self) -> int:
        """
        intensity of the reflected (red) light in percent [0 - 100]
        
        uses modes EV3-Color-Reflected or NXT-Color-Reflected
        """
        ops = b''.join((
                opInput_Device,  # operation
                READY_PCT,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                LCX(self.sensors_as_dict[self._port]),  # EV3-Color or NXT-Color
                LCX(0),  # MODE (Reflected)
                LCX(1),  # VALUES
                GVX(0)  # VALUE1 (output)
        ))
        reply = self.send_direct_cmd(ops, global_mem=1)
        return struct.unpack('B', reply)[0]

    @property
    def ambient(self) -> int:
        """
        intensity of ambient light in percent [0 - 100]
        
        uses modes EV3-Color-Ambient or NXT-Color-Ambient
        """
        ops = b''.join((
                opInput_Device,  # operation
                READY_PCT,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                LCX(self.sensors_as_dict[self._port]),  # EV3-Color or NXT-Color
                LCX(1),  # MODE (ambient)
                LCX(1),  # VALUES
                GVX(0)  # VALUE1 (output)
        ))
        reply = self.send_direct_cmd(ops, global_mem=1)
        return struct.unpack('B', reply)[0]

    @property
    def color(self) -> int:
        """
        surface color in front of the sensor
        
        0: none, 1: black, 2: blue, 3: green, 4: yellow, 5: red,
        6: white, 7: brown
        
        uses modes EV3-Color-Color or NXT-Color-Color
        """
        ops = b''.join((
                opInput_Device,  # operation
                READY_RAW,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                LCX(self.sensors_as_dict[self._port]),  # EV3-Color or NXT-Color
                LCX(2),  # MODE (color)
                LCX(1),  # VALUES
                GVX(0)  # VALUE1 (output)
        ))
        reply = self.send_direct_cmd(ops, global_mem=4)
        return struct.unpack('<i', reply)[0]
