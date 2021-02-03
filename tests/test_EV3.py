'''pytest ev3_dc.EV3'''

import ev3_dc as ev3
import struct
import pytest
import re

my_ev3 = ev3.EV3(
    protocol=ev3.WIFI,
    host='00:16:53:42:2B:99',
    sync_mode=ev3.SYNC,
    verbosity=1
)


def test_opNop(capsys):
    '''the art of doing nothing'''

    # SYNC -> with reply, without output
    ops = ev3.opNop
    reply = ':'.join(
        '{:02X}'.format(
            byte
        ) for byte in my_ev3.send_direct_cmd(
            ops,
            sync_mode=ev3.SYNC,
            verbosity=0
        )
    )
    assert reply == ''
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''

    # SYNC -> with reply, with output
    my_ev3.sync_mode = ev3.SYNC
    my_ev3.verbosity = 1
    reply = ':'.join(
        '{:02X}'.format(
            byte
        ) for byte in my_ev3.send_direct_cmd(ops)
    )
    assert reply == ''
    captured = capsys.readouterr()
    assert captured.err == ''
    assert re.sub(
        r'\d\d:\d\d:\d\d\.\d{6}',
        'xx:xx:xx.xxxxxx',
        captured.out
    ) == (
        'xx:xx:xx.xxxxxx Sent 0x|06:00|2B:00|00|00:00|01|' + '\n' +
        'xx:xx:xx.xxxxxx Recv 0x|03:00|2B:00|02|' + '\n'
    )

    # ASYNC -> no reply, with output
    my_ev3.sync_mode = ev3.ASYNC
    reply = ':'.join(
        '{:02X}'.format(
            byte
        ) for byte in my_ev3.send_direct_cmd(ops)
    )
    assert reply == '2C:00'
    captured = capsys.readouterr()
    assert captured.err == ''
    assert re.sub(
        r'\d\d:\d\d:\d\d\.\d{6}',
        'xx:xx:xx.xxxxxx',
        captured.out
    ) == (
        'xx:xx:xx.xxxxxx Sent 0x|06:00|2C:00|80|00:00|01|' + '\n'
    )

    # STD without global_mem -> no reply, with output
    my_ev3.sync_mode = ev3.STD
    reply = ':'.join(
        '{:02X}'.format(
            byte
        ) for byte in my_ev3.send_direct_cmd(ops)
    )
    assert reply == '2D:00'
    captured = capsys.readouterr()
    assert captured.err == ''
    assert re.sub(
        r'\d\d:\d\d:\d\d\.\d{6}',
        'xx:xx:xx.xxxxxx',
        captured.out
    ) == (
        'xx:xx:xx.xxxxxx Sent 0x|06:00|2D:00|80|00:00|01|' + '\n'
    )

    # STD with global_mem -> reply, without output
    my_ev3.sync_mode = ev3.STD
    reply = ':'.join(
        '{:02X}'.format(
            byte
        ) for byte in my_ev3.send_direct_cmd(
            ops,
            global_mem=1,
            verbosity=0
        )
    )
    # assert reply.startswith('04:00:2E:00:02:')
    assert len(reply) == 2
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''

    # ASYNC with globla_mem -> reply, without output
    my_ev3.sync_mode = ev3.ASYNC
    my_ev3.verbosity = 0
    msg_cnt_1 = my_ev3.send_direct_cmd(
        ops,
        global_mem=1
    )
    assert ':'.join('{:02X}'.format(byte) for byte in msg_cnt_1) == '2F:00'
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''

    msg_cnt_2 = my_ev3.send_direct_cmd(
        ops,
        global_mem=2
    )
    assert ':'.join('{:02X}'.format(byte) for byte in msg_cnt_2) == '30:00'
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''

    reply_2 = my_ev3.wait_for_reply(msg_cnt_2)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''
    reply_2_str = ':'.join('{:02X}'.format(byte) for byte in reply_2)
    assert len(reply_2_str) == 5

    # msg_1 must be in the reply buffer
    assert msg_cnt_1 in my_ev3._physical_ev3._reply_buffer
    assert msg_cnt_1 == my_ev3._physical_ev3._reply_buffer[msg_cnt_1][2:4]

    my_ev3.verbosity = 1
    reply_1 = my_ev3.wait_for_reply(msg_cnt_1, verbosity=0)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''
    reply_1_str = ':'.join('{:02X}'.format(byte) for byte in reply_1)
    assert len(reply_1_str) == 2


def test_opError():
    '''direct command error'''
    my_ev3.sync_mode = ev3.SYNC
    my_ev3.verbosity = 0
    ops = ev3.opError
    with pytest.raises(ev3.DirCmdError) as exc:
        my_ev3.send_direct_cmd(ops)
        assert exc.args[0] == 'direct command 2B:00 replied error'


def test_brickname():
    '''set and read brickname'''
    my_ev3.verbosity = 0
    my_ev3.sync_mode = ev3.STD
    ops_get = b''.join((
        ev3.opCom_Get,
        ev3.GET_BRICKNAME,  # CMD
        ev3.LCX(32),  # LENGTH
        ev3.GVX(0)  # NAME (out)
    ))
    reply = my_ev3.send_direct_cmd(ops_get, global_mem=32)
    name_orig = struct.unpack(
        '32s',
        reply
    )[0].split(b'\x00')[0].decode("ascii")

    ops_set = b''.join((
        ev3.opCom_Set,
        ev3.SET_BRICKNAME,
        ev3.LCS('Bernie')
    ))
    my_ev3.send_direct_cmd(ops_set)

    reply = my_ev3.send_direct_cmd(ops_get, global_mem=32)
    name_tmp = struct.unpack(
        '32s',
        reply
    )[0].split(b'\x00')[0].decode("ascii")
    assert name_tmp == 'Bernie'

    ops_set = b''.join((
        ev3.opCom_Set,
        ev3.SET_BRICKNAME,
        ev3.LCS(name_orig)
    ))
    my_ev3.send_direct_cmd(ops_set)

    my_ev3.sync_mode = ev3.ASYNC
    msg_cnt = my_ev3.send_direct_cmd(ops_get, global_mem=32)
    reply = my_ev3.wait_for_reply(msg_cnt)
    name = struct.unpack(
        '32s',
        reply
    )[0].split(b'\x00')[0].decode("ascii")
    assert name == name_orig
