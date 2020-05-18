.. ev3_dc documentation master file, created by
   sphinx-quickstart on Wed Apr 22 12:59:19 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

.. title:: ev3_dc


Installation
============

Use pip to install from pypi::

  pip3 install --user ev3_dc


Examples
===========

The art of doing nothing
------------------------

We send the idle operation of the EV3 device to test the connection.

USB
~~~

Two steps for preparation:

  - Note the `MAC-address <https://en.wikipedia.org/wiki/MAC_address>`_ of your EV3 device,
    you can read it from your EV3's display under Brick Info / ID.
  - Take an USB cable and connect your EV3 device (the 2.0 Mini-B
    port, titled PC) with your computer.

Then modify the following program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_ev3.verbosity = 1
  my_ev3.sync_mode = ev3.SYNC
  ops = ev3.opNop
  my_ev3.send_direct_cmd(ops)

Replace the MAC-address ``00:16:53:42:2B:99`` with the one of your EV3
device (it must be the colon-separated format), then run the program.  If
everything is o.k., you will see an output like:

.. code-block:: none

  10:44:21.205319 Sent 0x|06:00|2A:00|00|00:00|01|
  10:44:21.214859 Recv 0x|03:00|2A:00|02|

Some remarks:

  - Both lines start with a timestamp.
  - The first line shows the sent data in a binary format. We separate
    bytes by colons ":" or vertical bars "|". Vertical bars separate
    these groups of bytes:
    
    - **Length of the message** (bytes 0, 1): The first two bytes are
      not part of the direct command itself. They are part of the
      communication protocol. The length is coded as a 2-byte unsigned
      integer in `little endian
      <https://en.wikipedia.org/wiki/Endianness>`_ format,
      0x|06:00| therefore stands for the value 6.
      
    - **Message counter** (bytes 2, 3): This is the footprint of the
      direct command. The message counter is included in the
      answer and allows to match the direct command and its
      reply. This too is a 2-byte unsigned integer in little endian
      format. The EV3 class starts counting with 0x|2A:00|, which is
      the value 42.
      
    - **Message type** (byte 4): For direct commands it may have the
      following two values:
      
      - DIRECT_COMMAND_REPLY = 0x|00|
      - DIRECT_COMMAND_NO_REPLY = 0x|80|

      In our case we set sync_mode=SYNC, which means we want
      the EV3 to reply all messages.

    - **Header** (bytes 5, 6): These two bytes, the last in front of
      the first operation are the header. It includes a combination of
      two numbers, which define the memory sizes of the direct command
      (yes, its plural, there are two memories, a local and a global
      one). Our command does not need any memory, therefore the header
      was set to 0x|00:00|.

    - **Operations** (starting at byte 7): Here one single
      byte, that stands for: opNOP = 0x|01|, do nothing, the idle
      operation of the EV3.

  - The second line shows the received data:
    
    - **Length of the message** (bytes 0, 1), here 3 bytes.
      
    - **Message counter** (bytes 2, 3): This fits the message counter
      of the corresponding request.
    
    - **Return status** (byte 4): For direct commands it may have the
      following two values:
      
      - DIRECT_REPLY = 0x|02|: the direct command was successfully operated.
      - DIRECT_REPLY_ERROR = 0x|04|: the direct command ended with an error.

If we had set the global memory to a value larger than 0 (e.g. calling
:py:meth:`~ev3_dc.EV3.send_direct_cmd` with a keyword argument
``global_mem=1``, we would have seen some additional data after the
return status.


Bluetooth
~~~~~~~~~

Remove the USB-cable, `couple (only steps 1 - 12)
<https://nrca.zendesk.com/hc/en-us/articles/115002669503-Bluetooth-How-to-connect-the-EV3-Robot-to-your-PC-Computer-by-wireless-Bluetooth>`_
your computer and your EV3 device via Bluetooth, then modify your
program by replacing USB by **ev3.BLUETOOTH**:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(
      protocol=ev3.BLUETOOTH,
      host='00:16:53:42:2B:99'
  )
  my_ev3.verbosity = 1
  my_ev3.sync_mode = ev3.SYNC
  ops = ev3.opNop
  my_ev3.send_direct_cmd(ops)

You will see a similar output, but the timespan between request and
reply will be longer, because the Bluetooth-connection is slower than
the USB-connection.


Wifi
~~~~

If you own a Wifi dongle, you can `connect (only steps 1 - 12)
<https://de.mathworks.com/help/supportpkg/legomindstormsev3io/ug/connect-to-an-ev3-brick-over-wifi.html>`_
your computer with your EV3 device via Wifi. Replace the protocol by
**ev3.WIFI** and start the program again. Your output will show you
a communication speed somewhere between USB and BLUETOOTH.


Tell your EV3 what to do
------------------------

Direct commands allow to send instructions with arguments.

Setting EV3's brickname
~~~~~~~~~~~~~~~~~~~~~~~

You can change the name of your EV3 brick by sending a direct command.

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.WIFI, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  ops = b''.join((
      ev3.opCom_Set,
      ev3.SET_BRICKNAME,
      ev3.LCS("myEV3")
  ))
  my_ev3.send_direct_cmd(ops)

Direct commands are built as byte strings. Multiple commands can be
concatenated. Here a single direct command is sent. The combination of
operation *opCom_Set* and CMD *SET_BRICKNAME* sets the brickname. This
command needs a single string argument and does not produce any
output. We let *sync_mode* be *STD*, which omits replies if the global
memory (space for return data) is unused.

The output of the program:

.. code-block:: none

  10:49:13.012039 Sent 0x|0E:00|2A:00|80|00:00|D4:08:84:6D:79:45:56:33:00|
  
Some remarks:

  - 0x|D4| is the bytecode of opCom_Set.
  - 0X|08| is the bytecode of SET_BRICKNAME.
  - 0x|84| is the bytecode of the leading identification byte of LCS character strings
    (in binary notation, it is: 0b 1000 0100).
  - 0x|6D:79:45:56:33| is the ascii bytecode of the string *myEV3*.
  - 0x|00| terminates LCS character strings.

Maybe you're not familiar with this vocabulary. The document *EV3
Firmware Developer Kit* is the reference book of the LEGO EV3 direct
commands and will help you. You find it under
`<http://www.lego.com/en-gb/mindstorms/downloads>`_. Read the details
about the leading identification byte in section *3.4 Parameter
encoding*.


Starting programs
~~~~~~~~~~~~~~~~~

Direct commands allow to start programs, which normally is done by
pressing buttons of the EV3 device. A program is a file, that exists
in the filesystem of the EV3. We will start
/home/root/lms2012/apps/Motor Control/Motor Control.rbf. This needs
two operations:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opFile,
      ev3.LOAD_IMAGE,
      ev3.LCX(1),  # SLOT
      ev3.LCS('../apps/Motor Control/Motor Control.rbf'),  # NAME
      ev3.LVX(0),  # SIZE
      ev3.LVX(4),  # IP*
      ev3.opProgram_Start,
      ev3.LCX(1),  # SLOT
      ev3.LVX(0),  # SIZE
      ev3.LVX(4),  # IP*
      ev3.LCX(0)  # DEBUG
  ))
  my_ev3.send_direct_cmd(ops, local_mem=8)

