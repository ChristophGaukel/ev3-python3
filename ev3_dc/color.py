"""
LEGO Mindstorms EV3 direct commands - color
"""

import struct
from typing import Tuple
from collections import namedtuple
from collections.abc import Iterable
from numbers import Number

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
from .exceptions import SensorError, PortInUse

RawRGBColor = namedtuple('RawRGBColor', [
        'red',
        'green',
        'blue'
])

RGBColor = namedtuple('RGBColor', [
        'red',
        'green',
        'blue'
])


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
        self._rgb_white_balance_raw = None

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

        if self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] is not None:
            port_str = 'PORT_' + str(1 + struct.unpack("<B", self._port)[0])
            host_str = self._physical_ev3._host
            raise PortInUse(f'{port_str} of {host_str} already in use')
        self._physical_ev3._introspection["sensors"] \
            [self._port]['used_by'] = self
        
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

    @property
    def rgb_raw(self) -> RawRGBColor:
        """
        surface color in front of the sensor as red, green, blue intensities
        
        intensities are reflected light intensities [0 - 1024]
        
        uses mode EV3-Color-Color, does not work with NXT-Color-Color
        """
        if self.sensors_as_dict[self._port] != EV3_COLOR:
            raise SensorError('rgb works only with EV3 color sensor')
        ops = b''.join((
                opInput_Device,  # operation
                READY_RAW,  # CMD
                LCX(0),  # LAYER
                self._port,  # NO
                LCX(self.sensors_as_dict[self._port]),  # EV3-Color or NXT-Color
                LCX(4),  # MODE (rgb)
                LCX(3),  # VALUES
                GVX(0),  # VALUE1 red (output)
                GVX(4),  # VALUE1 green (output)
                GVX(8)  # VALUE1 blue (output)
        ))
        reply = self.send_direct_cmd(ops, global_mem=12)
        return RawRGBColor(
            *struct.unpack('<3i', reply)
        )

    @property
    def rgb(self) -> RGBColor:
        """
        surface color in front of the sensor as red, green, blue intensities
        
        intensities are white balanced reflected light intensities [0 - 255]
        
        uses mode EV3-Color-Color, does not work with NXT-Color-Color
        """
        if self.sensors_as_dict[self._port] != EV3_COLOR:
            raise SensorError('rgb works only with EV3 color sensor')
        assert self._rgb_white_balance_raw is not None, "no white_balance done"
        rgb_raw = self.rgb_raw
        result = RGBColor(
            *(
                round(raw * 255 / white)
                for raw, white in zip(rgb_raw, self._rgb_white_balance_raw)
            )
        )
            
        if max(result) <= 255:
            return result
            
        fact = 255 / max(result)
        return RGBColor(
            *(
                round(fact * res)
                for res in result
            )
        )

    @property
    def rgb_white_balance(self) -> RawRGBColor:
        """
        perfect white surface in front of the sensor for calibration
        
        returned intensities are raw reflected light intensities [0 - 1024]
        
        uses mode EV3-Color-Color, does not work with NXT-Color-Color
        """
        if self.sensors_as_dict[self._port] != EV3_COLOR:
            raise SensorError('rgb works only with EV3 color sensor')
        self._rgb_white_balance_raw = self.rgb_raw
        return self._rgb_white_balance_raw
    
    @rgb_white_balance.setter
    def rgb_white_balance(self, raw: Iterable):
        if self.sensors_as_dict[self._port] != EV3_COLOR:
            raise SensorError('rgb works only with EV3 color sensor')
        assert isinstance(raw, Iterable) and len(raw) == 3, \
               "white_balance takes exactly 3 color values"
        for val in (raw):
            assert isinstance(val, Number), "white_balance must be 3 numbers"
            assert 0 <= val <= 1024, "values must be in range [0 - 1024]"
        if isinstance(raw, RawRGBColor):
            self._rgb_white_balance_raw = raw
        else:
            self._rgb_white_balance_raw = RawRGBColor(*raw)
        