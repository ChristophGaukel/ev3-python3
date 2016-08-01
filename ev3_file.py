#!/usr/bin/env python3

"""
access on EV3's filesystem
"""

# Copyright (C) 2016 Christoph Gaukel <christoph.gaukel@gmx.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import ev3, datetime, struct

class SysCmdError(Exception):
    pass

class FileSystem(ev3.EV3):
    """
    Works with EV3's filesystem
    """
    def _complete_system_cmd(self, cmd:bytes, reply:bool) -> bytes:
        """
        complete system command with heading standard parts
        """
        if reply:
            cmd_type = _SYSTEM_COMMAND_REPLY
        else:
            cmd_type = _SYSTEM_COMMAND_NO_REPLY
        self._lock.acquire()
        msg_cnt = self._msg_cnt.next()
        self._lock.release()
        return b''.join([
            struct.pack('<hh', len(cmd) + 3, msg_cnt),
            cmd_type,
            cmd
        ])

    def send_system_cmd(self, cmd: bytes, reply: bool=True) -> bytes:
        """
        Send a system command to the LEGO EV3

        Arguments:
        cmd: holds netto data only (cmd and arguments), the following fields are added:
          length: 2 bytes, little endian
          counter: 2 bytes, little endian
          type: 1 byte, SYSTEM_COMMAND_REPLY or SYSTEM_COMMAND_NO_REPLY

        Keywor Arguments:
        reply: flag if with reply
        
        Returns: 
          reply (in case of SYSTEM_COMMAND_NO_REPLY: counter)
        """
        cmd = self._complete_system_cmd(cmd, reply)
        if self._verbosity >= 1:
            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now + \
                  ' Sent 0x|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[5:]) + '|' \
            )
        if self._protocol in [ev3.BLUETOOTH, ev3.WIFI]:
            self._socket.send(cmd)
        elif self._protocol is ev3.USB:
            self._device.write(ev3._EP_OUT, cmd, 100)
        else:
            raise RuntimeError('No EV3 connected')
        counter = cmd[2:4]
        if not reply:
            return counter
        else:
            reply = self._wait_for_system_reply(counter)
            return reply

    def _wait_for_system_reply(self, counter: bytes) -> bytes:
        """
        Ask the LEGO EV3 for a reply and wait until received

        Arguments:
        counter: is the message counter of the corresponding send_direct_cmd
        
        Returns:
        reply to the system command
        """
        self._lock.acquire()
        reply = self._foreign.get(counter)
        if reply:
            if reply[4:5] != _SYSTEM_REPLY:
                raise SysCmdError("error: {:02X}".format(reply[6]))
            self._lock.release()
            return reply
        while True:
            if self._protocol in [ev3.BLUETOOTH, ev3.WIFI]:
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(ev3._EP_IN, 1024, 0))
            len_data = struct.unpack('<H', reply[:2])[0] + 2
            reply_counter = reply[2:4]
            if self._verbosity >= 1:
                now = datetime.datetime.now().strftime('%H:%M:%S.%f')
                print(now + \
                      ' Recv 0x|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[0:2]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[2:4]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[4:5]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[5:6]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[6:7]) + \
                      '|', end='')
                if len_data > 7:
                    dat = ':'.join('{:02X}'.format(byte) for byte in reply[7:len_data])
                    print(dat + '|')
                else:
                    print()
            if counter != reply_counter:
                self._foreign.put(reply_counter, reply[:len_data])
            else:
                if reply[4:5] != _SYSTEM_REPLY:
                    raise SysCmdError("system command replied error: {:02X}".format(reply[6]))
                self._lock.release()
                return reply[:len_data]

    def write_file(self, path: str, data: bytes) -> None:
        """
        Write a file to the EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/") of the file
        data: data to write into the file
        """
        size = len(data)
        cmd = b''.join([
            BEGIN_DOWNLOAD,
            struct.pack('<I', size),      # SIZE
            str.encode(path) + b'\x00'    # NAME
        ])
        reply = self.send_system_cmd(cmd)
        handle = struct.unpack('B', reply[7:8])[0]
        rest = size
        while rest > 0:
            part_size = min(1017, rest)
            pos = size - rest
            fmt = 'B' + str(part_size) + 's'
            cmd = b''.join([
                CONTINUE_DOWNLOAD,
                struct.pack(fmt, handle, data[pos:pos+part_size]) # HANDLE, DATA
            ])
            self.send_system_cmd(cmd)
            rest -= part_size

    def read_file(self, path: str) -> bytes:
        """
        Read one of EV3's files

        Attributes:
        path: absolute or relative path to file (f.i. "/bin/sh")
        """
        cmd = b''.join([
            BEGIN_UPLOAD,
            struct.pack('<H', 1012),      # SIZE
            str.encode(path) + b'\x00'    # NAME
        ])
        reply = self.send_system_cmd(cmd)
        (size, handle) = struct.unpack('<IB', reply[7:12])
        part_size = min(1012, size)
        if part_size > 0:
            fmt = str(part_size) + 's'
            data = struct.unpack(fmt, reply[12:])[0]
        else:
            data = b''
        rest = size - part_size
        while rest > 0:
            part_size = min(1016, rest)
            cmd = b''.join([
                CONTINUE_UPLOAD,
                struct.pack('<BH', handle, part_size) # HANDLE, SIZE
            ])
            reply = self.send_system_cmd(cmd)
            fmt = 'B' + str(part_size) + 's'
            (handle, part) = struct.unpack(fmt, reply[7:])
            data += part
            rest -= part_size
            if rest <= 0 and reply[6:7] != _SYSTEM_END_OF_FILE:
                raise SysCmdError("end of file not reached")
        return data       

    def del_file(self, path: str) -> None:
        """
        Delete a file from the EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/") of the file
        secure: flag, if the file may be located outside of directory "/home/root/lms2012/"
        """
        cmd = b''.join([
            DELETE_FILE,
            str.encode(path) + b'\x00'    # NAME
        ])
        self.send_system_cmd(cmd)

    def copy_file(self, path_source: str, path_dest: str) -> None:
        """
        Copies a file in the EV3's file system from
        its old location to a new one
        (no error if the file doesn't exist)

        Attributes:
        path_source: absolute or relative path (from "/home/root/lms2012/sys/")
                     of the existing file
        path_dest: absolute or relative path of the new file
        """
        ops = b''.join([
            ev3.opFile,
            ev3.MOVE,
            ev3.LCS(path_source), # SOURCE
            ev3.LCS(path_dest)    # DESTINATION
        ])
        self.send_direct_cmd(ops, global_mem=1)

    def list_dir(self, path: str) -> dict:
        """
        Read one of EV3's directories

        Attributes:
        path: absolute or relative path to the directory (f.i. "/bin")

        Returns:
        dict, that holds subfolders and files.
          folders as an array of strings (names)
          files as an array of dictionaries
          {'folders': ['subfolder1', 'subfolder2', ...]
           'files': [{'size': 4202,
                      'name': 'usb-devices',
                      'md5': '5E78E1B8C0E1E8CB73FDED5DE384C000'}, ...]}
        """
        cmd = b''.join([
            LIST_FILES,
            struct.pack('<H', 1012),      # SIZE
            str.encode(path) + b'\x00'    # NAME
        ])
        reply = self.send_system_cmd(cmd)
        (size, handle) = struct.unpack('<IB', reply[7:12])
        part_size = min(1012, size)
        if part_size > 0:
            fmt = str(part_size) + 's'
            data = struct.unpack(fmt, reply[12:])[0]
        else:
            data = b''
        rest = size - part_size
        while rest > 0:
            part_size = min(1016, rest)
            cmd = b''.join([
                CONTINUE_LIST_FILES,
                struct.pack('<BH', handle, part_size) # HANDLE, SIZE
            ])
            reply = self.send_system_cmd(cmd)
            fmt = 'B' + str(part_size) + 's'
            (handle, part) = struct.unpack(fmt, reply[7:])
            data += part
            rest -= part_size
            if rest <= 0 and reply[6:7] != _SYSTEM_END_OF_FILE:
                raise SysCmdError("end of file not reached")
        folders = []
        files = []
        for line in data.split(sep=b'\x0A'):
            if line == b'':
                pass
            elif line.endswith(b'\x2F'):
                folders.append(line.rstrip(b'\x2F').decode("utf8"))
            else:
                (md5, size_hex, name) = line.split(None, 2)
                size = int(size_hex, 16)
                files.append({
                    'md5': md5.decode("utf8"),
                    'size': size,
                    'name': name.decode("utf8")
                })
        return {'files': files, 'folders': folders}

    def create_dir(self, path: str) -> None:
        """
        Create a directory on EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/")
        """
        cmd = b''.join([
            CREATE_DIR,
            str.encode(path) + b'\x00'    # NAME
        ])
        self.send_system_cmd(cmd)

    def del_dir(self, path: str, secure: bool=True) -> None:
        """
        Delete a directory on EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/")
        secure: flag, if the directory may be not empty
        """
        if secure:
            self.del_file(path)
        else:
            if path.endswith("/"):
                path = path[:-1]
            parent_path = path.rsplit("/", 1)[0] + "/"
            folder = path.rsplit("/", 1)[1]
            ops = b''.join([
                ev3.opFile,
                ev3.GET_FOLDERS,
                ev3.LCS(parent_path),
                ev3.GVX(0)
            ])
            reply = self.send_direct_cmd(ops, global_mem=1)
            num = struct.unpack('B', reply[5:])[0]
            found = False
            for i in range(num):
                ops = b''.join([
                    ev3.opFile,
                    ev3.GET_SUBFOLDER_NAME,
                    ev3.LCS(parent_path),
                    ev3.LCX(i + 1),         # ITEM
                    ev3.LCX(64),            # LENGTH
                    ev3.GVX(0)              # NAME
                ])
                reply = self.send_direct_cmd(ops, global_mem=64)
                subdir = struct.unpack('64s', reply[5:])[0]
                subdir = subdir.split(b'\x00')[0]
                subdir = subdir.decode("utf8")
                if subdir == folder:
                    found = True
                    ops = b''.join([
                        ev3.opFile,
                        ev3.DEL_SUBFOLDER,
                        ev3.LCS(parent_path), # NAME
                        ev3.LCX(i + 1)        # ITEM
                    ])
                    self.send_direct_cmd(ops)
                    break
            if not found:
                raise ev3.DirCmdError("Folder " + path + " doesn't exist")
                    

_SYSTEM_COMMAND_REPLY     = b'\x01'
_SYSTEM_COMMAND_NO_REPLY  = b'\x81'

_SYSTEM_REPLY             = b'\x03'
_SYSTEM_REPLY_ERROR       = b'\x05'

_SYSTEM_REPLY_OK          = b'\x00'
_SYSTEM_UNKNOWN_HANDLE    = b'\x01'
_SYSTEM_HANDLE_NOT_READY  = b'\x02'
_SYSTEM_CORRUPT_FILE      = b'\x03'
_SYSTEM_NO_HANDLES_AVAILABLE = b'\x04'
_SYSTEM_NO_PERMISSION     = b'\x05'
_SYSTEM_ILLEGAL_PATH      = b'\x06'
_SYSTEM_FILE_EXITS        = b'\x07'
_SYSTEM_END_OF_FILE       = b'\x08'
_SYSTEM_SIZE_ERROR        = b'\x09'
_SYSTEM_UNKNOWN_ERROR     = b'\x0A'
_SYSTEM_ILLEGAL_FILENAME  = b'\x0B'
_SYSTEM_ILLEGAL_CONNECTION= b'\x0C'

BEGIN_DOWNLOAD            = b'\x92'
CONTINUE_DOWNLOAD         = b'\x93'
BEGIN_UPLOAD              = b'\x94'
CONTINUE_UPLOAD           = b'\x95'
BEGIN_GETFILE             = b'\x96'
CONTINUE_GETFILE          = b'\x97'
CLOSE_FILEHANDLE          = b'\x98'
LIST_FILES                = b'\x99'
CONTINUE_LIST_FILES       = b'\x9A'
CREATE_DIR                = b'\x9B'
DELETE_FILE               = b'\x9C'
LIST_OPEN_HANDLES         = b'\x9D'
WRITEMAILBOX              = b'\x9E'
BLUETOOTHPIN              = b'\x9F'
ENTERFWUPDATE             = b'\xA0'
