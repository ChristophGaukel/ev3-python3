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

import struct
import time
import ev3

class FileSystem(ev3.EV3):
    """
    Works with EV3's filesystem
    """
    def write_file(self, path: str, data: bytes) -> None:
        """
        Write data into a file of the EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/") of the file
        data: data to write into the file
        """
        size = len(data)
        cmd = b''.join([
            ev3.BEGIN_DOWNLOAD,
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
                ev3.CONTINUE_DOWNLOAD,
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
            ev3.BEGIN_UPLOAD,
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
                ev3.CONTINUE_UPLOAD,
                struct.pack('<BH', handle, part_size) # HANDLE, SIZE
            ])
            reply = self.send_system_cmd(cmd)
            fmt = 'B' + str(part_size) + 's'
            (handle, part) = struct.unpack(fmt, reply[7:])
            data += part
            rest -= part_size
            if rest <= 0 and reply[6:7] != ev3.SYSTEM_END_OF_FILE:
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
            ev3.DELETE_FILE,
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

    # pylint: disable=too-many-locals
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
            ev3.LIST_FILES,
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
                ev3.CONTINUE_LIST_FILES,
                struct.pack('<BH', handle, part_size) # HANDLE, SIZE
            ])
            reply = self.send_system_cmd(cmd)
            fmt = 'B' + str(part_size) + 's'
            (handle, part) = struct.unpack(fmt, reply[7:])
            data += part
            rest -= part_size
            if rest <= 0 and reply[6:7] != ev3.SYSTEM_END_OF_FILE:
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
    # pylint: enable=too-many-locals

    def create_dir(self, path: str) -> None:
        """
        Create a directory on EV3's file system

        Attributes:
        path: absolute or relative path (from "/home/root/lms2012/sys/")
        """
        cmd = b''.join([
            ev3.CREATE_DIR,
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
