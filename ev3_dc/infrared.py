#!/usr/bin/env python3
"""
LEGO Mindstorms EV3 direct commands - infrared
"""

import struct
from collections import namedtuple
from typing import Tuple
from .ev3 import EV3
from .constants import (
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    opInput_Device,
    READY_RAW,
    EV3_IR
)
from .functions import (
    LCX,
    GVX
)
from .exceptions import (
        DirCmdError
)

    
Beacon = namedtuple('Beacon', [
        'heading',
        'distance'
])
Remote = namedtuple('Remote', [
        'permanent',
        'red_up',
        'red_down',
        'blue_up',
        'blue_down'
])

class Infrared(EV3):
    """
    controls a single infrared sensor
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
        Positional Arguments

          port
            port of infrared sensor (PORT_1, PORT_2, PORT_3 or PORT_4)

        Keyword only Arguments (either protocol and host or ev3_obj)

          protocol
            either ev3_dc.BLUETOOTH, ev3_dc.USB or ev3_dc.WIFI
          host
            mac-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            an existing EV3 object 
            (its already established connection will be used)
          channel
            beacon sends on this channel (1, 2, 3, 4)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).
        """
        assert port in (PORT_1, PORT_2, PORT_3, PORT_4), "incorrect port"
        self._port = port
        assert channel in (None, 1, 2, 3, 4), "incorrect channel"
        self._channel = channel

        super().__init__(
                protocol=protocol,
                host=host,
                ev3_obj=ev3_obj,
                verbosity=verbosity
        )
        
        if (
                self._physical_ev3._sensors is not None and
                self._physical_ev3._sensors[self._port] != EV3_IR
                
        ):
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            raise DirCmdError('no EV3_IR sensor connected at ' + port_str)
        
    def __str__(self):
        """description of the object in a str context"""
        port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
        return ' '.join((
                'EV3_IR',
                f'at {port_str}',
                f'of {super().__str__()}'
        ))
        
    def _validate_sensor_type(self):
        if self._physical_ev3._sensors[self._port] != EV3_IR:
            port_str = (
                    'PORT_' +
                    str(1 + struct.unpack("<B", self._port)[0])
            )
            raise DirCmdError('no EV3_IR connected at ' + port_str)

    @property
    def port(self) -> bytes:
        """
        port, where sensor is connected (PORT_1, PORT_2, PORT_3 or PORT_4)
        """
        return self._port
    
    @property
    def channel(self) -> int:
        """
        selected channel, on which the beacon sends
        """
        return self._channel
    
    @channel.setter
    def channel(self, value: int):
        assert isinstance(value, int), \
            'channel must be of type int'
        assert value in (1, 2, 3, 4), \
            'channel must be one of (1, 2, 3, 4)'
        self._channel = value

    @property
    def distance(self) -> float:
        """
        distance [m], where the sensor detected something (proximity mode).
        returned distances are between 0.01 and 1.00 m. The distance
        1.00 m also stands for 'seen nothing'
        """
        ops_values = b''.join((
                opInput_Device,  # operation
                READY_RAW,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                GVX(33),  # TYPE
                LCX(0),  # MODE (Proximity)
                LCX(1),  # VALUES
                GVX(0)  # VALUE1 (output)
        ))

        if self._physical_ev3._sensors is None:
            ops = b''.join((
                    self._physical_ev3._introspection_dc(offset=4),
                    ops_values,
            ))
            reply = self.send_direct_cmd(ops, global_mem=20)
            self._physical_ev3._introspection_store(reply[4:])
            self._validate_sensor_type()
        else:
            self._validate_sensor_type()
            reply = self.send_direct_cmd(ops_values, global_mem=4)

        return float(struct.unpack('<i', reply[:4])[0] / 100)

    @property
    def beacons(self) -> Tuple[Beacon]:
        """
        headings and distances [m] of detected beacons (seeker mode).
        returned headings are between -25 and 25: 

          -25 stands for far left

          0 stands for straight forward

          25 stands for far right
        
        returned distances are between 0.01 and 1.00 m.
        
        returns a tuple of four items, one per channel. 
        Each of them is either None or
        a namedtuple Beacon with heading and distance
        """
        ops_values = b''.join((
                opInput_Device,  # operation
                READY_RAW,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                GVX(EV3_IR),  # TYPE
                LCX(1),  # MODE (Seeker)
                LCX(8),  # VALUES
                GVX(0),  # VALUE1 - heading   channel 1
                GVX(4),  # VALUE2 - proximity channel 1
                GVX(8),  # VALUE3 - heading   channel 2
                GVX(12),  # VALUE4 - proximity channel 2
                GVX(16),  # VALUE5 - heading   channel 3
                GVX(20),  # VALUE6 - proximity channel 3
                GVX(24),  # VALUE7 - heading   channel 4
                GVX(28)  # VALUE8 - proximity channel 4
        ))

        if self._physical_ev3._sensors is None:
            ops = b''.join((
                    self._physical_ev3._introspection_dc(offset=32),
                    ops_values,
            ))
            reply = self.send_direct_cmd(ops, global_mem=48)
            self._physical_ev3._introspection_store(reply[32:])
            self._validate_sensor_type()
        else:
            self._validate_sensor_type()
            reply = self.send_direct_cmd(ops_values, global_mem=32)

        values = struct.unpack('<8i', reply[:32])
        return tuple(
                None 
                if values[2*n + 1] == -2147483648
                else Beacon(values[2*n], float(values[2*n + 1] / 100))
                for n in range(4)
        )

    @property
    def beacon(self) -> Beacon:
        """
        heading and distance [m] of detected the beacon (seeker mode).
        returned heading is between -25 and 25.
        
          -25 stands for far left
          
          0 stands for straight forward
          
          25 stands for far right
        
        returned distance is between 0.01 and 1.00 m.
        
        returns either None or namedtuple Beacon with heading and distance
        """
        
        assert self._channel is not None, \
          'no beacon channel has been set'
        
        return self.beacons[self._channel - 1]

    @property
    def remotes(self) -> Tuple[Remote]:
        """
        headings and distances [m] of detected beacons (remote mode).
        returned headings are between -25 and 25:
            
          -25 stands for far left
          
          0 stands for straight forward
          
          25 stands for far right
        
        returned distances are between 0.01 and 1.00 m.
        
        returns a tuple of four items, each of them is either None or
        a namedtuple Beacon with heading and distance
        """
        
        ops_values = b''.join((
                opInput_Device,  # operation
                READY_RAW,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                GVX(EV3_IR),  # TYPE
                LCX(2),  # MODE (Remote)
                LCX(4),  # VALUES
                GVX(0),  # VALUE1 - channel 1
                GVX(4),  # VALUE2 - channel 2
                GVX(8),  # VALUE3 - channel 3
                GVX(12)  # VALUE4 - channel 4
        ))

        if self._physical_ev3._sensors is None:
            ops = b''.join((
                    self._physical_ev3._introspection_dc(offset=16),
                    ops_values,
            ))
            reply = self.send_direct_cmd(ops, global_mem=32)
            self._physical_ev3._introspection_store(reply[16:])
            self._validate_sensor_type()
        else:
            self._validate_sensor_type()
            reply = self.send_direct_cmd(ops_values, global_mem=16)

        values = struct.unpack('<4i', reply[:16])
        result = []
        for n in range(4):
            if values[n] == 0:
                result.append(None)
            elif values[n] == 1:
                result.append(Remote(False, True, False, False, False))
            elif values[n] == 2:
                result.append(Remote(False, False, True, False, False))
            elif values[n] == 3:
                result.append(Remote(False, False, False, True, False))
            elif values[n] == 4:
                result.append(Remote(False, False, False, False, True))
            elif values[n] == 5:
                result.append(Remote(False, True, False, True, False))
            elif values[n] == 6:
                result.append(Remote(False, True, False, False, True))
            elif values[n] == 7:
                result.append(Remote(False, False, True, True, False))
            elif values[n] == 8:
                result.append(Remote(False, False, True, False, True))
            elif values[n] == 9:
                result.append(Remote(True, False, False, False, False))
            elif values[n] == 10:
                result.append(Remote(False, True, True, False, False))
            elif values[n] == 11:
                result.append(Remote(False, False, False, True, True))
            else:
                raise ValueError('undefined value: ' + str(values[n]))
        return tuple(result)

    @property
    def remote(self) -> Remote:
        """
        heading and distance [m] of detected beacon (remote mode)
        returned heading is between -25 and 25:
            
          -25 stands for far left
          
          0 stands for straight forward
          
          25 stands for far right
        
        returned distance is between 0.01 and 1.00 m.
        
        returns either None or namedtuple Beacon with heading and distance
        """
        
        assert self._channel is not None, \
          'no beacon channel has been set'
        
        return self.remotes[self._channel - 1]
