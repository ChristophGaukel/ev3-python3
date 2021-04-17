#!/usr/bin/env python3
'''
LEGO EV3 direct commands - ev3
'''

import re
import usb.util
import socket
import struct
from collections import namedtuple
from time import sleep
from datetime import datetime, timedelta
from threading import Lock
from .exceptions import NoEV3, DirCmdError, SysCmdError
from .constants import (
    _ID_VENDOR_LEGO,
    _ID_PRODUCT_EV3,
    _EP_IN,
    _EP_OUT,
    _DIRECT_COMMAND_REPLY,
    _DIRECT_COMMAND_NO_REPLY,
    _DIRECT_REPLY,
    _SYSTEM_COMMAND_REPLY,
    _SYSTEM_COMMAND_NO_REPLY,
    _SYSTEM_REPLY,
    WIFI,
    BLUETOOTH,
    USB,
    STD,
    ASYNC,
    SYNC,
    
    # introspection
    opInfo,
    opInput_Device,
    opMemory_Usage,
    opCom_Get,
    opCom_Set,
    opUI_Read,
    GET_TYPEMODE,
    GET_VOLUME,
    GET_MINUTES,
    GET_VBATT,
    GET_IBATT,
    GET_LBATT,
    GET_BRICKNAME,
    GET_OS_VERS,
    GET_OS_BUILD,
    GET_HW_VERS,
    GET_FW_BUILD,
    GET_FW_VERS,
    GET_NETWORK,
    SET_BRICKNAME,
    SET_VOLUME,
    SET_MINUTES,
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
    PORT_A_SENSOR,
    PORT_B_SENSOR,
    PORT_C_SENSOR,
    PORT_D_SENSOR
)
from .functions import LCX, GVX, LCS

Battery = namedtuple('Battery', [
        'voltage',
        'current',
        'percentage'
])

Memory = namedtuple('Memory', [
        'total',
        'free'
])

Sensors = namedtuple('Sensors', [
        'Port_1',
        'Port_2',
        'Port_3',
        'Port_4',
        'Port_A',
        'Port_B',
        'Port_C',
        'Port_D'
])

Network = namedtuple('Network', [
        'name',
        'ip_adr',
        'mac_adr'
])

System = namedtuple('System', [
        'os_version',
        'os_build',
        'fw_version',
        'fw_build',
        'hw_version'
])

