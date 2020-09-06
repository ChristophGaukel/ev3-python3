---
EV3
---

Class :py:class:`~ev3_dc.EV3` is the base class of ev3_dc. For using
it, you need to know some details of direct commands. The constructor
of EV3 establishes a connection between your computer and your EV3
brick.  The most interesting method is
:py:meth:`~ev3_dc.EV3.send_direct_cmd`, which sends a bytestring to
your EV3 brick. If this bytestring is well formed, your EV3 brick will
understand and execute its operations. If the bytestring requested it,
the EV3 brick will answer the direct command with some data.

Document `EV3 Firmware Developer Kit
<https://www.lego.com/cdn/cs/set/assets/blt77bd61c3ac436ea3/LEGO_MINDSTORMS_EV3_Firmware_Developer_Kit.pdf>`_
is the reference book of LEGO EV3 direct commands and will help
you.


The art of doing nothing
~~~~~~~~~~~~~~~~~~~~~~~~

We send the idle operation of the EV3 device to test the connection.

USB
...

Two steps for preparation:

  - Note the `MAC-address <https://en.wikipedia.org/wiki/MAC_address>`_ of your EV3 device,
    you can read it from your EV3's display under Brick Info / ID.
  - Take an USB cable and connect your EV3 device (the 2.0 Mini-B
    port, titled PC) with your computer.

Then modify the following program. Replace the MAC-address
``00:16:53:42:2B:99`` with the one of your EV3 device (it must be the
colon-separated format), then run the program.

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

If everything is o.k., you will see an output like:

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
.........

Remove the USB-cable, `couple
<https://nrca.zendesk.com/hc/en-us/articles/115002669503-Bluetooth-How-to-connect-the-EV3-Robot-to-your-PC-Computer-by-wireless-Bluetooth>`_
(only steps 1 - 12) your computer and your EV3 device via Bluetooth,
then modify your program by replacing ev3.USB by **ev3.BLUETOOTH**:

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
....

If you own a Wifi dongle, you can `connect
<https://de.mathworks.com/help/supportpkg/legomindstormsev3io/ug/connect-to-an-ev3-brick-over-wifi.html>`_
(only steps 1 - 12) your computer with your EV3 device via
Wifi. Replace the protocol by **ev3.WIFI** and start the program
again. Your output will show you a communication speed somewhere
between USB and BLUETOOTH.


Tell your EV3 what to do
~~~~~~~~~~~~~~~~~~~~~~~~

Direct commands allow to send instructions with arguments.

.. _changing_led_colors_label:

Changing LED colors
...................

There are some light effects on the EV3 brick. You can change the
colors of the LEDs and this is done by operation *opUI_Write* with CMD
*LED*.

opUI_Write = 0x|82| with CMD LED = 0x|1B| needs one argument:

  - PATTERN: GREEN = 0x|01|, RED = 0x|02|, etc.

Take an USB cable and connect your EV3 brick
with your computer. Replace the
MAC-address by the one of your EV3 brick, then
start the program.

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  ops = b''.join((
      ev3.opUI_Write,  # operation
      ev3.LED,  # CMD
      ev3.LED_RED_FLASH  # PATTERN
  ))
  my_ev3.send_direct_cmd(ops)
  
  sleep(5)
  ops = b''.join((
      ev3.opUI_Write,
      ev3.LED,
      ev3.LED_GREEN
  ))
  my_ev3.send_direct_cmd(ops)

This program sends two direct commands with a timespan of 5
sec. between them. The first one changes the LED color to a red flashing,
the second sets the well known green color.

The output:

.. code-block:: none

  10:43:38.601015 Sent 0x|08:00|2A:00|00|00:00|82:1B:05|
  10:43:38.616028 Recv 0x|03:00|2A:00|02|
  10:43:43.620023 Sent 0x|08:00|2B:00|00|00:00|82:1B:01|
  10:43:43.630105 Recv 0x|03:00|2B:00|02|
  
Some remarks:

  - The default *sync_mode* of the USB protocol is *SYNC*. This is why
    both direct commands were replied.
  - EV3 increments the message counter. The first command got 0x|2A:00|,
    which is the value 42, the second command got 0x|2B:00| (value 43).
  - 0x|82| is the bytecode of operation *opUI_Write*.
  - 0x|1B| is the bytecode of CMD *LED*.
  - 0x|05| is the bytecode of *LED_RED_FLASH*.
  - 0x|01| is the bytecode of *LED_GREEN*.

If we replace *protocol=ev3.USB* by *protocol=ev3.BLUETOOTH*, we get
this output:

.. code-block:: none

  10:44:47.266688 Sent 0x|08:00|2A:00|80|00:00|82:1B:05|
  10:44:52.272881 Sent 0x|08:00|2B:00|80|00:00|82:1B:01|

The *message type* changed from 0x|00| (DIRECT_COMMAND_REPLY) to
0x|80| (DIRECT_COMMAND_NO_REPLY) and the EV3 brick indeed did not
reply. This happens because *protocol* BLUETOOTH defaults to
*sync_mode* STD.

Setting EV3's brickname
.......................

You can change the name of your EV3 brick by sending a direct command.

opCom_Set = 0x|D4| with CMD SET_BRICKNAME = 0x|08| needs one argument:

  - NAME: (DATA8) – First character in character string

Some more explanations of argument NAME will follow. The text above
is, what the LEGO documentation says.

The program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.WIFI, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  ops = b''.join((
      ev3.opCom_Set,  # operation
      ev3.SET_BRICKNAME,  # CMD
      ev3.LCS("myEV3")  # NAME
  ))
  my_ev3.send_direct_cmd(ops)

Direct commands are built as byte strings. Multiple operations can be
concatenated. Here a single operation is sent. The combination of
operation *opCom_Set* and CMD *SET_BRICKNAME* sets the brickname. This
command needs a single string argument and does not produce any
output. We let *sync_mode* be *STD*, which omits replies if the global
memory (space for return data) is unused.

The output of the program:

.. code-block:: none

  10:49:13.012039 Sent 0x|0E:00|2A:00|80|00:00|D4:08:84:6D:79:45:56:33:00|
  
Some remarks:

  - 0x|D4| is the bytecode of operation *opCom_Set*.
  - 0X|08| is the bytecode of CMD *SET_BRICKNAME*.
  - 0x|84| is the bytecode of the leading identification byte of
    :py:func:`~ev3_dc.LCS` character strings (in binary notation, it is:
    0b 1000 0100). If any argument is a string, it will be sent as an
    LCS, which says a leading and a trailing byte must be added.
  - 0x|6D:79:45:56:33| is the ascii bytecode of the string *myEV3*.
  - 0x|00| terminates LCS character strings.

Maybe you're not familiar with this vocabulary. Document `EV3
Firmware Developer Kit
<https://www.lego.com/cdn/cs/set/assets/blt77bd61c3ac436ea3/LEGO_MINDSTORMS_EV3_Firmware_Developer_Kit.pdf>`_
is the will help you. Read the details about the leading
identification byte in section *3.4 Parameter encoding*.


Starting programs
.................

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
program into memory and prepares it for execution. The second operation starts the
program. The return values of the first operation are SIZE and IP*. We
use :py:meth:`~ev3_dc.LVX` to write them to the local memory at
addresses 0 and 4. The second operation reads its arguments SIZE and
IP* from the local memory. It's arguments SLOT and DEBUG are given as
constant values.

