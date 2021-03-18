"""
LEGO Mindstorms EV3 direct commands - ultrasonic
"""

import struct
from .ev3 import EV3
from .constants import (
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    opInput_Device,
    READY_RAW,
    NXT_ULTRASONIC,
    EV3_ULTRASONIC
)
from .functions import LCX, GVX
from .exceptions import SensorError


class Ultrasonic(EV3):
    """
    controls a single ultrasonic sensor in cm mode
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
            port of ultrasonic sensor (PORT_1, PORT_2, PORT_3 or PORT_4)

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
                NXT_ULTRASONIC,
                EV3_ULTRASONIC
        ):
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise SensorError('no ultrasonic connected at ' + port_str)
        
    def __str__(self):
        """description of the object in a str context"""
        type_str = (
                'EV3_ULTRASONIC' 
                if self.sensor_type == EV3_ULTRASONIC
                else 'NXT_ULTRASONIC'
        )
        port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
        return ' '.join((
                type_str,
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
    def sensor_type(self) -> int:
        """
        type of sensor
        """
        return self.sensors_as_dict[self._port]

    @property
    def distance(self) -> float:
        """
        distance [m] ahead, where the sensor detected something
        
        distances are between 0.01 and 2.55 m. None stands for 'seen nothing'
        """

        reply = self.send_direct_cmd(
                b''.join((
                    opInput_Device,  # operation
                    READY_RAW,  # CMD
                    LCX(0),  # LAYER
                    self._port,  # NO
                    LCX(5),  # TYPE
                    LCX(0),  # MODE (cm)
                    LCX(1),  # VALUES
                    GVX(0)  # VALUE1 (output)
                )),
                global_mem=4
        )
        dist = struct.unpack('<i', reply)[0]
        if dist == 255:
            return None
        return float(dist/ 100)