The first operation is the `loader
<https://en.wikipedia.org/wiki/Loader_(computing)>`_. It places a
program into memory and prepares it for execution. The second
operation starts the program. The return values of the first operation
are SIZE and IP*. We use :py:meth:`~ev3_dc.LVX` to write them to the
local memory at addresses 0 and 4. The second operation reads its
arguments SIZE and IP* from the local memory. It's arguments SLOT and
DEBUG are given as constant values.

We don't set verbosity and the command does not use any global memory,
therefore it sends the direct command and ends silently. But the
display of the EV3 device will show, that the program has been
started.


Reading data from EV3's sensors
-------------------------------
Direct commands allow to read data from your EV3 device.


Reading the current position of motors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If two large motors are connected with ports A and D, you can
start this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opInput_Device,
      ev3.READY_SI,
      ev3.LCX(0),  # LAYER
      ev3.port_motor_input(ev3.PORT_A),  # NO
      ev3.LCX(7),  # TYPE
      ev3.LCX(0),  # MODE
      ev3.LCX(1),  # VALUES
      ev3.GVX(0),  # VALUE1
      ev3.opInput_Device,
      ev3.READY_RAW,
      ev3.LCX(0),  # LAYER
      ev3.port_motor_input(ev3.PORT_D),  # NO
      ev3.LCX(7),  # TYPE
      ev3.LCX(0),  # MODE
      ev3.LCX(1),  # VALUES
      ev3.GVX(4)  # VALUE1
  ))
  reply = my_ev3.send_direct_cmd(ops, global_mem=8)
  pos_a, pos_d = struct.unpack('<fi', reply[5:])
  print(
      "positions in degrees (ports A and D): {} and {}".format(
          pos_a,
          pos_d
      )
  )

Section *5 Device type list* in *EV3 Firmware Developer Kit* lists
the sensors of the EV3 device. If you want to read the positions
of large motors in degrees, you will set TYPE=7 and MODE=0. We read
one value from each.

For demonstration pupose only, we use two different CMDs, *READY_SI*
and *READY_RAW*. Both of them read the current position of a motor,
but the first writes floating point data, the second interger data. We
use 8 bytes of global memory. The first 4 bytes hold the position of
motor A as a floating point number. The next 4 bytes hold the position
of motor D as an integer. Module `struct
<https://docs.python.org/3/library/struct.html>`_ is the tool of
choice to translate the packed binary little endian data into a float
and an int.





API documentation
=================
.. automodule:: ev3_dc


Static methods
--------------

LCX
~~~

Translates an integer into a direct command compatible number with identification byte.

.. autofunction:: ev3_dc.LCX

LCS
~~~

Adds a leading identification byte and an ending zero terminator
to an ascii string and returns a byte string.

.. autofunction:: ev3_dc.LCS

LVX
~~~

Translates an local memory adress into a direct command compatible format with identification byte.

.. autofunction:: ev3_dc.LVX

GVX
~~~

Translates an global memory adress into a direct command compatible format with identification byte.

.. autofunction:: ev3_dc.LVX

port_motor_input
~~~~~~~~~~~~~~~~

Allows to use well known motor ports of output commands for input commands too.

.. autofunction:: ev3_dc.port_motor_input


Classes
-------

EV3
~~~~

.. autoclass:: ev3_dc.EV3
   :members:

Jukebox
~~~~~~~

.. autoclass:: ev3_dc.Jukebox
   :members:

TwoWheelVehicle
~~~~~~~~~~~~~~~

.. autoclass:: ev3_dc.TwoWheelVehicle
   :members:

PID
~~~

.. autoclass:: ev3_dc.PID
   :members:

Index
=====

* :ref:`genindex`