Paths can be absolute or relative. Relative paths, like the above one,
are relative to */home/root/lms2012/sys/*. We don't set verbosity and
the command does not use any global memory, therefore it sends the
direct command and ends silently. But the display of the EV3 device
will show, that the program has been started.


Playing Sound Files
...................

Take an USB cable and connect your EV3 brick
with your computer. Replace the
MAC-address by the one of your EV3 brick, then
start the program.

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  ops = b''.join((
      ev3.opSound,  # operation
      ev3.PLAY,  # CMD
      ev3.LCX(100),  # VOLUME
      ev3.LCS('./ui/DownloadSucces')  # NAME
  ))
  my_ev3.send_direct_cmd(ops)

The output:

.. code-block:: none

  10:20:05.004355 Sent 0x|1E:00|2A:00|00|00:00|94:02:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  10:20:05.022584 Recv 0x|03:00|2A:00|02|

opSound with CMD *PLAY* needs two arguments:

  - volume in percent as an integer value [0 - 100]
  - name of the sound file (without extension ".rsf") as absolute
    path, or relative to */home/root/lms2012/sys/*

The default *sync_mode* of the USB protocol is *SYNC*. This is why
the direct command was replied.

.. _playing_sound_files_repeatedly_label:

Playing Sound Files repeatedly
..............................

As above, take an USB cable, connect your EV3 brick with your computer
and replace the MAC-address by the one of your EV3 brick, then start
this program.

.. code:: python3

  import ev3_dc as ev3
  import time
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  ops = b''.join((
      ev3.opSound,  # operation
      ev3.REPEAT,  # CMD
      ev3.LCX(100),  # VOLUME
      ev3.LCS('./ui/DownloadSucces')  # NAME
  ))
  my_ev3.send_direct_cmd(ops)
  
  time.sleep(5)
  ops = b''.join((
      ev3.opSound,
      ev3.BREAK
  ))
  my_ev3.send_direct_cmd(ops)

This program sends two direct commands with a timespan of 5
sec. between them. The first one starts the repeated playing
of a sound file, the second stops the playing.

The output:

.. code-block:: none

  10:26:20.466604 Sent 0x|1E:00|2A:00|00|00:00|94:03:81:64:84:2E:2F:75:69:2F:44:6F:77:6E:6C:6F:61:64:53:75:63:63:65:73:00|
  10:26:20.481941 Recv 0x|03:00|2A:00|02|
  10:26:25.487598 Sent 0x|07:00|2B:00|00|00:00|94:00|
  10:26:25.500652 Recv 0x|03:00|2B:00|02|

EV3 increments the message counter. The first command got 0x|2A:00|,
which is the value 42, the second command got 0x|2B:00| (value 43).

Playing Tones
.............

We send a direct command, that plays a flourish in c, which consists
of four tones:

  - c' (262 Hz)
  - e' (330 Hz)
  - g' (392 Hz)
  - c'' (523 Hz)

.. code:: python3

  import ev3_dc as ev3

  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opSound,  # operation
      ev3.TONE,  # CMD
      ev3.LCX(1),  # volume
      ev3.LCX(262),  # frequency
      ev3.LCX(1000),  # duration
      ev3.opSound_Ready,  # operation
      ev3.opSound,
      ev3.TONE,
      ev3.LCX(1),
      ev3.LCX(330),
      ev3.LCX(1000),
      ev3.opSound_Ready,
      ev3.opSound,
      ev3.TONE,
      ev3.LCX(1),
      ev3.LCX(392),
      ev3.LCX(1000),
      ev3.opSound_Ready,
      ev3.opSound,
      ev3.TONE,
      ev3.LCX(2),
      ev3.LCX(523),
      ev3.LCX(2000)
  ))
  my_ev3.send_direct_cmd(ops)

The single direct command consists of 7 operations. *opSound_Ready*
prevents interruption. Without it, only the last tone could be
heard. The duration is in milliseconds.

Drawing and Timers
..................

Contolling time is an important aspect in real time programs. We have
seen how to wait until a tone ended and we waited in the python program
until we stopped the repeated playing of a sound file. The operation
set of the EV3 includes timer operations which allow to wait in the
execution of a direct command. This needs the following two operations:

opTimer_Wait = 0x|85| with two arguments:

  - (Data32) TIME: Time to wait (in milliseconds)
  - (Data32) TIMER: Variable used for timing

This operation writes a 4-bytes timestamp into the local or global memory.

opTimer_Ready = 0x|86| with one argument:

  - (Data32) TIMER: Variable used for timing

This operation reads a timestamp and waits until the actual time reaches the value of this timestamp.

We test the timer operations with a program that draws a triangle. This needs operation *opUI_Draw*
with CMD *LINE* three times.

opUI_Draw = 0x|84| with CMD LINE = 0x|03| and the arguments:

  - (Data8) COLOR: Specify either black or white, [0: White, 1: Black]
  - (Data16) X0: Specify X start point, [0 - 177]
  - (Data16) Y0: Specify Y start point, [0 - 127]
  - (Data16) X1: Specify X end point
  - (Data16) Y1: Specify Y end point

The program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opUI_Draw,
      ev3.TOPLINE,
      ev3.LCX(0),  # ENABLE
      ev3.opUI_Draw,
      ev3.FILLWINDOW,
      ev3.LCX(0),  # COLOR
      ev3.LCX(0),  # Y0
      ev3.LCX(0),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE,
      ev3.opTimer_Wait,
      ev3.LCX(2000),
      ev3.LVX(0),
      ev3.opTimer_Ready,
      ev3.LVX(0),
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(2),  # X0
      ev3.LCX(125),  # Y0
      ev3.LCX(88),  # X1
      ev3.LCX(2),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE,
      ev3.opTimer_Wait,
      ev3.LCX(1000),
      ev3.LVX(0),
      ev3.opTimer_Ready,
      ev3.LVX(0),
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(88),  # X0
      ev3.LCX(2),  # Y0
      ev3.LCX(175),  # X1
      ev3.LCX(125),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE,
      ev3.opTimer_Wait,
      ev3.LCX(1000),
      ev3.LVX(0),
      ev3.opTimer_Ready,
      ev3.LVX(0),
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(175),  # X0
      ev3.LCX(125),  # Y0
      ev3.LCX(2),  # X1
      ev3.LCX(125),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE
  ))
  my_ev3.send_direct_cmd(ops, local_mem=4)

This program cleans the display, then waits for two seconds, draws a
line, waits for one second, draws another line, waits and finally
draws a third line. It needs 4 bytes of local memory, which are
multiple times written and red. *opTimer_Wait* writes a timestamp to
local memory address 0 and *opTimer_Ready* reads it from local memory
address 0.

Obviously the timing can be done in the local program or in the direct
command. We change the program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opUI_Draw,
      ev3.TOPLINE,
      ev3.LCX(0),  # ENABLE
      ev3.opUI_Draw,
      ev3.FILLWINDOW,
      ev3.LCX(0),  # COLOR
      ev3.LCX(0),  # Y0
      ev3.LCX(0),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE
  ))
  my_ev3.send_direct_cmd(ops)
  
  sleep(2)
  ops = b''.join((
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(2),  # X0
      ev3.LCX(125),  # Y0
      ev3.LCX(88),  # X1
      ev3.LCX(2),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE
  ))
  my_ev3.send_direct_cmd(ops)
  
  sleep(1)
  ops = b''.join((
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(88),  # X0
      ev3.LCX(2),  # Y0
      ev3.LCX(175),  # X1
      ev3.LCX(125),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE
  ))
  my_ev3.send_direct_cmd(ops)
  
  sleep(1)
  ops = b''.join((
      ev3.opUI_Draw,
      ev3.LINE,
      ev3.LCX(1),  # COLOR
      ev3.LCX(175),  # X0
      ev3.LCX(125),  # Y0
      ev3.LCX(2),  # X1
      ev3.LCX(125),  # Y1
      ev3.opUI_Draw,
      ev3.UPDATE
  ))
  my_ev3.send_direct_cmd(ops)

Both alternatives result in the same behaviour of the display but are
different. The first version needs less communication but blocks the
EV3 device for four seconds (until the direct command ends its
execution). The second version needs four direct commands but does not
block the EV3 brick. All its direct commands need a short execution
time and allow to send other direct commands in between.

Simulating Button presses
.........................

In this example, we shut down the EV3 brick by simulating button
presses. We use two operations:

*opUI_Button* = 0x|83| with CMD *PRESS* = 0x|05| needs one argument:

  - BUTTON

    - NO_BUTTON = 0x|00|
    - UP_BUTTON = 0x|01|
    - ENTER_BUTTON = 0x|02|
    - DOWN_BUTTON = 0x|03|
    - RIGHT_BUTTON = 0x|04|
    - LEFT_BUTTON = 0x|05|
    - BACK_BUTTON = 0x|06|
    - ANY_BUTTON = 0x|07|

*opUI_Button* = 0x|83| with CMD *WAIT_FOR_PRESS* = 0x|03| needs no argument.

To prevent interruption, we need to wait until the initiated
operations are finished. This is done by the second operation.

The program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  
  ops = b''.join((
      ev3.opUI_Button,  # operation
      ev3.PRESS,  # CMD
      ev3.BACK_BUTTON,
      ev3.opUI_Button,  # operation
      ev3.WAIT_FOR_PRESS,  # CMD
      ev3.opUI_Button,
      ev3.PRESS,
      ev3.RIGHT_BUTTON,
      ev3.opUI_Button,
      ev3.WAIT_FOR_PRESS,
      ev3.opUI_Button,
      ev3.PRESS,
      ev3.ENTER_BUTTON
  ))
  my_ev3.send_direct_cmd(ops)
    

Reading data from EV3's sensors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Direct commands allow to read data from your EV3 device.
The most important operation for reading data is:

*opInput_Device* = 0x|99| with CMD *READY_RAW* = 0x|1C|

  Arguments
  
    - (Data8) LAYER: Specify chain layer number [0-3]
    - (Data8) NO: Port number
    - (Data8) TYPE: Specify device type (0 = Don’t change type)
    - (Data8) MODE: Device mode [0-7] (-1 = Don’t change mode)
    - (Data8) VALUES: Number of return values
  
  Returns
  
    - (Data32) VALUE1: First value received from sensor in the
      specified mode

There are two siblings, that read data a bit different:

  - *opInput_Device* = 0x|99| with CMD *READY_PCT* = 0x|1B| writes
    integer data in the range [0 - 100], that must be interpreted as a
    percentage.
  - *opInput_Device* = 0x|99| with CMD *READY_SI* = 0x|1D| writes floating point data.

Return data can be written to the local or global memory. Use function
:py:func:`~ev3_dc.LVX` to address the local memory and
:py:func:`~ev3_dc.GVX` to address the global memory (e.g. GVX(0)
addresses the first byte of the global memory).

Another operation, that may be important for sensors, resets the
sensor at a specific port. This sets the sensor to its initial state
and clears its counters.

*opInput_Device* = 0x|99| with CMD *CLR_CHANGES* = 0x|1A|

  Arguments
  
    - (Data8) LAYER: Specify chain layer number [0-3]
    - (Data8) NO: Port number

Introspection
.............

There is an operation, that asks for the type and mode of a sensor at a specified port.

*opInput_Device* = 0x|99| with CMD *GET_TYPEMODE* = 0x|05|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NO: port number
  
  Returns
  
    - (Data8) TYPE: device type
    - (Data8) MODE: device mode

Please connect some sensors to your sensor ports and some motors to
your motor ports. Then connect your EV3 brick and your computer with
an USB cable. Replace the MAC-address by the one of your EV3 brick.
The following program sends two direct commands, the first asks for
the sensors, the second for the motors.

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  
  def create_ops(ports: tuple, motors=False):
      if motors:
          ports = tuple(ev3.port_motor_input(port) for port in ports)
      ops = b''
      for i in range(4):
          ops += b''.join((
              ev3.opInput_Device,  # operation
              ev3.GET_TYPEMODE,  # CMD
              ev3.LCX(0),  # LAYER
              ports[i],  # NO
              ev3.GVX(2*i),  # TYPE (output)
              ev3.GVX(2*i + 1)  # MODE (output)
          ))
      return ops
  
  
  def print_table(port_names: tuple, answer: tuple):
      print('-'*20)
      print('port | type | mode |')
      print('-'*20)
      for i in range(4):
          print(
              '   {} |'.format(
                  port_names[i]
              ),
              end=''
          )
          if answer[2*i] == 126:
              print('    - |    - |')
          else:
              print(
                  '  {:3d} |  {:3d} |'.format(
                      answer[2*i],
                      answer[2*i + 1]
                  )
              )
      print('-'*20)
      print()
  
  
  # sensors
  ports = (ev3.PORT_1, ev3.PORT_2, ev3.PORT_3, ev3.PORT_4)
  ops = create_ops(ports)
  reply = my_ev3.send_direct_cmd(ops, global_mem=8)
  answer = struct.unpack('8B', reply)
  
  print()
  print('Sensor ports:')
  print_table(
      ('1', '2', '3', '4'),
      answer
  )
  
  # motors
  ports = (ev3.PORT_A, ev3.PORT_B, ev3.PORT_C, ev3.PORT_D)
  ops = create_ops(ports, motors=True)
  reply = my_ev3.send_direct_cmd(ops, global_mem=8)
  answer = struct.unpack('8B', reply)
  
  print()
  print('Motor ports:')
  print_table(
      ('A', 'B', 'C', 'D'),
      answer
  )
        
Some Remarks:

  - Each operation *opInput_Device* with CMD *GET_TYPEMODE* answers
    with two bytes of data, one byte for the type, another for the
    mode.
  - It's the python program that decides, how to place the data into
    the global memory. Every :py:func:`~ev3_dc.GVX` directs some
    output data to an address of the global memory.
  - *reply* is a byte string of 8 bytes length, *answer* is a tuple of
    8 byte numbers.
  - `struct <https://docs.python.org/3/library/struct.html>`_ is the tool of
    choice to translate binary data into python data types.
  - :py:func:`~ev3_dc.port_motor_input` allows to use the same motor
    port constants for input and output.
  - type *126* stands for *no sensor connected*.

The output:

.. code-block:: none

  09:25:12.400013 Sent 0x|1D:00|2A:00|00|08:00|99:05:00:00:60:61:99:05:00:01:62:63:99:05:00:02:64:65:99:05:00:03:66:67|
  09:25:12.410124 Recv 0x|0B:00|2A:00|02|10:00:1D:00:21:00:7E:00|
  
  Sensor ports:
  --------------------
  port | type | mode |
  --------------------
     1 |   16 |    0 |
     2 |   29 |    0 |
     3 |   33 |    0 |
     4 |    - |    - |
  --------------------
  
  09:25:12.411241 Sent 0x|1D:00|2B:00|00|08:00|99:05:00:10:60:61:99:05:00:11:62:63:99:05:00:12:64:65:99:05:00:13:66:67|
  09:25:12.417945 Recv 0x|0B:00|2B:00|02|07:00:7E:00:08:00:07:00|
  
  Motor ports:
  --------------------
  port | type | mode |
  --------------------
     A |    7 |    0 |
     B |    - |    - |
     C |    8 |    0 |
     D |    7 |    0 |
  --------------------

*Section 5 Device type list* in `EV3 Firmware Developer Kit
<https://www.lego.com/cdn/cs/set/assets/blt77bd61c3ac436ea3/LEGO_MINDSTORMS_EV3_Firmware_Developer_Kit.pdf>`_
lists the sensor types and modes of the EV3 device and helps to
understand these numbers.

Touch mode of the Touch Sensor
..............................

We use operation *opInput_Device* to ask the touch sensor if it currently is touched.
Connect your touch sensor with port 1, take an USB-cable and connect
your computer with your EV3 brick, replace the MAC-address with the one
of your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  # touch sensor at port 1
  ops = b''.join((
      ev3.opInput_Device,  # operation
      ev3.READY_SI,  # CMD
      ev3.LCX(0),  # LAYER
      ev3.PORT_1,  # NO
      ev3.LCX(16),  # TYPE (EV3-Touch)
      ev3.LCX(0),  # MODE (Touch)
      ev3.LCX(1),  # VALUES
      ev3.GVX(0)  # VALUE1 (output)
  ))
  reply = my_ev3.send_direct_cmd(ops, global_mem=4)
  touched = struct.unpack('<f', reply)[0]
  
  print()
  print(
          'The sensor is',
          ('not touched', 'touched')[int(touched)]
  )

Some remarks:

  - The single return value of *opInput_Device* with CMD *READY_SI* is
    a floating point number of 4 bytes length in `little endian
    <https://en.wikipedia.org/wiki/Endianness>`_ notation.
  - With GVX(0) we write it to the global memory address 0. This says, it takes
    the first 4 bytes of the global memory.
  - Method :py:func:`~ev3_dc.EV3.send_direct_cmd` skips the leading
    bytes of the reply and returns the global memory only.
  - `struct <https://docs.python.org/3/library/struct.html>`_ is the
    tool of choice to translate the packed binary little endian data
    into python data format. :py:meth:`struct.unpack` returns a tuple,
    from where we pick the first (and only) item.

The output:

.. code-block:: none

  09:35:17.516913 Sent 0x|0D:00|2A:00|00|04:00|99:1D:00:00:10:00:01:60|
  09:35:17.524934 Recv 0x|07:00|2A:00|02|00:00:80:3F|
  
  The sensor is touched

0x|00:00:80:3F| is the little endian notation of the floating point
number 1.0.

Bump mode of the Touch Sensor
..............................

The bump mode of the touch sensor counts the number of touches since the
last reset. The following program resets the counter of the touch sensor, waits
for five seconds, then asks about the number of touches.

If you own a Wifi dongle and both, you computer and your EV3 brick are
connected to the Wifi, then you can start the following program after
you replaced the MAC-address. If not, replace the protocol by USB or
by BLUETOOTH.

.. code:: python3

  import ev3_dc as ev3
  import struct
  from time import sleep
  
  my_ev3 = ev3.EV3(protocol=ev3.WIFI, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  # clear port 1
  ops = b''.join((
      ev3.opInput_Device,  # operation
      ev3.CLR_CHANGES,  # CMD
      ev3.LCX(0),  # LAYER
      ev3.PORT_1  # NO
  ))
  my_ev3.send_direct_cmd(ops)
  
  print('\ncounting starts now ...\n')
  sleep(5)
  
  # touch sensor at port 1
  ops = b''.join((
      ev3.opInput_Device,  # operation
      ev3.READY_SI,  # CMD
      ev3.LCX(0),  # LAYER
      ev3.PORT_1,  # NO
      ev3.LCX(16),  # TYPE (EV3-Touch)
      ev3.LCX(1),  # MODE (Bump)
      ev3.LCX(1),  # VALUES
      ev3.GVX(0)  # VALUE1 (output)
  ))
  reply = my_ev3.send_direct_cmd(ops, global_mem=4)
  touched = struct.unpack('<f', reply)[0]
  
  print()
  print(
          'The sensor was',
          int(touched),
          'times touched'
  )

The output:

.. code-block:: none

  09:37:04.402440 Sent 0x|09:00|2A:00|80|00:00|99:1A:00:00|
  
  counting starts now ...
  
  09:37:09.418332 Sent 0x|0D:00|2B:00|00|04:00|99:1D:00:00:10:01:01:60|
  09:37:09.435870 Recv 0x|07:00|2B:00|02|00:00:40:41|
  
  The sensor was 12 times touched
  
If you compare the two direct commands, you will realize some differences:

  - The length is different.
  - The message counter has been incremented.
  - The message types are different, the first one is
    *DIRECT_COMMAND_NO_REPLY*, the second one is
    *DIRECT_COMMAND_REPLY*. Consequently, the first command does not get
    a reply. If you use protocol USB, this will change and all direct
    commands will be replied.
  - The header is different. The first direct command does not use any global or local memory,
    the second needs 4 bytes of global memory.
  - The operations are different, which is not surprising.

Measure distances
.................

Use operation *opInput_Device* to read data of the infrared sensor.
Connect your EV3 infrared sensor with port 3, take an USB-cable and connect
your computer with your EV3 brick, replace the MAC-address with the one
of your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  # infrared sensor at port 3
  ops = b''.join((
      ev3.opInput_Device,
      ev3.READY_SI,
      ev3.LCX(0),  # LAYER
      ev3.PORT_3,  # NO
      ev3.LCX(33),  # TYPE - EV3-IR
      ev3.LCX(0),  # MODE - Proximity
      ev3.LCX(1),  # VALUES
      ev3.GVX(0)  # VALUE1
  ))
  reply = my_ev3.send_direct_cmd(ops, global_mem=4)
  distance = struct.unpack('<f', reply)[0]
  
  print('\nSomething detected at a distance of {:2.0f} cm.'.format(distance))

The output:

.. code-block:: none

  09:45:34.223216 Sent 0x|0E:00|2A:00|00|04:00|99:1D:00:02:81:21:00:01:60|
  09:45:34.229976 Recv 0x|07:00|2A:00|02|00:00:D0:41|
  
  Something detected at a distance of 26 cm.


Seeker and Beacon
.................

Combining the EV3 infrared sensor and the EV3 beacon identifies
the position of one to four beacons. A beacon send signals on one of four
channels and the infrared sensor measures its own position relative to
the position the beacon.

Connect your EV3 infrared sensor with port 3, take an USB-cable and
connect your computer with your EV3 brick, replace the MAC-address with
the one of your EV3 brick, switch on the beacon, select a channel,
place it in front of the infrared sensor, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  ops_read = b''.join((
      ev3.opInput_Device,  # operation
      ev3.READY_RAW,  # CMD
      ev3.LCX(0),  # LAYER
      ev3.PORT_3,  # NO
      ev3.LCX(33),  # TYPE - IR
      ev3.LCX(1),  # MODE - Seeker
      ev3.LCX(8),  # VALUES
      ev3.GVX(0),  # VALUE1 - heading   channel 1
      ev3.GVX(4),  # VALUE2 - proximity channel 1
      ev3.GVX(8),  # VALUE3 - heading   channel 2
      ev3.GVX(12),  # VALUE4 - proximity channel 2
      ev3.GVX(16),  # VALUE5 - heading   channel 3
      ev3.GVX(20),  # VALUE6 - proximity channel 3
      ev3.GVX(24),  # VALUE7 - heading   channel 4
      ev3.GVX(28)  # VALUE8 - proximity channel 4
  ))
  reply = my_ev3.send_direct_cmd(ops_read, global_mem=32)
  answer = struct.unpack('<8i', reply)
  
  for i in range(4):
      # proximity (little endian) == 0x|00:00:00:80| means no signal
      if answer[2*i + 1] == -2147483648:
          continue
  
      print(
          '\nchannel: {}, heading: {}, proximity: {}'.format(
              i + 1,
              answer[2*i],
              answer[2*i + 1]
          )
      )

Some remarks:

  - Type 33 (IR) with Mode 1 (Seeker) writes 8 data values, heading
    and proximity of four channels.
  - In case of CMD *READY_RAW*, these are 8 integer values, each of
    four bytes length. This needs 32 bytes of global memory.
  - `struct <https://docs.python.org/3/library/struct.html>`_
    translates the packed binary little endian data of the global memory
    and returns a tuple of eight integer values.
  - A proximity of 0x|00:00:00:80| (little endian, the heighest bit is
    1, all others are 0) has a special meaning. It says, on this
    channel the infrared sensor did not receive a signal. Interpeted
    as a signed litlle endian integer, 0x|00:00:00:80| becomes
    :math:`- 2,147,483,648 = - 2^{31}`, the smallest of all values.
  - Using a single beacon means, three channels without signal, one
    channel with. Channels without signal are sorted out.

The output:

.. code-block:: none

  10:05:43.514714 Sent 0x|15:00|2A:00|00|20:00|99:1C:00:02:81:21:01:08:60:64:68:6C:70:74:78:7C|
  10:05:44.629441 Recv 0x|23:00|2A:00|02|00:00:00:00:00:00:00:80:EB:FF:FF:FF:1B:00:00:00:00:00:00:00:00:00:00:80:00:00:00:00:00:00:00:80|
  
  channel: 2, heading: -21, proximity: 27

Some remarks:

  - Heading is in the range [-25 - 25], negative values stand for the
    left, 0 for straight, positive for the right side.
  - Proximity is in the range [0 - 100] and measures in cm.
  - In my case, the beacon was far left, 27 cm apart and sended on
    channel 2.
  

Reading the color
.................

We use operation *opInput_Device* to read data of the color sensor.
Connect your color sensor with port 2, take an USB-cable and connect
your computer with your EV3 brick, replace the MAC-address with the one
of your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  
  my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  # color sensor at port 2
  ops = b''.join((
      ev3.opInput_Device,  # operation
      ev3.READY_RAW,  # CMD
      ev3.LCX(0),  # LAYER
      ev3.PORT_2,  # NO
      ev3.LCX(29),  # TYPE (EV3-Color)
      ev3.LCX(2),  # MODE (Color)
      ev3.LCX(1),  # VALUES
      ev3.GVX(0)  # VALUE1 (output)
  ))
  reply = my_ev3.send_direct_cmd(ops, global_mem=4)
  color_nr = struct.unpack('<i', reply)[0]
  
  color_str = (
      'none',
      'black',
      'blue',
      'green',
      'yellow',
      'red',
      'white',
      'brown'
  )[color_nr]
  print('\nThis color is', color_str)

The output:

.. code-block:: none

  09:49:32.461804 Sent 0x|0D:00|2A:00|00|04:00|99:1C:00:01:1D:02:01:60|
  09:49:32.467874 Recv 0x|07:00|2A:00|02|03:00:00:00|
  
  This color is green

There are some more color sensor modes, maybe you like to test these:

  - Mode 0 (Reflected) - switches on the red light and measures the inensity
    of the reflection, which is dependent from distance, color and the reflection factor
    of the surface.
  - Mode 1 (Ambient) - switches on the blue light (why?) and measures the intensity of
    the ambient light.
  - Mode 4 (RGB-Raw)  - switches on red, green and blue light and measures the intensity of
    the reflected light.

  


Reading the current position of motors
......................................

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
      ev3.LCX(7),  # TYPE (EV3-Large-Motor)
      ev3.LCX(0),  # MODE (Degree)
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
  pos_a, pos_d = struct.unpack('<fi', reply)
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
but the first writes floating point data, the second integer data. We
use 8 bytes of global memory. The first 4 bytes hold the position of
motor A as a floating point number. The next 4 bytes hold the position
of motor D as an integer. Module `struct
<https://docs.python.org/3/library/struct.html>`_ is the tool of
choice to translate the packed binary little endian data into a float
and an int.


Moving motors
~~~~~~~~~~~~~

A number of operations is used for motor movements.

Exact movements, blocking the EV3 brick
.......................................

Exact and smooth movements of a mootor are our first theme. We start
with using four operations:

*opOutput_Reset* = 0x|A2|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)

  The EV3 brick tracks exact movements and does some corrections of
  overshooting or manual movements. *opOutput_Reset* resets these
  tracking informations. It does not clear the counter.

*opOutput_Step_Speed* = 0x|AE|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)
    - (Data8) SPEED: direction (sign) and speed of movement [-100, 100]
    - (Data32) STEP1: length of acceleration
    - (Data32) STEP2: length of constant speed movement
    - (Data32) STEP3: length of deceleration
    - (Data8) BRAKE: flag if ending with floating motor or active
      break [0: Float, 1: Break]

  This operation defines a smooth and exact movement of one or
  multiple motors. Dependent from the mode, *STEP1*, *STEP2* and *STEP3* are
  in degrees (default) or rotations.

*opOutput_Ready* = 0x|AA|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)

  Starts the movement and waits until the movement has finished.

*opOutput_Stop* = 0x|A3|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)
    - (Data8) BRAKE: flag if ending with floating motor or active
      break [0: Float, 1: Break]

  Stops the current movement of one or multiple motors.

Connect your EV3 medium motor with port B, connect your computer via
Bluetooth with your EV3 brick, replace the MAC-address with the one of
your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  jukebox.song(ev3.FRERE_JACQUES).start()
  
  
  def reset():
      ops = b''.join((
          ev3.opOutput_Reset,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B)  # NOS
      ))
      my_ev3.send_direct_cmd(ops, sync_mode=ev3.SYNC)
  
  
  def step_speed(speed: int):
      ops_step_speed = b''.join((
          ev3.opOutput_Step_Speed,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.LCX(speed),  # SPEED
          ev3.LCX(15),  # STEP1
          ev3.LCX(60),  # STEP2
          ev3.LCX(15),  # STEP3
          ev3.LCX(1)  # BRAKE - yes
      ))
      ops_ready = b''.join((
          ev3.opOutput_Ready,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B)  # NOS
      ))
      my_ev3.send_direct_cmd(ops_step_speed + ops_ready, sync_mode=ev3.SYNC)
  
  
  def stop():
      ops = b''.join((
          ev3.opOutput_Stop,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.LCX(0)  # BRAKE - no
      ))
      my_ev3.send_direct_cmd(ops)
  
  
  speed = 5
  
  reset()
  for i in range(5):
      step_speed(speed)
      step_speed(-speed)
  
  sleep(.2)
  stop()
  
Some remarks:

  - Function :py:func:`reset` resets the tracking information of the
    motor at port B.
  - Function :py:func:`step_speed` does a 90 ° smooth movement of the
    motor at port B. Dependent from the sign of SPEED the movement is
    forwards or backwards. The three numbers STEP1, STEP2 and
    STEP3 define the lengths of the acceleration, the constant speed
    and the deceleration phase, all of them in degrees. The movement
    ends with an active break, which holds the motor in a defined
    position. It waits until the movement has finished.
  - Function :py:func:`stop` releases the brake. This is done 0.2 sec.
    after the last movement has finished.
  - There are 10 slow and smooth movements of the motor, 5 times
    forwards and backwards. If you fix an infrared sensor on top of
    the shaft, this looks like headshaking. Changing the speed will
    change the character of the headshaking.
  - Setting *sync_mode=SYNC* allows to get the reply just when the
    movement has finished.
  - The program plays the song *Frère Jacques* parallel to the motor
    movement.
  - Using two classes *EV3* and *Jukebox* is not necessary. *Jukebox*
    as a subclass of *EV3* would have done the job alone. But this
    example demonstrates, how specialized subclasses of *EV3* can
    handle specific tasks, like *Jukebox* handles sound. And multiple
    subclasses of *EV3* can work together.

The output:

.. code-block:: none

  11:52:26.168681 Sent 0x|08:00|2A:00|00|00:00|A2:00:02|
  11:52:26.247070 Recv 0x|03:00|2A:00|02|
  11:52:26.248399 Sent 0x|11:00|2D:00|00|00:00|AE:00:02:05:0F:81:3C:0F:01:AA:00:02|
  11:52:27.402000 Recv 0x|03:00|2D:00|02|
  11:52:27.403093 Sent 0x|11:00|2F:00|00|00:00|AE:00:02:3B:0F:81:3C:0F:01:AA:00:02|
  11:52:28.578030 Recv 0x|03:00|2F:00|02|
  11:52:28.578578 Sent 0x|11:00|30:00|00|00:00|AE:00:02:05:0F:81:3C:0F:01:AA:00:02|
  11:52:29.735028 Recv 0x|03:00|30:00|02|
  11:52:29.736302 Sent 0x|11:00|33:00|00|00:00|AE:00:02:3B:0F:81:3C:0F:01:AA:00:02|
  11:52:30.929957 Recv 0x|03:00|33:00|02|
  11:52:30.930941 Sent 0x|11:00|35:00|00|00:00|AE:00:02:05:0F:81:3C:0F:01:AA:00:02|
  11:52:32.089839 Recv 0x|03:00|35:00|02|
  11:52:32.091088 Sent 0x|11:00|38:00|00|00:00|AE:00:02:3B:0F:81:3C:0F:01:AA:00:02|
  11:52:33.220884 Recv 0x|03:00|38:00|02|
  11:52:33.221437 Sent 0x|11:00|39:00|00|00:00|AE:00:02:05:0F:81:3C:0F:01:AA:00:02|
  11:52:34.366040 Recv 0x|03:00|39:00|02|
  11:52:34.367271 Sent 0x|11:00|3C:00|00|00:00|AE:00:02:3B:0F:81:3C:0F:01:AA:00:02|
  11:52:35.536879 Recv 0x|03:00|3C:00|02|
  11:52:35.537949 Sent 0x|11:00|3E:00|00|00:00|AE:00:02:05:0F:81:3C:0F:01:AA:00:02|
  11:52:36.735035 Recv 0x|03:00|3E:00|02|
  11:52:36.735600 Sent 0x|11:00|3F:00|00|00:00|AE:00:02:3B:0F:81:3C:0F:01:AA:00:02|
  11:52:37.870978 Recv 0x|03:00|3F:00|02|
  11:52:38.071796 Sent 0x|09:00|43:00|80|00:00|A3:00:02:00|
      
The movement of the motor is the expected, but the song is not! The
movements last more than a second each and for this timespan, the EV3
brick is blocked because operation *opOutput_Ready* lets the EV3 brick
wait. If you look at the message counters, you find some gaps, where
direct commands of the sond were sent.

What we heave learned: *If the timing is done in the direct command,
this limits parallel execution.*


Exact Movements, not blocking
.............................

We modify the program and replace *opOutput_Ready* by *opOutput_Start*.
While the movement takes place, we ask frequently if it still is
in progress or has finished (done by *opOutput_Test*). This means more
data traffic, but none of the requests will block the EV3 brick. We
use these new operations:

*opOutput_Start* = 0x|A6|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)

  Starts the movement and does not wait until the movement has finished.

*opOutput_Test* = 0x|A9|

  Arguments
  
    - (Data8) LAYER: chain layer number
    - (Data8) NOS: port number (or a combination of port numbers)
  
  Returns
  
    - (Data8) BUSY: flag if motor is busy [0 = Ready, 1 = Busy]

  Tests if a motor is currently busy.

Connect your EV3 medium motor with port B, connect your computer via
Bluetooth with your EV3 brick, replace the MAC-address with the one of
your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  jukebox.song(ev3.FRERE_JACQUES).start()
  
  
  def reset():
      ops = b''.join((
          ev3.opOutput_Reset,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B)  # NOS
      ))
      my_ev3.send_direct_cmd(ops, sync_mode=ev3.SYNC)
  
  
  def step_speed(speed: int):
      ops_step_speed = b''.join((
          ev3.opOutput_Step_Speed,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.LCX(speed),  # SPEED
          ev3.LCX(15),  # STEP1
          ev3.LCX(60),  # STEP2
          ev3.LCX(15),  # STEP3
          ev3.LCX(1)  # BRAKE - yes
      ))
      ops_start = b''.join((
          ev3.opOutput_Start,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B)  # NOS
      ))
      my_ev3.send_direct_cmd(ops_step_speed + ops_start)
  
  
  def test():
      ops = b''.join((
          ev3.opOutput_Test,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.GVX(0)  # BUSY
      ))
      reply = my_ev3.send_direct_cmd(ops, global_mem=4)
      return struct.unpack('<i', reply)[0]
  
  
  def stop():
      ops = b''.join((
          ev3.opOutput_Stop,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.LCX(0)  # BRAKE - no
      ))
      my_ev3.send_direct_cmd(ops)
  
  
  speed = 5
  
  reset()
  for i in range(5):
      step_speed(speed)
      sleep(.2)
      while test():
          sleep(.2)
  
      step_speed(-speed)
      sleep(.2)
      while test():
          sleep(.2)
  
  sleep(.2)
  stop()
    
Some remarks:

  - *opOutput_Ready* has been replaced by *opOutput_Start*. This
    starts the movement, but does not wait for its end.
  - Instead of waiting, this program uses *opOutput_Test* to ask
    frequently, if the movement is still in progress.
  - If still your song is not played correctly, use protocols USB or
    Wifi instead of Bluetooth, because these are faster and speed
    helps to prevent conflicts.

The output:

.. code-block:: none

  12:21:08.851739 Sent 0x|08:00|2A:00|00|00:00|A2:00:02|
  12:21:08.903092 Recv 0x|03:00|2A:00|02|
  12:21:08.904440 Sent 0x|11:00|2D:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:21:09.105336 Sent 0x|09:00|2E:00|00|01:00|A9:00:02:60|
  12:21:09.174974 Recv 0x|04:00|2E:00|02|01|
  12:21:09.375951 Sent 0x|09:00|2F:00|00|01:00|A9:00:02:60|
  12:21:09.444917 Recv 0x|04:00|2F:00|02|01|
  12:21:09.645735 Sent 0x|09:00|31:00|00|01:00|A9:00:02:60|
  12:21:09.715081 Recv 0x|04:00|31:00|02|01|
  12:21:09.916029 Sent 0x|09:00|32:00|00|01:00|A9:00:02:60|
  12:21:09.991093 Recv 0x|04:00|32:00|02|01|
  12:21:10.191946 Sent 0x|09:00|34:00|00|01:00|A9:00:02:60|
  12:21:10.262916 Recv 0x|04:00|34:00|02|00|
  12:21:10.263476 Sent 0x|11:00|35:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:21:10.464500 Sent 0x|09:00|36:00|00|01:00|A9:00:02:60|
  12:21:10.535111 Recv 0x|04:00|36:00|02|01|
  12:21:10.736109 Sent 0x|09:00|38:00|00|01:00|A9:00:02:60|
  12:21:10.777892 Recv 0x|04:00|38:00|02|01|
  12:21:10.978716 Sent 0x|09:00|39:00|00|01:00|A9:00:02:60|
  12:21:11.044970 Recv 0x|04:00|39:00|02|01|
  12:21:11.245923 Sent 0x|09:00|3A:00|00|01:00|A9:00:02:60|
  12:21:11.303016 Recv 0x|04:00|3A:00|02|01|
  12:21:11.504236 Sent 0x|09:00|3D:00|00|01:00|A9:00:02:60|
  12:21:11.575097 Recv 0x|04:00|3D:00|02|00|
  12:21:11.575639 Sent 0x|11:00|3E:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:21:11.776573 Sent 0x|09:00|3F:00|00|01:00|A9:00:02:60|
  12:21:11.842046 Recv 0x|04:00|3F:00|02|01|
  12:21:12.043106 Sent 0x|09:00|41:00|00|01:00|A9:00:02:60|
  12:21:12.112103 Recv 0x|04:00|41:00|02|01|
  12:21:12.313026 Sent 0x|09:00|42:00|00|01:00|A9:00:02:60|
  12:21:12.375051 Recv 0x|04:00|42:00|02|01|
  12:21:12.575968 Sent 0x|09:00|44:00|00|01:00|A9:00:02:60|
  12:21:12.637077 Recv 0x|04:00|44:00|02|01|
  12:21:12.838115 Sent 0x|09:00|45:00|00|01:00|A9:00:02:60|
  12:21:12.908110 Recv 0x|04:00|45:00|02|00|
  12:21:12.908696 Sent 0x|11:00|46:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:21:13.109496 Sent 0x|09:00|48:00|00|01:00|A9:00:02:60|
  12:21:13.121873 Recv 0x|04:00|48:00|02|01|
  12:21:13.322848 Sent 0x|09:00|49:00|00|01:00|A9:00:02:60|
  12:21:13.402117 Recv 0x|04:00|49:00|02|01|
  12:21:13.603152 Sent 0x|09:00|4A:00|00|01:00|A9:00:02:60|
  12:21:13.657882 Recv 0x|04:00|4A:00|02|01|
  12:21:13.858904 Sent 0x|09:00|4D:00|00|01:00|A9:00:02:60|
  12:21:13.899888 Recv 0x|04:00|4D:00|02|01|
  12:21:14.100762 Sent 0x|09:00|4E:00|00|01:00|A9:00:02:60|
  12:21:14.144913 Recv 0x|04:00|4E:00|02|00|
  12:21:14.145297 Sent 0x|11:00|4F:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:21:14.346331 Sent 0x|09:00|51:00|00|01:00|A9:00:02:60|
  12:21:14.389892 Recv 0x|04:00|51:00|02|01|
  12:21:14.590822 Sent 0x|09:00|52:00|00|01:00|A9:00:02:60|
  12:21:14.657997 Recv 0x|04:00|52:00|02|01|
  12:21:14.858864 Sent 0x|09:00|54:00|00|01:00|A9:00:02:60|
  12:21:14.944139 Recv 0x|04:00|54:00|02|01|
  12:21:15.145073 Sent 0x|09:00|55:00|00|01:00|A9:00:02:60|
  12:21:15.206087 Recv 0x|04:00|55:00|02|01|
  12:21:15.407067 Sent 0x|09:00|56:00|00|01:00|A9:00:02:60|
  12:21:15.476913 Recv 0x|04:00|56:00|02|00|
  12:21:15.477296 Sent 0x|11:00|57:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:21:15.678152 Sent 0x|09:00|58:00|00|01:00|A9:00:02:60|
  12:21:15.746237 Recv 0x|04:00|58:00|02|01|
  12:21:15.947113 Sent 0x|09:00|59:00|00|01:00|A9:00:02:60|
  12:21:16.008946 Recv 0x|04:00|59:00|02|01|
  12:21:16.209772 Sent 0x|09:00|5C:00|00|01:00|A9:00:02:60|
  12:21:16.286122 Recv 0x|04:00|5C:00|02|01|
  12:21:16.488816 Sent 0x|09:00|5D:00|00|01:00|A9:00:02:60|
  12:21:16.611171 Recv 0x|04:00|5D:00|02|01|
  12:21:16.812098 Sent 0x|09:00|5F:00|00|01:00|A9:00:02:60|
  12:21:16.895091 Recv 0x|04:00|5F:00|02|00|
  12:21:16.895637 Sent 0x|11:00|60:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:21:17.096654 Sent 0x|09:00|61:00|00|01:00|A9:00:02:60|
  12:21:17.138906 Recv 0x|04:00|61:00|02|01|
  12:21:17.339764 Sent 0x|09:00|63:00|00|01:00|A9:00:02:60|
  12:21:17.400990 Recv 0x|04:00|63:00|02|01|
  12:21:17.601883 Sent 0x|09:00|64:00|00|01:00|A9:00:02:60|
  12:21:17.638926 Recv 0x|04:00|64:00|02|01|
  12:21:17.839940 Sent 0x|09:00|65:00|00|01:00|A9:00:02:60|
  12:21:17.910139 Recv 0x|04:00|65:00|02|01|
  12:21:18.111050 Sent 0x|09:00|66:00|00|01:00|A9:00:02:60|
  12:21:18.176911 Recv 0x|04:00|66:00|02|00|
  12:21:18.177386 Sent 0x|11:00|67:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:21:18.378438 Sent 0x|09:00|68:00|00|01:00|A9:00:02:60|
  12:21:18.454102 Recv 0x|04:00|68:00|02|01|
  12:21:18.655531 Sent 0x|09:00|6B:00|00|01:00|A9:00:02:60|
  12:21:18.699933 Recv 0x|04:00|6B:00|02|01|
  12:21:18.900855 Sent 0x|09:00|6C:00|00|01:00|A9:00:02:60|
  12:21:18.956985 Recv 0x|04:00|6C:00|02|01|
  12:21:19.158315 Sent 0x|09:00|6F:00|00|01:00|A9:00:02:60|
  12:21:19.205918 Recv 0x|04:00|6F:00|02|01|
  12:21:19.406850 Sent 0x|09:00|71:00|00|01:00|A9:00:02:60|
  12:21:19.455956 Recv 0x|04:00|71:00|02|00|
  12:21:19.456500 Sent 0x|11:00|72:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:21:19.657513 Sent 0x|09:00|73:00|00|01:00|A9:00:02:60|
  12:21:19.722027 Recv 0x|04:00|73:00|02|01|
  12:21:19.923390 Sent 0x|09:00|75:00|00|01:00|A9:00:02:60|
  12:21:19.961935 Recv 0x|04:00|75:00|02|01|
  12:21:20.162824 Sent 0x|09:00|76:00|00|01:00|A9:00:02:60|
  12:21:20.234139 Recv 0x|04:00|76:00|02|01|
  12:21:20.435034 Sent 0x|09:00|78:00|00|01:00|A9:00:02:60|
  12:21:20.480964 Recv 0x|04:00|78:00|02|01|
  12:21:20.681819 Sent 0x|09:00|79:00|00|01:00|A9:00:02:60|
  12:21:20.735111 Recv 0x|04:00|79:00|02|00|
  12:21:20.735661 Sent 0x|11:00|7A:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:21:20.936434 Sent 0x|09:00|7D:00|00|01:00|A9:00:02:60|
  12:21:20.985048 Recv 0x|04:00|7D:00|02|01|
  12:21:21.185991 Sent 0x|09:00|7E:00|00|01:00|A9:00:02:60|
  12:21:21.255167 Recv 0x|04:00|7E:00|02|01|
  12:21:21.456068 Sent 0x|09:00|80:00|00|01:00|A9:00:02:60|
  12:21:21.519136 Recv 0x|04:00|80:00|02|01|
  12:21:21.720515 Sent 0x|09:00|82:00|00|01:00|A9:00:02:60|
  12:21:21.780126 Recv 0x|04:00|82:00|02|01|
  12:21:21.981291 Sent 0x|09:00|84:00|00|01:00|A9:00:02:60|
  12:21:22.033996 Recv 0x|04:00|84:00|02|00|
  12:21:22.235006 Sent 0x|09:00|86:00|80|00:00|A3:00:02:00|
      
Some remarks:

  - Much more data traffic, but smooth and correct execution of
    movements, tones and LED lights.
  - All these direct commands block the EV3 brick only for a very short
    timespan, short enough to be not recognized.
  - As before, the message counters show gaps, where the direct
    commands of the song have been sent. But now, they were sent with
    a correct timing.

You can easily imagine, how adding some more motors or sensors will
complicate the code. Therefore it's good practice to separate the
tasks. Here the song has been separated as a `thread task
<https://thread-task.readthedocs.io/en/latest/>`_ object and we didn't
care about its internals.
    

Exact Movements as a Thread Task
................................

We modify this program once more and create a `thread task
<https://thread-task.readthedocs.io/en/latest/>`_ object for both, the
motor movement and the song, which can be started and
stopped. Encapsulating activities into thread task objects helps to
code applications of more and more parallel actions.

Connect your EV3 medium motor with port B, connect your computer via
Bluetooth with your EV3 brick, replace the MAC-address with the one of your
EV3 brick, then run this program:

.. code:: python3
  
  import ev3_dc as ev3
  import struct
  from thread_task import Task, Periodic, Repeated, Sleep
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  
  
  def reset():
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Reset,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_B)  # NOS
          )),
          sync_mode=ev3.SYNC
      )
  
  
  def step_speed(speed: int):
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Step_Speed,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_B),  # NOS
              ev3.LCX(speed),  # SPEED
              ev3.LCX(15),  # STEP1
              ev3.LCX(60),  # STEP2
              ev3.LCX(15),  # STEP3
              ev3.LCX(1),  # BRAKE - yes
              ev3.opOutput_Start,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_B)  # NOS
          ))
      )
  
  
  def test():
      ops = b''.join((
          ev3.opOutput_Test,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_B),  # NOS
          ev3.GVX(0)  # BUSY
      ))
      reply = my_ev3.send_direct_cmd(ops, global_mem=1)
      busy = struct.unpack('<b', reply)[0]
      return False if busy else True
  
  
  def stop():
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Stop,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_B),  # NOS
              ev3.LCX(0)  # BRAKE - no
          ))
      )
  
  
  speed = 5
  
  t_song = jukebox.song(ev3.FRERE_JACQUES)
  
  t_forwards = (
      Task(step_speed, args=(speed,), duration=.2) +
      Periodic(.2, test)
  )
  t_forwards.action_stop = stop
  
  t_backwards = (
      Task(step_speed, args=(-speed,), duration=.2) +
      Periodic(.2, test)
  )
  
  t = (
      Task(t_song.start) +
      Task(reset) +
      Repeated(
          t_forwards + t_backwards,
          num=5
      ) +
      Sleep(.2) +
      Task(stop)
  )
  
  t.start()
  
  sleep(8)
  t.stop()
  
Some remarks:

  - periodic ends, when its action returns True. This is why function
    :py:func:`test` returns the opposite of the expected.
  - Nearly all of the program is about creating t as a thread task
    object. Its execution is only the few lines at the end. You can
    easily imagine to hide the creation behind the public API of a
    class.
  - The parallel execution of motor movements and playing a song is handled inside of t.
  - Stopping is quite easy. The logic, how to stop the activities is
    hidden insite the thread task.
  - This thread task is not perfect because its continuation logic is not proper coded.

The output:

.. code-block:: none

  12:48:40.569302 Sent 0x|08:00|2A:00|00|00:00|A2:00:02|
  12:48:40.648679 Recv 0x|03:00|2A:00|02|
  12:48:40.649948 Sent 0x|11:00|2D:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:48:40.849774 Sent 0x|09:00|2E:00|00|01:00|A9:00:02:60|
  12:48:40.896519 Recv 0x|04:00|2E:00|02|01|
  12:48:41.050036 Sent 0x|09:00|2F:00|00|01:00|A9:00:02:60|
  12:48:41.098628 Recv 0x|04:00|2F:00|02|01|
  12:48:41.250406 Sent 0x|09:00|31:00|00|01:00|A9:00:02:60|
  12:48:41.318686 Recv 0x|04:00|31:00|02|01|
  12:48:41.450778 Sent 0x|09:00|32:00|00|01:00|A9:00:02:60|
  12:48:41.494671 Recv 0x|04:00|32:00|02|01|
  12:48:41.651188 Sent 0x|09:00|33:00|00|01:00|A9:00:02:60|
  12:48:41.703649 Recv 0x|04:00|33:00|02|01|
  12:48:41.851603 Sent 0x|09:00|35:00|00|01:00|A9:00:02:60|
  12:48:41.943683 Recv 0x|04:00|35:00|02|00|
  12:48:41.944486 Sent 0x|11:00|36:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:48:42.144719 Sent 0x|09:00|37:00|00|01:00|A9:00:02:60|
  12:48:42.211513 Recv 0x|04:00|37:00|02|01|
  12:48:42.344999 Sent 0x|09:00|38:00|00|01:00|A9:00:02:60|
  12:48:42.385481 Recv 0x|04:00|38:00|02|01|
  12:48:42.545455 Sent 0x|09:00|3A:00|00|01:00|A9:00:02:60|
  12:48:42.598677 Recv 0x|04:00|3A:00|02|01|
  12:48:42.745691 Sent 0x|09:00|3B:00|00|01:00|A9:00:02:60|
  12:48:42.799659 Recv 0x|04:00|3B:00|02|01|
  12:48:42.946066 Sent 0x|09:00|3C:00|00|01:00|A9:00:02:60|
  12:48:43.031706 Recv 0x|04:00|3C:00|02|01|
  12:48:43.146600 Sent 0x|09:00|3F:00|00|01:00|A9:00:02:60|
  12:48:43.207665 Recv 0x|04:00|3F:00|02|00|
  12:48:43.208658 Sent 0x|11:00|40:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:48:43.409048 Sent 0x|09:00|41:00|00|01:00|A9:00:02:60|
  12:48:43.482677 Recv 0x|04:00|41:00|02|01|
  12:48:43.609350 Sent 0x|09:00|43:00|00|01:00|A9:00:02:60|
  12:48:43.659614 Recv 0x|04:00|43:00|02|01|
  12:48:43.809783 Sent 0x|09:00|44:00|00|01:00|A9:00:02:60|
  12:48:43.867547 Recv 0x|04:00|44:00|02|01|
  12:48:44.009999 Sent 0x|09:00|45:00|00|01:00|A9:00:02:60|
  12:48:44.067605 Recv 0x|04:00|45:00|02|01|
  12:48:44.210310 Sent 0x|09:00|47:00|00|01:00|A9:00:02:60|
  12:48:44.295689 Recv 0x|04:00|47:00|02|01|
  12:48:44.410610 Sent 0x|09:00|48:00|00|01:00|A9:00:02:60|
  12:48:44.472626 Recv 0x|04:00|48:00|02|00|
  12:48:44.473215 Sent 0x|11:00|49:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:48:44.673718 Sent 0x|09:00|4A:00|00|01:00|A9:00:02:60|
  12:48:44.773517 Recv 0x|04:00|4A:00|02|01|
  12:48:44.874162 Sent 0x|09:00|4C:00|00|01:00|A9:00:02:60|
  12:48:44.950694 Recv 0x|04:00|4C:00|02|01|
  12:48:45.074450 Sent 0x|09:00|4D:00|00|01:00|A9:00:02:60|
  12:48:45.124658 Recv 0x|04:00|4D:00|02|01|
  12:48:45.274793 Sent 0x|09:00|4E:00|00|01:00|A9:00:02:60|
  12:48:45.322584 Recv 0x|04:00|4E:00|02|01|
  12:48:45.475099 Sent 0x|09:00|51:00|00|01:00|A9:00:02:60|
  12:48:45.528592 Recv 0x|04:00|51:00|02|01|
  12:48:45.675549 Sent 0x|09:00|52:00|00|01:00|A9:00:02:60|
  12:48:45.732762 Recv 0x|04:00|52:00|02|00|
  12:48:45.733656 Sent 0x|11:00|53:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:48:45.934072 Sent 0x|09:00|54:00|00|01:00|A9:00:02:60|
  12:48:45.985610 Recv 0x|04:00|54:00|02|01|
  12:48:46.134651 Sent 0x|09:00|56:00|00|01:00|A9:00:02:60|
  12:48:46.183608 Recv 0x|04:00|56:00|02|01|
  12:48:46.334950 Sent 0x|09:00|57:00|00|01:00|A9:00:02:60|
  12:48:46.399693 Recv 0x|04:00|57:00|02|01|
  12:48:46.535293 Sent 0x|09:00|58:00|00|01:00|A9:00:02:60|
  12:48:46.579582 Recv 0x|04:00|58:00|02|01|
  12:48:46.735896 Sent 0x|09:00|5A:00|00|01:00|A9:00:02:60|
  12:48:46.788654 Recv 0x|04:00|5A:00|02|01|
  12:48:46.936190 Sent 0x|09:00|5B:00|00|01:00|A9:00:02:60|
  12:48:46.992702 Recv 0x|04:00|5B:00|02|00|
  12:48:46.993371 Sent 0x|11:00|5C:00|80|00:00|AE:00:02:3B:0F:81:3C:0F:01:A6:00:02|
  12:48:47.193783 Sent 0x|09:00|5D:00|00|01:00|A9:00:02:60|
  12:48:47.263712 Recv 0x|04:00|5D:00|02|01|
  12:48:47.394209 Sent 0x|09:00|5E:00|00|01:00|A9:00:02:60|
  12:48:47.439528 Recv 0x|04:00|5E:00|02|01|
  12:48:47.594571 Sent 0x|09:00|5F:00|00|01:00|A9:00:02:60|
  12:48:47.652589 Recv 0x|04:00|5F:00|02|01|
  12:48:47.794863 Sent 0x|09:00|62:00|00|01:00|A9:00:02:60|
  12:48:47.874742 Recv 0x|04:00|62:00|02|01|
  12:48:47.995327 Sent 0x|09:00|63:00|00|01:00|A9:00:02:60|
  12:48:48.067742 Recv 0x|04:00|63:00|02|01|
  12:48:48.195556 Sent 0x|09:00|64:00|00|01:00|A9:00:02:60|
  12:48:48.242525 Recv 0x|04:00|64:00|02|00|
  12:48:48.243357 Sent 0x|11:00|65:00|80|00:00|AE:00:02:05:0F:81:3C:0F:01:A6:00:02|
  12:48:48.443723 Sent 0x|09:00|67:00|00|01:00|A9:00:02:60|
  12:48:48.498720 Recv 0x|04:00|67:00|02|01|
  12:48:48.578092 Sent 0x|09:00|6A:00|80|00:00|A3:00:02:00|
    
Some remarks:

  - Until the interruption, the direct commands were the same as
    before.
  - The stopping occured during the seventh movement.
  - The last direct command stopped the motor. This is what
    *t_forwards.action_stop = stop* meant.

    
Moving a motor to a Specified Position
......................................

Connect your EV3 medium motor with port B, connect your computer and
your EV3 brick with an USB cable, replace the MAC-address with the one of your
EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  from math import copysign
  
  
  my_ev3 = ev3.EV3(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_ev3.verbosity = 1
  
  speed = 10
  to_position = 90
  port = ev3.PORT_B
  brake = 0
  
  ops1 = b''.join((
      ev3.opInput_Device,
      ev3.READY_SI,
      ev3.LCX(0),  # LAYER
      ev3.port_motor_input(port),  # NO
      ev3.LCX(8),  # TYPE (EV3-Medium-Motor)
      ev3.LCX(0),  # MODE (Degree)
      ev3.LCX(1),  # VALUES
      ev3.GVX(0)  # VALUE1
  ))
  reply = my_ev3.send_direct_cmd(ops1, global_mem=4)
  from_position = struct.unpack('<f', reply)[0]
  
  diff = to_position - round(from_position)
  speed *= round(copysign(1, diff))
  steps = abs(diff)
  
  ops2 = b''.join((
      ev3.opOutput_Reset,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port),  # NOS
      
      ev3.opOutput_Step_Speed,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port),  # NOS
      ev3.LCX(speed),  # SPEED
      ev3.LCX(0),  # STEP1
      ev3.LCX(steps),  # STEP2
      ev3.LCX(0),  # STEP3
      ev3.LCX(brake),  # BRAKE - 1 (yes) or 0 (no)
      
      ev3.opOutput_Start,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port)  # NOS
  ))
  my_ev3.send_direct_cmd(ops2)

Please move the motor by hand and then run the program again. The
motor will return to the defined position of 90 degrees. We use 4
already known operations and it's obvious, that this algorithm can
easily be encapsulated into a method of a motor class.

The output:

.. code-block:: none

  13:19:05.149392 Sent 0x|0D:00|2A:00|00|04:00|99:1D:00:11:07:00:01:60|
  13:19:05.155311 Recv 0x|07:00|2A:00|02|00:00:04:C2|
  13:19:05.155969 Sent 0x|14:00|2B:00|00|00:00|A2:00:02:AE:00:02:0A:00:81:7B:00:00:A6:00:02|
  13:19:05.161331 Recv 0x|03:00|2B:00|02|
  


Direct Commands are Machine Code Programs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
There are operations for calculations and much more. Direct commands
are little machine code programs. Let's write a single direct command,
that does the same thing.

.. code:: python3

  import ev3_dc as ev3
  
  
  my_ev3 = ev3.EV3(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99'
  )
  my_ev3.verbosity = 1
  
  speed = 10
  to_position = 90
  port = ev3.PORT_B
  brake = 0
  
  ops = b''.join((
      ev3.opInput_Device,
      ev3.READY_SI,
      ev3.LCX(0),  # LAYER
      ev3.port_motor_input(port),  # NO
      ev3.LCX(8),  # TYPE (EV3-Medium-Motor)
      ev3.LCX(0),  # MODE (Degree)
      ev3.LCX(1),  # VALUES
      ev3.LVX(0),  # VALUE1 - from_position (DATAF)
  
      ev3.opMove32_F,
      ev3.LCX(to_position),  # SOURCE
      ev3.LVX(4),  # DESTINATION - to_position (DATAF)
      
      ev3.opSubF,
      ev3.LVX(4),  # SOURCE1 - to_position (DATAF)
      ev3.LVX(0),  # SOURCE2 - from_position (DATAF)
      ev3.LVX(0),  # DESTINATION - diff (DATAF)
      
      ev3.opMath,
      ev3.ABS,  # CMD
      ev3.LVX(0),  # DATA X - diff (DATAF)
      ev3.LVX(4),  # RESULT - abs(diff) (DATAF)
      
      ev3.opDivF,
      ev3.LVX(0),  # SOURCE1 - diff (DATAF)
      ev3.LVX(4),  # SOURCE2 - abs(diff) (DATAF)
      ev3.LVX(0),  # DESTINATION - sign of diff (DATAF)
      
      ev3.opMove32_F,
      ev3.LCX(speed),  # SOURCE
      ev3.LVX(8),  # DESTINATION - speed (DATAF)
      
      ev3.opMulF,
      ev3.LVX(0),  # SOURCE1 - sign of diff (DATAF)
      ev3.LVX(8),  # SOURCE2 - speed (DATAF)
      ev3.LVX(0),  # DESTINATION - signed_speed (DATAF)
      
      ev3.opMoveF_32,
      ev3.LVX(4),  # SOURCE - abs(diff) (DATAF)
      ev3.LVX(4),  # DESTINATION - abs(diff) (DATA32)
      
      ev3.opMoveF_8,
      ev3.LVX(0),  # SOURCE - signed_speed (DATAF)
      ev3.LVX(0),  # DESTINATION - signed_speed (DATA8)
      
      ev3.opOutput_Reset,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port),  # NOS
      
      ev3.opOutput_Step_Speed,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port),  # NOS
      ev3.LVX(0),  # SPEED - signed_speed (DATA8)
      ev3.LCX(0),  # STEP1
      ev3.LVX(4),  # STEP2 - abs(diff) (DATA32)
      ev3.LCX(0),  # STEP3
      ev3.LCX(brake),  # BRAKE - 1 (yes) or 0 (no)
      
      ev3.opOutput_Start,
      ev3.LCX(0),  # LAYER
      ev3.LCX(port)  # NOS
  ))
  my_ev3.send_direct_cmd(ops, local_mem=12)

Some remarks:

  - This direct command allocates 12 bytes of local memory for its
    intermediate results. Most of these are 4-bytes-numbers, therefore
    the referenced addresses are LVX(0), LVX(4) and LVX(8).
    
  - We need to be carefull with the data formats, here we use numbers
    in three formats:
    
    - *DATA8* (1 byte integer),
    - *DATA32* (4 bytes integer) and
    - *DATAF* (4 bytes floating point).
      
  - We have to translate some of the formats:

    - *opMove32_F* translates a 4 bytes integer into a floating point
      number,
    - *opMoveF_32* does the opposite,
    - *opMoveF_8* translates a floating point number into a 1 byte
      integer.
    
  - We do the calculations with floating point numbers and use:

    - *opDivF* for division,
    - *opMulF* for multiplication and
    - *opMath* with CMD *ABS* to get the absolute value of a floating point number.
      
That's machine code, welcome to the sixties! Think a minute about
coding complex algorithms this way and realize what the apollo program
meant for the software developers in these times. But keep in mind,
coding machine code is great for performance. Here the communication
is reduced from 2 direct commands to one. In case of protocol *USB*,
this means some 0.05 sec.
            