class _PhysicalEV3:
    '''
    holds data and methods, which are singletons per physical EV3 device
    '''
    def __init__(
        self,
        protocol: str,
        host: str,
    ):
        assert isinstance(protocol, str), \
            'protocol needs to be of type str'
        assert protocol in (BLUETOOTH, WIFI, USB), \
            'Protocol ' + protocol + 'is not valid'
        assert isinstance(host, str), \
            "host needs to be of type str"

        self._msg_cnt = 41
        self._lock = Lock()
        self._reply_buffer = {}
        self._protocol = protocol
        self._host = host
        self._device = None
        self._socket = None
        self._name = None
        self._ip_adr = None
        self._introspection = None

        if protocol == BLUETOOTH:
            self._connect_bluetooth()
        elif protocol == WIFI:
            self._connect_wifi()
        else:
            self._connect_usb()

    def __del__(self):
        """
        closes the connection to the LEGO EV3
        """
        if (
            self._socket is not None and
            isinstance(self._socket, socket.socket)
        ):
            self._socket.close()

    def next_msg_cnt(self) -> int:
        '''
        determines next message counter
        '''
        if self._msg_cnt < 65535:
            self._msg_cnt += 1
        else:
            self._msg_cnt = 1
        return self._msg_cnt

    def put_to_reply_buffer(self, msg_cnt: bytes, reply: bytes) -> None:
        """
        put a reply to the stack
        """
        if msg_cnt in self._reply_buffer:
            raise ValueError(
                'reply with msg_cnt ' +
                ':'.join('{:02X}'.format(byte) for byte in msg_cnt) +
                ' already exists'
            )
        else:
            self._reply_buffer[msg_cnt] = reply

    def _connect_bluetooth(self) -> int:
        """
        Create a socket, that holds a bluetooth-connection to an EV3
        """
        self._socket = socket.socket(
            socket.AF_BLUETOOTH,
            socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM
        )
        try:
            self._socket.connect((self._host, 1))
        except OSError:
            raise NoEV3('EV3 brick not found') from None

    def _connect_wifi(self) -> int:
        """
        Create a socket, that holds a WiFi-connection to an EV3
        """

        # listen on port 3015 for a UDP broadcast from the EV3
        started_at = datetime.now()
        while True:
            UDPSock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            UDPSock.settimeout(10)
            UDPSock.bind(('', 3015))
            try:
                data, addr = UDPSock.recvfrom(67)
            except socket.timeout:
                raise NoEV3('no EV3 brick found') from None

            # pick serial number, port, name and protocol
            # from the broadcast message
            matcher = re.search(
                r'^Serial-Number: (\w*)\s\n' +
                r'Port: (\d{4,4})\s\n' +
                r'Name: (\w+)\s\n' +
                r'Protocol: (\w+)',
                data.decode('utf-8')
            )
            serial_number = matcher.group(1)
            port = matcher.group(2)
            name = matcher.group(3)
            protocol = matcher.group(4)

            # test if correct mac-addr
            if (
                    serial_number.upper() == self._host.replace(':', '').upper()
            ):
                break

            if datetime.now() - started_at > timedelta(seconds=10):
                raise NoEV3('EV3 brick found, but not ' + self._host)

        # Send an UDP message back to the EV3
        # to make it accept a TCP/IP connection
        UDPSock.sendto(' '.encode('utf-8'), (addr[0], int(port)))
        UDPSock.close()

        # Establish a TCP/IP connection with EV3's address and port
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self._socket.connect((addr[0], int(port)))

        # Send an unlock message to the EV3 over TCP/IP
        msg = 'GET /target?sn=' + serial_number + 'VMTP1.0\n' + \
              'Protocol: ' + protocol
        self._socket.send(msg.encode('utf-8'))
        reply = self._socket.recv(16).decode('utf-8')
        if not reply.startswith('Accept:EV340'):
            raise RuntimeError(
                'No WiFi connection to ' +
                name +
                ' established'
            )

    def _connect_usb(self) -> int:
        """
        Create a device, that holds an USB connection to an EV3
        """
        ev3_devices = usb.core.find(
            find_all=True,
            idVendor=_ID_VENDOR_LEGO,
            idProduct=_ID_PRODUCT_EV3
        )

        # identify EV3 device
        for dev in ev3_devices:
            if self._device:
                raise ValueError(
                    'found multiple EV3 but argument host was not set'
                )
            if self._host:
                mac_addr = usb.util.get_string(dev, dev.iSerialNumber)
                if mac_addr.upper() == self._host.replace(':', '').upper():
                    self._device = dev
                    break
            else:
                self._device = dev
        if not self._device:
            raise NoEV3("Lego EV3 not found")

        # handle interfaces
        for i in self._device.configurations()[0].interfaces():
            try:
                if self._device.is_kernel_driver_active(i.index):
                    self._device.detach_kernel_driver(i.index)
            except NotImplementedError:
                pass
        self._device.set_configuration()

        # initial read
        self._device.read(_EP_IN, 1024, 100)

    def introspection(self, verbosity: int) -> None:
        """
        reads informations about itself
        """
        ports = (
                PORT_1,
                PORT_2,
                PORT_3,
                PORT_4,
                PORT_A_SENSOR,
                PORT_B_SENSOR,
                PORT_C_SENSOR,
                PORT_D_SENSOR
        )
        ops = b''
        for i in range(8):
            ops += b''.join((
                opInput_Device,  # operation
                GET_TYPEMODE,  # CMD
                LCX(0),  # LAYER
                ports[i],  # NO
                GVX(2*i),  # TYPE (output)
                GVX(2*i + 1)  # MODE (output)
            ))
        ops += b''.join((
                opMemory_Usage,    
                GVX(16),  # TOTAL (out)
                GVX(20),  # FREE (out)
                opInfo,
                GET_VOLUME ,  # CMD
                GVX(24) , # VALUE
                opInfo,
                GET_MINUTES ,  # CMD
                GVX(25) , # VALUE
                opCom_Get,
                GET_BRICKNAME,  # CMD
                LCX(32),  # LENGTH
                GVX(26),  # NAME (out)
                opUI_Read,
                GET_OS_VERS,  # CMD
                LCX(16),  # LENGTH
                GVX(58),  # NAME (out)
                opUI_Read,
                GET_HW_VERS,  # CMD
                LCX(8),  # LENGTH
                GVX(74),  # NAME (out)
                opUI_Read,
                GET_FW_VERS,  # CMD
                LCX(8),  # LENGTH
                GVX(82),  # NAME (out)
                opUI_Read,
                GET_OS_BUILD,  # CMD
                LCX(12),  # LENGTH
                GVX(90),  # NAME (out)
                opUI_Read,
                GET_FW_BUILD,  # CMD
                LCX(12),  # LENGTH
                GVX(102)  # NAME (out)
        ))
        reply = self.send_direct_cmd(
                ops,
                global_mem=114,
                verbosity=verbosity,
                sync_mode=SYNC
        )

        self._introspection = {}
        self._introspection["sensors"] = {}
        for i in range(8):
            sensor_type, sensor_mode = struct.unpack(
                '<BB',
                reply[2*i:2*i+2]
            )
            if sensor_type == 126:
                self._introspection["sensors"][ports[i]] = None
            else:
                self._introspection["sensors"][ports[i]] = sensor_type
        (
                self._introspection["mem_total"],
                self._introspection["mem_free"],
                self._introspection["volume"],
                self._introspection["sleep"],
                name,
                os_vers,
                hw_vers,
                fw_vers,
                os_build,
                fw_build
        ) = struct.unpack(
                '<2i2B32s16s8s8s12s12s',
                reply[16:]
        )

        self._introspection["name"] = name.split(b'\x00')[0].decode("utf8")
        self._introspection["os_vers"] = os_vers.split(b'\x00')[0].decode("utf8")
        self._introspection["os_build"] = os_build.split(b'\x00')[0].decode("utf8")
        self._introspection["fw_vers"] = fw_vers.split(b'\x00')[0].decode("utf8")
        self._introspection["fw_build"] = fw_build.split(b'\x00')[0].decode("utf8")
        self._introspection["hw_vers"] = hw_vers.split(b'\x00')[0].decode("utf8")
        
        if self._protocol == WIFI:
            ops = b''.join((
                opCom_Get,
                GET_NETWORK,
                LCX(3),  # HARDWARE
                LCX(42),  # LENGTH
                GVX(0),  # NAME
                GVX(42),  # MAC
                GVX(84)  # IP
            ))
            (
                    self._introspection["network_name"],
                    self._introspection["network_mac_adr"],
                    self._introspection["network_ip_adr"]
            ) = [
                    value.split(b'\x00')[0].decode("utf8")
                    for value in struct.unpack(
                            '42s42s42s',
                            self.send_direct_cmd(
                                    ops,
                                    global_mem=126,
                                    verbosity=verbosity,
                                    sync_mode=SYNC
                            )
                    )
            ]
            self._introspection["network_mac_adr"] = ':'.join(
                    self._introspection["network_mac_adr"][i:i+2]
                    for i in range(6)
            )

    def send_direct_cmd(
        self,
        ops: bytes,
        *,
        verbosity: int,
        local_mem: int = 0,
        global_mem: int = 0,
        sync_mode: str = None
    ) -> bytes:
        """
        Send a direct command to the LEGO EV3
        """
        
        if sync_mode == None:
            if self._protocol == USB:
                sync_mode = SYNC
            else:
                sync_mode = STD

        self._lock.acquire()

        if (
                global_mem > 0 or
                sync_mode == SYNC
        ):
            cmd_type = _DIRECT_COMMAND_REPLY
        else:
            cmd_type = _DIRECT_COMMAND_NO_REPLY

        msg_cnt = self.next_msg_cnt()

        cmd = b''.join((
            struct.pack('<HH', len(ops) + 5, msg_cnt),
            cmd_type,
            struct.pack('<H', local_mem * 1024 + global_mem),
            ops
        ))

        if verbosity is not None and verbosity > 0:
            print(
                datetime.now().strftime('%H:%M:%S.%f') +
                ' Sent 0x|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[5:7]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[7:]) + '|'
            )

        if self._protocol in (BLUETOOTH, WIFI):
            self._socket.send(cmd)
        else:
            self._device.write(_EP_OUT, cmd, 100)

        msg_cnt = cmd[2:4]
        if (
                cmd[4:5] == _DIRECT_COMMAND_NO_REPLY or
                sync_mode == ASYNC
        ):
            self._lock.release()
            return msg_cnt
        else:
            return self.wait_for_reply(
                msg_cnt,
                verbosity=verbosity,
                _locked=True
            )

    def wait_for_reply(
        self,
        msg_cnt: bytes,
        verbosity: int = None,
        _locked: bool = False
    ) -> bytes:
        """
        Ask the LEGO EV3 for a reply and wait until it is received
        """

        if not _locked:
            self._lock.acquire()

        # reply already in buffer?
        reply = self._reply_buffer.pop(msg_cnt, None)
        if reply is not None:
            self._lock.release()
            if reply[4:5] == _DIRECT_REPLY:
                return reply[5:]
            raise DirCmdError(
                "direct command {:02X}:{:02X} replied error".format(
                    reply[2],
                    reply[3]
                )
            )

        #  get replies from EV3 device until msg_cnt fits
        while True:
            if self._protocol in (BLUETOOTH, WIFI):
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(_EP_IN, 1024, 0))
            len_data = struct.unpack('<H', reply[:2])[0] + 2
            msg_cnt_reply = reply[2:4]
            if verbosity is not None and verbosity > 0:
                print(
                    datetime.now().strftime('%H:%M:%S.%f') +
                    ' Recv 0x|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[0:2]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[2:4]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[4:5]) +
                    '|', end=''
                )
                if len_data > 5:
                    dat = ':'.join(
                        '{:02X}'.format(byte) for byte in reply[5:len_data]
                    )
                    print(dat + '|')
                else:
                    print()

            if msg_cnt != msg_cnt_reply:
                # does not fit, put reply into buffer
                self.put_to_reply_buffer(
                    msg_cnt_reply,
                    reply[:len_data]
                )
            else:
                self._lock.release()
                if reply[4:5] == _DIRECT_REPLY:
                    return reply[5:len_data]
                raise DirCmdError(
                    "direct command {:02X}:{:02X} replied error".format(
                        reply[2],
                        reply[3]
                    )
                )

    def send_system_cmd(
        self,
        cmd: bytes,
        *,
        verbosity: int,
        reply: bool = True
    ) -> bytes:
        """
        Send a system command to the LEGO EV3
        """

        self._lock.acquire()

        if reply:
            cmd_type = _SYSTEM_COMMAND_REPLY
        else:
            cmd_type = _SYSTEM_COMMAND_NO_REPLY
        msg_cnt = self.next_msg_cnt()
        cmd = b''.join((
            struct.pack('<hh', len(cmd) + 3, msg_cnt),
            cmd_type,
            cmd
        ))
        if verbosity >= 1:
            print(
                datetime.now().strftime('%H:%M:%S.%f') +
                ' Sent 0x|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|' +
                ':'.join('{:02X}'.format(byte) for byte in cmd[5:]) + '|'
            )
        if self._protocol in (BLUETOOTH, WIFI):
            self._socket.send(cmd)
        else:
            self._device.write(_EP_OUT, cmd, 100)

        msg_cnt = cmd[2:4]
        if not reply:
            self._lock.release()
            return msg_cnt
        else:
            return self._wait_for_system_reply(
                msg_cnt,
                verbosity=verbosity,
                _locked=True
            )

    def _wait_for_system_reply(
            self,
            msg_cnt: bytes,
            *,
            verbosity: int,
            _locked=False
    ) -> bytes:
        """
        Ask the LEGO EV3 for a system command reply and wait until received
        """

        if not _locked:
            self._lock.acquire()

        # reply already in buffer?
        reply = self._reply_buffer.pop(msg_cnt, None)
        if reply is not None:
            self._lock.release()
            if reply[4:5] == _SYSTEM_REPLY:
                return reply[6:]
            raise SysCmdError(
                "system command {:02X}:{:02X} replied error".format(
                    reply[2],
                    reply[3]
                )
            )

        #  get replies from EV3 device until msg_cnt fits
        while True:
            if self._protocol == BLUETOOTH:
                sleep(0.1)
            if self._protocol in (BLUETOOTH, WIFI):
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(_EP_IN, 1024, 0))
            len_data = struct.unpack('<H', reply[:2])[0] + 2
            reply_msg_cnt = reply[2:4]

            if (
                    verbosity is not None and verbosity > 0 or
                    verbosity is None and self._verbosity > 0
            ):
                print(
                    datetime.now().strftime('%H:%M:%S.%f') +
                    ' Recv 0x|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[0:2]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[2:4]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[4:5]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[5:6]) +
                    '|' +
                    ':'.join('{:02X}'.format(byte) for byte in reply[6:7]) +
                    '|',
                    end=''
                )
                if len_data > 7:
                    dat = ':'.join(
                        '{:02X}'.format(byte) for byte in reply[7:len_data]
                    )
                    print(dat + '|')
                else:
                    print()

            if msg_cnt != reply_msg_cnt:
                self.put_to_reply_buffer(
                    reply_msg_cnt,
                    reply[:len_data]
                )
            else:
                self._lock.release()
                if reply[4:5] == _SYSTEM_REPLY:
                    return reply[6:len_data]
                raise SysCmdError(
                    "system command {:02X}:{:02X} replied error".format(
                        reply[2],
                        reply[3]
                    )
                )


