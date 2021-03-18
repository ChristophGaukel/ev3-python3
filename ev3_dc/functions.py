#!/usr/bin/env python3
'''
LEGO EV3 direct commands - functions
'''

import struct
from .constants import PORT_A, PORT_B, PORT_C, PORT_D


def LCX(value: int) -> bytes:
    """
    create a LC0, LC1, LC2, LC4, dependent from the value

    Positional Argument
      value
        integer value as argument of a direct command
    """
    assert isinstance(value, int), \
        "value needs to be an integer"

    if -32 <= value < 0:
        return struct.pack('b', 0x3F & (value + 64))
    if 0 <= value < 32:
        return struct.pack('b', value)
    if -127 <= value <= 127:
        return b'\x81' + struct.pack('<b', value)
    if -32767 <= value <= 32767:
        return b'\x82' + struct.pack('<h', value)
    return b'\x83' + struct.pack('<i', value)


def LCS(value: str) -> bytes:
    """
    pack a string into a LCS by adding a leading and a trailing byte

    Positional Argument
      value
        string as argument of a direct command
    """
    assert isinstance(value, str), \
        "value needs to be an string"

    return b'\x84' + str.encode(value) + b'\x00'


def LVX(value: int) -> bytes:
    """
    create a LV0, LV1, LV2, LV4, dependent from the value

    Positional Argument
      value
        position (bytes address) in the local memory
    """
    assert isinstance(value, int), \
        "value needs to be an integer"
    assert value >= 0, 'No negative values allowed'

    if value < 32:
        return struct.pack('b', 0x40 | value)
    if value < 256:
        return b'\xc1' + struct.pack('<b', value)
    if value < 65536:
        return b'\xc2' + struct.pack('<h', value)
    return b'\xc3' + struct.pack('<i', value)


def GVX(value: int) -> bytes:
    """
    create a GV0, GV1, GV2, GV4, dependent from the value

    Positional Argument
      value
        position (bytes address) in the global memory
    """
    assert isinstance(value, int), \
        "value needs to be an integer"
    assert value >= 0, 'No negative values allowed'

    if value < 32:
        return struct.pack('<b', 0x60 | value)
    if value < 256:
        return b'\xe1' + struct.pack('<b', value)
    if value < 65536:
        return b'\xe2' + struct.pack('<h', value)
    return b'\xe3' + struct.pack('<i', value)


def port_motor_input(port_output: int) -> bytes:
    """
    get corresponding input motor port (from output motor port)

    Positional Argument
      port_output
        motor port number
    """
    assert isinstance(port_output, int), \
        "port_output needs to be an integer"
    assert port_output in (PORT_A, PORT_B, PORT_C, PORT_D), \
        "port_output needs to be one of the numbers 1, 2, 4, 8"

    if port_output == PORT_A:
        return LCX(16)
    if port_output == PORT_B:
        return LCX(17)
    if port_output == PORT_C:
        return LCX(18)
    return LCX(19)
