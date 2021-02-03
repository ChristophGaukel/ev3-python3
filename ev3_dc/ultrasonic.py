#!/usr/bin/env python3
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
from .functions import (
    LCX,
    GVX
)
from .exceptions import (
        DirCmdError
)


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
        
        if (
                self._physical_ev3._sensors is not None and
                self._physical_ev3._sensors[self._port] not in (
                        NXT_ULTRASONIC,
                        EV3_ULTRASONIC
                )
                
        ):
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise DirCmdError('no ultrasonic connected at ' + port_str)
        
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
        if self._physical_ev3._sensors is None:
            reply = self.send_direct_cmd(
                    self._physical_ev3._introspection_dc(),
                    global_mem=16
            )
            self._physical_ev3._introspection_store(reply)
            if self._physical_ev3._sensors[self._port] not in (
                    NXT_ULTRASONIC,
                    EV3_ULTRASONIC
            ):
                port_str = 'PORT_' + str(1 + struct.unpack('<B', self._port)[0])
                raise DirCmdError('no ultrasonic connected at ' + port_str)
        return self._physical_ev3._sensors[self._port]

    @property
    def distance(self) -> float:
        """
        distance [m], where the sensor detected something
        
        distances are between 0.01 and 2.55 m. The distance
        2.55 m also stands for 'seen nothing'
        """

        if self._physical_ev3._sensors is None:
            port_int = struct.unpack("<B", self._port)[0]
            ops = b''.join((
                    self._physical_ev3._introspection_dc(offset=4),
                    opInput_Device,  # operation
                    READY_RAW,  # CMD
                    LCX(0),  # LAYER
                    self._port,  # NO
                    GVX(4 + port_int*2),  # TYPE
                    LCX(0),  # MODE (cm)
                    LCX(1),  # VALUES
                    GVX(0)  # VALUE1 (output)
            ))
            reply = self.send_direct_cmd(
                    ops,
                    global_mem=20
            )
            self._physical_ev3._introspection_store(reply[4:])
            if self._physical_ev3._sensors[self._port] not in (
                    NXT_ULTRASONIC,
                    EV3_ULTRASONIC
            ):
                port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
                raise DirCmdError('no ultrasonic connected at ' + port_str)
        else:
            if self._physical_ev3._sensors[self._port] not in (
                    NXT_ULTRASONIC,
                    EV3_ULTRASONIC
            ):
                port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
                raise DirCmdError('no ultrasonic connected at ' + port_str)
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

        return float(struct.unpack('<i', reply[:4])[0] / 100)
