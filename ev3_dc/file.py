"""
LEGO Mindstorms EV3 direct commands - filesystem
"""

import os
import struct
import hashlib
from ev3_dc import EV3
from .functions import (
    LCS,
    LCX,
    GVX
)
from .constants import (
    opFile,
    MOVE,
    BEGIN_DOWNLOAD,
    CONTINUE_DOWNLOAD,
    BEGIN_UPLOAD,
    CONTINUE_UPLOAD,
    SYSTEM_REPLY_OK,
    SYSTEM_END_OF_FILE,
    LIST_FILES,
    CONTINUE_LIST_FILES,
    DELETE_FILE,
    CREATE_DIR,
    GET_FOLDERS,
    GET_SUBFOLDER_NAME,
    DEL_SUBFOLDER,
    SYNC
)
from .exceptions import SysCmdError, DirCmdError


class FileSystem(EV3):
    """
    Access to EV3's filesystem
    """

    def __str__(self):
        '''
        description of the object in a str context
        '''
        return ' '.join((
                'FileSystem',
                f'of {super().__str__()}'
        ))

    def write_file(self, path: str, data: bytes, *, check: bool = True) -> None:
        """
        Create a file in EV3's file system and write data into it

        Mandatory positional arguments

          path
            absolute or relative path (from "/home/root/lms2012/sys/")
            of the file
          data
            data to write into the file

        Optional keyword only arguments

          check
            flag for check if file already exists with identical MD5 checksum
        """
        assert isinstance(path, str), \
            'path needs to be of type str'
        assert isinstance(data, bytes), \
            "data needs to be of type bytes"
        assert isinstance(check, bool), \
            'check needs to be of type bool'

        size = len(data)

        if check:
            # check if identic file already exists
            dir_dest = '/'.join(path.split('/')[:-1])
            file_dest = path.split('/')[-1]
            try:
                folders, files = self.list_dir(dir_dest)
            except SysCmdError:
                raise SysCmdError('directory ' + path_dest_dir + ' does not exist')

            data_md5 = None
            for curr_name, curr_size, curr_md5 in files:
                if curr_size == size:
                    if data_md5 is None:
                        data_md5 = hashlib.md5(data).hexdigest().upper()
                    if data_md5 == curr_md5:
                        # identic size and md5 hash
                        return

        cmd = b''.join((
            BEGIN_DOWNLOAD,
            struct.pack('<I', size),      # SIZE
            str.encode(path) + b'\x00'    # NAME
        ))
        reply = self.send_system_cmd(cmd)
        rc, handle = struct.unpack('sB', reply)
        rest = size
        if rc != SYSTEM_REPLY_OK:
            raise SysCmdError(
                "error " +
                '{:02X}'.format(rc) +
                " when writing file " +
                path
            )
        while rest > 0:
            part_size = min(1017, rest)
            pos = size - rest
            fmt = 'B' + str(part_size) + 's'
            cmd = b''.join((
                CONTINUE_DOWNLOAD,
                struct.pack(
                    fmt,
                    handle,
                    data[pos:pos+part_size]
                )
            ))
            reply = self.send_system_cmd(cmd)
            rc, handle = struct.unpack('sB', reply)
            rest -= part_size
            if rest > 0 and rc != SYSTEM_REPLY_OK:
                raise SysCmdError(
                    "error " +
                    '{:02X}'.format(rc) +
                    " when writing file " +
                    path
                )
            if rest <= 0 and rc != SYSTEM_END_OF_FILE:
                raise SysCmdError(
                    "end of file " +
                    path +
                    " not reached"
                )

    def load_file(self, path_source: str, path_dest: str, *, check: bool = True) -> None:
        """
        Copy a local file to EV3's file system


        Mandatory positional arguments

          path_source
            absolute or relative path of the existing file
            in the local file system
          path_dest
            absolute or relative path (from "/home/root/lms2012/sys/")
            in EV3's file system

        Optional keyword only aguments

          check
            flag for check if file already exists with identical MD5 checksum
        """
        assert isinstance(path_source, str), \
            'path_source needs to be of type str'
        assert isinstance(path_dest, str), \
            'path_dest needs to be of type str'
        assert isinstance(check, bool), \
            'check needs to be of type bool'

        # file size
        size = os.path.getsize(path_source)

        if check:
            # check if identic file already exists
            dir_dest = '/'.join(path_dest.split('/')[:-1])
            file_dest = path_dest.split('/')[-1]
            try:
                folders, files = self.list_dir(dir_dest)
            except SysCmdError:
                raise SysCmdError('directory ' + path_dest_dir + ' does not exist')
            for curr_name, curr_size, curr_md5 in files:
                if curr_name == file_dest:
                    if curr_size == size:
                        # identic name and size
                        md5_hash = hashlib.md5()
                        with open(path_source, 'rb') as f:
                            chunk = f.read(4096)
                            while chunk:
                                md5_hash.update(chunk)
                                chunk = f.read(4096)
                        if md5_hash.hexdigest().upper() == curr_md5:
                            # identic name, size and md5 hash
                            return
                    break

        # get file handle
        reply = self.send_system_cmd(
            b''.join((
                BEGIN_DOWNLOAD,
                struct.pack('<I', size),      # SIZE
                str.encode(path_dest) + b'\x00'    # NAME
            ))
        )
        rc, handle = struct.unpack('sB', reply)
        if rc != SYSTEM_REPLY_OK:
            raise SysCmdError(
                "error " +
                '{:02X}'.format(rc) +
                " when writing file " +
                path
            )

        # open file and copy in parts of 1017 bytes
        with open(path_source, 'rb') as f:
            while True:
                part = f.read(1017)
                if not part:
                    raise SysCmdError(
                        "reached end of file " +
                        path_source
                    )
                    break
                fmt = 'B' + str(len(part)) + 's'
                reply = self.send_system_cmd(
                    b''.join((
                        CONTINUE_DOWNLOAD,
                        struct.pack(
                            fmt,
                            handle,
                            part
                        )
                    ))
                )
                rc, handle = struct.unpack('sB', reply)

                # all done?
                if rc == SYSTEM_END_OF_FILE:
                    break
                elif rc != SYSTEM_REPLY_OK:
                    raise SysCmdError(
                        "error " +
                        '{:02X}'.format(rc) +
                        " when writing file " +
                        path_dest
                    )

    def read_file(self, path: str) -> bytes:
        """
        Read one of EV3's files

        Mandatory positional arguments

          path
            absolute or relative path to file (f.i. "/bin/sh")
        """
        assert isinstance(path, str), \
            'path needs to be of type str'

        cmd = b''.join((
            BEGIN_UPLOAD,
            struct.pack('<H', 1012),      # SIZE
            str.encode(path) + b'\x00'    # NAME
        ))
        reply = self.send_system_cmd(cmd)
        size, handle = struct.unpack(
            '<IB',
            reply[1:6]
        )
        part_size = min(1012, size)
        if part_size > 0:
            fmt = str(part_size) + 's'
            data = struct.unpack(
                fmt,
                reply[6:]
            )[0]
        else:
            data = b''
        rest = size - part_size
        while rest > 0:
            part_size = min(1016, rest)
            cmd = b''.join((
                CONTINUE_UPLOAD,
                struct.pack('<BH', handle, part_size)  # HANDLE, SIZE
            ))
            rc, handle, part = struct.unpack(
                'sB' + str(part_size) + 's',
                self.send_system_cmd(cmd)
            )
            data += part
            rest -= part_size
            if rest > 0 and rc != SYSTEM_REPLY_OK:
                raise SysCmdError(
                    "error " +
                    '{:02X}'.format(rc) +
                    " when reading file " +
                    path
                )
            if rest <= 0 and rc != SYSTEM_END_OF_FILE:
                raise SysCmdError(
                    "end of file " +
                    path +
                    " not reached"
                )
        return data

    def del_file(self, path: str) -> None:
        """
        Delete a file in EV3's file system

        Mandatory positional arguments

          path
            absolute or relative path (from "/home/root/lms2012/sys/")
            of the file
        """
        assert isinstance(path, str), \
            'path needs to be of type str'

        cmd = b''.join((
            DELETE_FILE,
            str.encode(path) + b'\x00'    # NAME
        ))
        self.send_system_cmd(cmd)

    def copy_file(self, path_source: str, path_dest: str) -> None:
        """
        Copies a file in EV3's file system from
        its old location to a new one
        (no error if the file doesn't exist)

        Mandatory positional arguments

          path_source
            absolute or relative path (from "/home/root/lms2012/sys/")
            of the existing file
          path_dest
            absolute or relative path of the new file
        """
        assert isinstance(path_source, str), \
            'path_source needs to be of type str'
        assert isinstance(path_dest, str), \
            'path_dest needs to be of type str'

        ops = b''.join((
            opFile,
            MOVE,
            LCS(path_source),  # SOURCE
            LCS(path_dest)  # DESTINATION
        ))
        self.send_direct_cmd(
            ops,
            sync_mode=SYNC
        )

    def list_dir(self, path: str) -> dict:
        """
        Read one EV3 directory's content

        Mandatory positional arguments

          path
            absolute or relative path (from "/home/root/lms2012/sys/")
            to the directory (f.i. "/bin")

        Returns

          subfolders
            tuple of strings (names)
          files
            tuple of tuples (name:str, size:int, md5:str)
        """
        assert isinstance(path, str), \
            'path needs to be of type str'

        cmd = b''.join((
            LIST_FILES,
            struct.pack('<H', 1012),  # SIZE
            str.encode(path) + b'\x00'  # NAME
        ))
        reply = self.send_system_cmd(cmd)
        size, handle = struct.unpack('<IB', reply[1:6])
        part_size = min(1012, size)
        if part_size > 0:
            fmt = str(part_size) + 's'
            data = struct.unpack(fmt, reply[6:])[0]
        else:
            data = b''
        rest = size - part_size
        while rest > 0:
            part_size = min(1016, rest)
            cmd = b''.join((
                CONTINUE_LIST_FILES,
                struct.pack('<BH', handle, part_size)  # HANDLE, SIZE
            ))
            rc, handle, part = struct.unpack(
                'sB' + str(part_size) + 's',
                self.send_system_cmd(cmd)
            )
            data += part
            rest -= part_size
            if rest > 0 and rc != SYSTEM_REPLY_OK:
                raise SysCmdError(
                    "error " +
                    '{:02X}'.format(rc) +
                    " when reading folder " +
                    path
                )
            if rest <= 0 and rc != SYSTEM_END_OF_FILE:
                raise SysCmdError(
                    "end of folder-data " +
                    path +
                    " not reached"
                )
        folders = []
        files = []
        for line in data.split(sep=b'\x0A'):
            if line == b'':
                pass
            elif line.endswith(b'\x2F'):
                folders.append(line.rstrip(b'\x2F').decode("utf8"))
            else:
                md5, size_hex, name = line.split(None, 2)
                size = int(size_hex, 16)
                files.append((
                    name.decode("utf8"),
                    size,
                    md5.decode("utf8")
                ))
        return tuple(folders), tuple(files)

    def create_dir(self, path: str) -> None:
        """
        Create a directory in EV3's file system

        Mandatory positional arguments

          path
            absolute or relative path (from "/home/root/lms2012/sys/")
        """
        assert isinstance(path, str), \
            'path needs to be of type str'

        cmd = b''.join((
            CREATE_DIR,
            str.encode(path) + b'\x00'  # NAME
        ))
        self.send_system_cmd(cmd)

    def del_dir(self, path: str, *, secure: bool = True) -> None:
        """
        Delete a directory in EV3's file system

        Mandatory positional arguments

          path
            absolute or relative path (from "/home/root/lms2012/sys/")

        Optional keyword only arguments

          secure
            flag, if the directory must be empty
        """
        assert isinstance(path, str), \
            'path needs to be of type str'
        assert isinstance(secure, bool), \
            "secure needs to be of type bool"

        if secure:
            self.del_file(path)
        else:
            if path.endswith("/"):
                path = path[:-1]
            parent_path = path.rsplit("/", 1)[0] + "/"
            folder = path.rsplit("/", 1)[1]
            ops = b''.join((
                opFile,
                GET_FOLDERS,
                LCS(parent_path),
                GVX(0)
            ))
            num = struct.unpack(
                'B',
                self.send_direct_cmd(
                    ops,
                    global_mem=1,
                    sync_mode=SYNC
                )
            )[0]
            found = False
            for i in range(num):
                ops = b''.join((
                    opFile,
                    GET_SUBFOLDER_NAME,
                    LCS(parent_path),
                    LCX(i + 1),  # ITEM
                    LCX(64),  # LENGTH
                    GVX(0)  # NAME
                ))
                subdir = struct.unpack(
                    '64s',
                    self.send_direct_cmd(
                        ops,
                        global_mem=64,
                        sync_mode=SYNC
                    )
                )[0].split(b'\x00')[0].decode("utf8")
                if subdir == folder:
                    found = True
                    ops = b''.join((
                        opFile,
                        DEL_SUBFOLDER,
                        LCS(parent_path),  # NAME
                        LCX(i + 1)  # ITEM
                    ))
                    self.send_direct_cmd(
                        ops,
                        sync_mode=SYNC
                    )
                    break
            if not found:
                raise DirCmdError("Folder " + path + " doesn't exist")
