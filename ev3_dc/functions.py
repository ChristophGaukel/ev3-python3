#!/usr/bin/env python3
'''
LEGO EV3 direct commands - functions
'''

import struct
from time import time
from typing import Callable
from numbers import Number

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


def pid(
        setpoint: float,
        gain: float,
        *,
        time_int: float = None,
        time_der: float = None
) -> Callable:
    """
    Parametrize a new PID controller (standard form)
    
    A PID controller derives a control signal from a measurement value

    Mandatory positional arguments

      setpoint
        target value of the measurement
      gain
        proportional gain,
        high values result in fast adaption,
        but too high values produce oscillations or instabilities

    Optional keyword only arguments

      time_int
        time of the integrative term [s] (approx. the time for elimination),
        compensates errors from the past (e.g. steady-state error)
        small values produce oscillations or instabilities
        and increase settling time
      time_der
        time of the derivative term [s] (approx. the forecast time),
        damps oszillations, decreases overshooting and reduces settling time
        but reacts sensitive on noise

    Returns
      function signal(value: float) -> float
    """
    assert isinstance(setpoint, Number), \
        'setpoint must be a number'
    assert isinstance(gain, Number) and gain > 0, \
        'gain must be a positive number'
    assert (
        time_int is None or
        isinstance(time_int, Number) and time_int >= 0
    ), 'time_int must be a positive number'
    assert isinstance(time_der, Number) and time_der >= 0, \
        'time_der must be a positive number'
    error_pre = None
    time_pre = None
    integral = None

    def signal(value: float) -> float:
        """
        calculates the control signal from the actually measured value

        Mandatory positional arguments
          value
            actually measured value (will be compared to setpoint)

        Returns
          control signal, which regulates the process
        """
        assert isinstance(value, Number), 'value must be a number'

        nonlocal error_pre, time_pre, integral

        if time_int is None and time_der is None:
            # P-controller (proportional term only)
            return gain * (setpoint - value)

        if time_pre is None:
            # first call
            time_pre = time()
            integral = 0
            error_pre = (setpoint - value)
            return gain * (setpoint - value)

        now = time()
        delta_time = now - time_pre
        time_pre = now
        error = (setpoint - value)

        if time_der is None:
            # PI-controller (no derivative term)
            integral += delta_time * error
            return gain * (error + integral / time_int)

        if time_int is None:
            # PD-controller (no integrative term)
            der = (error - error_pre) / delta_time
            error_pre = error
            return gain * (error + der * time_der)

        # PID-controller (proportional, integrative and derivative term)
        der = (error - error_pre) / delta_time
        error_pre = error
        integral += delta_time * error
        return gain * (error + integral / time_int + der * time_der)

    return signal


def corrector(
        *,
        actual: float = 0.0,
        factor: float = 1.0,
        target: float = 0.0
) -> Callable:
    """
    Parametrize a new corrector
    
    the corrector replaces actual values by target ones. In detail it does:
      - shift the measured value by actual (value -= actual)
      - multiply by factor (value *= factor)
      - shift back by target (value += target)

    this means, value actual is replaces by value target,
    other values, which are some distance apart from actual,
    also are shiftet, but additianally their distance from actual
    is corrected by factor.

    Optional keyword only arguments

      actual
        initial shift, set it to the measurement value, you are most insterested in
      factor
        linear correction of distances from actual
      target
        final shift, set it to the value, which you will replace actual with

    Returns
      function correct(value: float) -> float
    """
    assert isinstance(actual, Number), \
        'actual must be a number'
    assert isinstance(factor, Number) and factor != 0, \
        'factor must be a number and may not be zero'
    assert isinstance(target, Number), \
        'target must be a number'

    summand = target / factor - actual

    def correct(value: float) -> float:
        """
        calculates the target value from the actually measured one

        Mandatory positional arguments
          value
            actually measured value (will be compared to setpoint)

        Returns
          corrected value
        """
        assert isinstance(value, Number), 'value must be a number'

        return factor * (value + summand)

    return correct