class EV3:
    """
    communicates with a LEGO EV3 using direct or system commands
    """

    def __init__(
            self,
            *,
            protocol: str = None,
            host: str = None,
            ev3_obj: 'EV3' = None,
            sync_mode: str = None,
            verbosity=0
    ):
        """
        Establish a connection to a LEGO EV3 device

        Keyword arguments (either protocol and host or ev3_obj)

          protocol
            'Bluetooth', 'USB' or 'WiFi'
          host
            MAC-address of the LEGO EV3 (e.g. '00:16:53:42:2B:99')
          ev3_obj
            existing EV3 object (its connections will be used)
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
        assert ev3_obj or protocol, \
            'Either protocol or ev3_obj needs to be given'
        if ev3_obj:
            assert isinstance(ev3_obj, EV3), \
                'ev3_obj needs to be instance of EV3'
            self._physical_ev3 = ev3_obj._physical_ev3
        else:
            self._physical_ev3 = _PhysicalEV3(protocol, host)

        assert isinstance(verbosity, int), \
            "verbosity needs to be of type int"
        assert verbosity >= 0 and verbosity <= 2, \
            "allowed verbosity values are: 0, 1 or 2"
        self._verbosity = int(verbosity)

        assert sync_mode is None or isinstance(sync_mode, str), \
            "sync_mode needs to be of type str"
        assert sync_mode is None or sync_mode in (STD, SYNC, ASYNC), \
            "value of sync_mode: " + sync_mode + " is invalid"

        if sync_mode is None and self._physical_ev3._protocol == USB:
            self._sync_mode = SYNC
        else:
            self._sync_mode = STD
            
    def __enter__(self):
        """
        allows to code 'with EV3 as my_ev3:'
        """
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        allows a clean exit from with block
        """
        self._physical_ev3.__del__()
        
    def __str__(self):
        """representation of the object in a str context"""
        return ' '.join((
                f'{self.protocol}',
                f'connected EV3 {self.host}',
                f'({self.name})'
        ))

    @property
    def battery(self) -> Battery:
        """
        battery voltage [V], current [A] and percentage (as named tuple)
        """
        reply = self._physical_ev3.send_direct_cmd(
                b''.join((
                    opUI_Read,
                    GET_VBATT,
                    GVX(0),
                    opUI_Read,
                    GET_IBATT,
                    GVX(4),
                    opUI_Read,
                    GET_LBATT,
                    GVX(8)
                )),
                global_mem=9,
                verbosity=self._verbosity,
                sync_mode=self._sync_mode
        )
        return Battery(
                *struct.unpack('<2fB', reply)
        )

    @property
    def host(self) -> str:
        """
        mac address of EV3 device
        """
        return self._physical_ev3._host

    @property
    def memory(self) -> Memory:
        """
        total and free memory [kB] (as named tuple)
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return Memory(
                self._physical_ev3._introspection["mem_total"],
                self._physical_ev3._introspection["mem_free"]
        )

    @property
    def name(self) -> str:
        """
        name of EV3 device
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return self._physical_ev3._introspection["name"]

    @name.setter
    def name(self, value: str):
        assert isinstance(value, str), "name needs to be of type str"
        assert value != '', "name may not be an empty string"
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        if value != self._physical_ev3._introspection["name"]:
            self._physical_ev3.send_direct_cmd(
                    b''.join((
                            opCom_Set,  # operation
                            SET_BRICKNAME,  # CMD
                            LCS(value)  # NAME
                    )),
                    verbosity=self._verbosity,
                    sync_mode=self._sync_mode
            )
            self._physical_ev3._introspection["name"] = value

    @property
    def network(self) -> str:
        """
        name, ip_adr and mac_adr of the EV3 device (as named tuple)
        
        available only for WiFi connected devices,
        mac_adr is the address of the WiFi dongle
        """
        assert self._physical_ev3._protocol == WIFI, \
          'available only for WiFi connected devices'
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return Network(
                self._physical_ev3._introspection["network_name"],
                self._physical_ev3._introspection["network_ip_adr"],
                self._physical_ev3._introspection["network_mac_adr"]
        )

    @property
    def protocol(self) -> str:
        """
        connection type
        """
        return self._physical_ev3._protocol

    @property
    def sensors(self) -> Sensors:
        """
        all connected sensors and motors at all ports (as named tuple Sensors)
        
        You can address a single one by e.g.:
        ev3_dc.EV3.sensors.Port_3 or
        ev3_dc.EV3.sensors.Port_C
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return Sensors(
                self._physical_ev3._introspection["sensors"][PORT_1],
                self._physical_ev3._introspection["sensors"][PORT_2],
                self._physical_ev3._introspection["sensors"][PORT_3],
                self._physical_ev3._introspection["sensors"][PORT_4],
                self._physical_ev3._introspection["sensors"][PORT_A_SENSOR],
                self._physical_ev3._introspection["sensors"][PORT_B_SENSOR],
                self._physical_ev3._introspection["sensors"][PORT_C_SENSOR],
                self._physical_ev3._introspection["sensors"][PORT_D_SENSOR]
        )

    @property
    def sensors_as_dict(self) -> dict:
        """
        all connected sensors and motors at all ports (as dict)
        
        You can address a single one by e.g.:
        ev3_dc.EV3.sensors_as_dict[ev3_dc.PORT_1] or
        ev3_dc.EV3.sensors_as_dict[ev3_dc.PORT_A_SENSOR]
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return self._physical_ev3._introspection["sensors"]

    @property
    def sleep(self) -> int:
        """
        idle minutes until EV3 shuts down, values from 0 to 120
        
        value 0 says: never shut down
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return self._physical_ev3._introspection["sleep"]

    @sleep.setter
    def sleep(self, value: int):
        assert isinstance(value, int), "sleep needs to be of type int"
        assert 0 <= value <= 120, "sleep must be between 0 and 120"
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        if value != self._physical_ev3._introspection["sleep"]:
            self._physical_ev3.send_direct_cmd(
                    b''.join((
                            opInfo,  # operation
                            SET_MINUTES,  # CMD
                            LCX(value)  # NAME
                    )),
                    verbosity=self._verbosity,
                    sync_mode=self._sync_mode
            )
            self._physical_ev3._introspection["sleep"] = value

    @property
    def sync_mode(self) -> str:
        """
        sync mode (standard, asynchronous, synchronous)

        STD
          use DIRECT_COMMAND_REPLY only if global_mem > 0,
          wait for reply if there is one.
        ASYNC
          use DIRECT_COMMAND_REPLY only if global_mem > 0,
          never wait for reply (it's the task of the calling program).
        SYNC
          always use DIRECT_COMMAND_REPLY and wait for reply.

        The idea is

          ASYNC - if there is a reply, it must explicitly be asked for.
          Control directly comes back.

          SYNC - EV3 device is blocked and control comes back,
          when direct command is finished, which means
          synchronicity of program and EV3 device.

          STD - direct commands with no reply are handled like ASYNC,
          direct commands with reply are handled like SYNC.
        """

        return self._sync_mode

    @sync_mode.setter
    def sync_mode(self, value: str):
        assert isinstance(value, str), \
            "sync_mode needs to be of type str"
        assert value in (STD, SYNC, ASYNC), \
            "value of sync_mode: " + value + " is invalid"
        self._sync_mode = value

    @property
    def system(self) -> str:
        """
        system versions and build numbers (as named tuple System)
        
          os_version
            operating system version
          os_build
            operating system build number
          fw_version
            firmware version
          fw_build
            firmware build number
          hw_version
            hardware version
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return System(
                self._physical_ev3._introspection["os_vers"],
                self._physical_ev3._introspection["os_build"],
                self._physical_ev3._introspection["fw_vers"],
                self._physical_ev3._introspection["fw_build"],
                self._physical_ev3._introspection["hw_vers"]
        )

    @property
    def verbosity(self) -> int:
        """
        level of verbosity (prints on stdout), values 0, 1 or 2
        """
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int):
        assert isinstance(value, int), \
            "verbosity needs to be of type int"
        assert value >= 0 and value <= 2, \
            "allowed verbosity values are: 0, 1 or 2"
        self._verbosity = int(value)

    @property
    def volume(self) -> int:
        """
        sound volume [%], values from 0 to 100
        """
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        return self._physical_ev3._introspection["volume"]

    @volume.setter
    def volume(self, value: int):
        assert isinstance(value, int), "volume needs to be of type int"
        assert 0 <= value <= 100, "volume must be between 0 and 100"
        if self._physical_ev3._introspection is None:
            self._physical_ev3.introspection(self._verbosity)
        if value != self._physical_ev3._introspection["volume"]:
            self._physical_ev3.send_direct_cmd(
                    b''.join((
                            opInfo,  # operation
                            SET_VOLUME,  # CMD
                            LCX(value)  # NAME
                    )),
                    verbosity=self._verbosity,
                    sync_mode=self._sync_mode
            )
            self._physical_ev3._introspection["volume"] = value

    def send_direct_cmd(
        self,
        ops: bytes,
        *,
        local_mem: int = 0,
        global_mem: int = 0,
        sync_mode: str = None,
        verbosity: int = None
    ) -> bytes:
        """
        Send a direct command to the LEGO EV3

        Mandatory positional arguments

          ops
            holds netto data only (operations), these fields are added:

              length: 2 bytes, little endian

              msg_cnt: 2 bytes, little endian

              type: 1 byte, DIRECT_COMMAND_REPLY or DIRECT_COMMAND_NO_REPLY

              header: 2 bytes, holds sizes of local and global memory

        Optional keyword only arguments

          local_mem
            size of the local memory
          global_mem
            size of the global memory
          sync_mode
            synchronization mode (STD, SYNC, ASYNC)
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).

        Returns

          STD (sync_mode)
            if global_mem > 0 then reply else message counter
          ASYNC (sync_mode)
            message counter
          SYNC (sync_mode)
            reply of the LEGO EV3
        """
        assert isinstance(ops, bytes), \
            "ops needs to be of type bytes"
        assert len(ops) > 0, \
            "ops must not be empty"
        assert isinstance(local_mem, int), \
            "local_mem needs to be an integer"
        assert local_mem >= 0, \
            "local_mem needs to be positive"
        assert local_mem <= 63, \
            "local_mem has a maximum of 63"
        assert isinstance(global_mem, int), \
            "global_mem needs to be an integer"
        assert global_mem >= 0, \
            "global_mem needs to be positive"
        assert local_mem <= 1019, \
            "global_mem has a maximum of 1019"
        assert sync_mode is None or isinstance(sync_mode, str), \
            "sync_mode needs to be of type str"
        assert sync_mode is None or sync_mode in (STD, SYNC, ASYNC), \
            "value of sync_mode: " + sync_mode + " is invalid"
        assert verbosity is None or isinstance(verbosity, int), \
            "verbosity needs to be of type int"
        assert verbosity is None or verbosity >= 0 and verbosity <= 2, \
            "allowed verbosity values are: 0, 1 or 2"
            
        if sync_mode is None:
            sync_mode = self._sync_mode
        if verbosity is None:
            verbosity = self._verbosity
        return self._physical_ev3.send_direct_cmd(
                ops,
                local_mem=local_mem,
                global_mem=global_mem,
                sync_mode=sync_mode,
                verbosity=verbosity                
        )

    def wait_for_reply(
        self,
        msg_cnt: bytes,
        *,
        verbosity: int = None
    ) -> bytes:
        """
        Ask the LEGO EV3 for a reply and wait until it is received

        Mandatory positional arguments

          msg_cnt
            is the message counter of the corresponding send_direct_cmd

        Optional keyword only arguments

          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).

        Returns

          reply to the direct command (without len, msg_cnt and return status)
        """
        assert isinstance(msg_cnt, bytes), \
            "msg_cnt needs to be of type bytes"
        assert len(msg_cnt) == 2, \
            "msg_cnt must be 2 bytes long"
        assert verbosity is None or isinstance(verbosity, int), \
            "verbosity needs to be of type int"
        assert verbosity is None or verbosity >= 0 and verbosity <= 2, \
            "allowed verbosity values are: 0, 1 or 2"

        if verbosity is None:
            verbosity = self._verbosity
        return self._physical_ev3.wait_for_reply(
                msg_cnt,
                verbosity=verbosity
        )

    def send_system_cmd(
        self,
        cmd: bytes,
        *,
        reply: bool = True,
        verbosity: int = None
    ) -> bytes:
        """
        Send a system command to the LEGO EV3

        Mandatory positional arguments

          cmd
            holds netto data only (cmd and arguments), these fields are added:

              length: 2 bytes, little endian

              msg_cnt: 2 bytes, little endian

              type: 1 byte, SYSTEM_COMMAND_REPLY or SYSTEM_COMMAND_NO_REPLY

        Optional keyword only arguments

          reply
            flag if with reply
          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).

        Returns

          reply (in case of SYSTEM_COMMAND_NO_REPLY: msg_cnt)
        """
        assert isinstance(cmd, bytes), \
            "cmd needs to be of type bytes"
        assert isinstance(reply, bool), \
            "reply needs to be of type bool"
        assert verbosity is None or isinstance(verbosity, int), \
            "verbosity needs to be of type int"
        assert verbosity is None or verbosity >= 0 and verbosity <= 2, \
            "allowed verbosity values are: 0, 1 or 2"

        if verbosity is None:
            verbosity = self._verbosity
        return self._physical_ev3.send_system_cmd(
                cmd,
                reply=reply,
                verbosity=verbosity
        )

    def _wait_for_system_reply(
            self,
            msg_cnt: bytes,
            *,
            verbosity: int = None
    ) -> bytes:
        """
        Ask the LEGO EV3 for a system command reply and wait until received

        Mandatory positional arguments

          msg_cnt
            is the message counter of the corresponding send_system_cmd

        Optional keyword only arguments

          verbosity
            level (0, 1, 2) of verbosity (prints on stdout).

        Returns

          reply to the system command
        """
        assert isinstance(msg_cnt, bytes), \
            "msg_cnt needs to be of type bytes"
        assert len(msg_cnt) == 2, \
            "msg_cnt must be 2 bytes long"
        assert verbosity is None or isinstance(verbosity, int), \
            "verbosity needs to be of type int"
        assert verbosity is None or verbosity >= 0 and verbosity <= 2, \
            "allowed verbosity values are: 0, 1 or 2"
            
        if verbosity is None:
            verbosity = self._verbosity
        return self._physical_ev3._wait_for_system_reply(
                msg_cnt,
                verbosity=verbosity
        )
