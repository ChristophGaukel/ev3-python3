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


Exact movements block the EV3 brick
...................................

Connect your EV3 medium motor with port C, connect your computer via
Bluetooth with your EV3 brick, replace the MAC-address with the one of
your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  jukebox.song(ev3.FRERE_JACQUES).start()
  
  
  def prepare():
      ops = b''.join((
          ev3.opOutput_Set_Type,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(8),  # TYPE - Medium motor
          ev3.opOutput_Reset,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C)  # NOS
      ))
      my_ev3.send_direct_cmd(ops, sync_mode=ev3.SYNC)
  
  
  def step_speed(speed: int):
      ops_step_speed = b''.join((
          ev3.opOutput_Step_Speed,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(speed),  # SPEED
          ev3.LCX(15),  # STEP1
          ev3.LCX(60),  # STEP2
          ev3.LCX(15),  # STEP3
          ev3.LCX(1)  # BRAKE - yes
      ))
      ops_ready = b''.join((
          ev3.opOutput_Ready,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C)  # NOS
      ))
      my_ev3.send_direct_cmd(ops_step_speed + ops_ready, sync_mode=ev3.SYNC)
  
  
  def stop():
      ops = b''.join((
          ev3.opOutput_Stop,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(0)  # BRAKE - no
      ))
      my_ev3.send_direct_cmd(ops)
  
  
  speed = 5
  
  prepare()
  for i in range(5):
      step_speed(speed)
      step_speed(-speed)
  
  sleep(.2)
  stop()
  
Some remarks:

  - Function :py:func:`prepare` sets the type of port C and resets
    the tacho counter of this port.
  - Function :py:func:`step_speed` does a 90 ° smooth movement of the
    medium motor. Dependent from the sign of SPEED the movement is
    forwards or backwards. The three numbers STEP1, STEP2 and
    STEP3 define the lengths of the acceleration, the constant speed
    and the deceleration phase, all of them in degrees. The movement
    ends with an active break, which holds the motor in a defined
    position.
  - Operation *opOutput_Ready* waits until the current movement
    (here the *opOutput_Step_Speed* operation) has finished.
  - Function :py:func:`stop` releases the brake. This is done 0.2 sec.
    after the last movement has finished.
  - There are 10 slow and smooth movements of the motor, 5 times
    forwards and backwards. If you fix an infrared sensor on top of
    the shaft, this looks like headshaking. Changing the speed will
    change the character of the headshaking.
  - Setting *sync_mode=SYNC* allows to get the reply after a movement
    has finished.
  - The program plays the song *Frère Jacques* parallel to the motor
    movement.
  - Using two classes *EV3* and *Jukebox* is not necessary. *Jukebox*
    as a subclass of *EV3* would have done the job alone. But this
    example demonstrates, how specialized subclasses of *EV3* can
    handle specific tasks, like *Jukebox* handles sound. And multiple
    subclasses of *EV3* can work together.

The output:

.. code-block:: none

  13:03:36.605872 Sent 0x|0C:00|2A:00|00|00:00|A1:00:04:08:A2:00:04|
  13:03:36.647234 Recv 0x|03:00|2A:00|02|
  13:03:36.648280 Sent 0x|11:00|2D:00|00|00:00|AE:00:04:05:0F:81:3C:0F:01:AA:00:04|
  13:03:37.814215 Recv 0x|03:00|2D:00|02|
  13:03:37.814766 Sent 0x|11:00|2E:00|00|00:00|AE:00:04:3B:0F:81:3C:0F:01:AA:00:04|
  13:03:38.923317 Recv 0x|03:00|2E:00|02|
  13:03:38.923914 Sent 0x|11:00|2F:00|00|00:00|AE:00:04:05:0F:81:3C:0F:01:AA:00:04|
  13:03:40.034365 Recv 0x|03:00|2F:00|02|
  13:03:40.035664 Sent 0x|11:00|32:00|00|00:00|AE:00:04:3B:0F:81:3C:0F:01:AA:00:04|
  13:03:41.124354 Recv 0x|03:00|32:00|02|
  13:03:41.125463 Sent 0x|11:00|34:00|00|00:00|AE:00:04:05:0F:81:3C:0F:01:AA:00:04|
  13:03:42.214335 Recv 0x|03:00|34:00|02|
  13:03:42.215478 Sent 0x|11:00|37:00|00|00:00|AE:00:04:3B:0F:81:3C:0F:01:AA:00:04|
  13:03:43.309308 Recv 0x|03:00|37:00|02|
  13:03:43.310457 Sent 0x|11:00|39:00|00|00:00|AE:00:04:05:0F:81:3C:0F:01:AA:00:04|
  13:03:44.427281 Recv 0x|03:00|39:00|02|
  13:03:44.427894 Sent 0x|11:00|3A:00|00|00:00|AE:00:04:3B:0F:81:3C:0F:01:AA:00:04|
  13:03:45.505264 Recv 0x|03:00|3A:00|02|
  13:03:45.506624 Sent 0x|11:00|3E:00|00|00:00|AE:00:04:05:0F:81:3C:0F:01:AA:00:04|
  13:03:46.601250 Recv 0x|03:00|3E:00|02|
  13:03:46.601816 Sent 0x|11:00|3F:00|00|00:00|AE:00:04:3B:0F:81:3C:0F:01:AA:00:04|
  13:03:47.686069 Recv 0x|03:00|3F:00|02|
  13:03:47.886976 Sent 0x|09:00|43:00|80|00:00|A3:00:04:00|
    
The movement of the motor is the expected, but the song is not! The
movements last more than a second each and for this timespan, the EV3
brick is blocked because operation *opOutput_Ready* lets the EV3 brick
wait.

What we heave learned: *If the timing is done in the direct command,
this limits parallel execution.*


Exact Movements, not blocking
.............................

We modify the program, instead of using *opOutput_Ready*, we use
*opOutput_Start* and we ask frequently if the movement still is in
progress or has finished. This means more data traffic, but none of
the requests blocks the EV3 brick.

Connect your EV3 medium motor with port C, connect your computer via
Wifi with your EV3 brick, replace the MAC-address with the one of
your EV3 brick, then run this program:

.. code:: python3

  import ev3_dc as ev3
  import struct
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  jukebox.song(ev3.FRERE_JACQUES).start()
  
  
  def prepare():
      ops = b''.join((
          ev3.opOutput_Set_Type,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(8),  # TYPE - Medium motor
          ev3.opOutput_Reset,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C)  # NOS
      ))
      my_ev3.send_direct_cmd(ops, sync_mode=ev3.SYNC)
  
  
  def step_speed(speed: int):
      ops_step_speed = b''.join((
          ev3.opOutput_Step_Speed,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(speed),  # SPEED
          ev3.LCX(15),  # STEP1
          ev3.LCX(60),  # STEP2
          ev3.LCX(15),  # STEP3
          ev3.LCX(1)  # BRAKE - yes
      ))
      ops_start = b''.join((
          ev3.opOutput_Start,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C)  # NOS
      ))
      my_ev3.send_direct_cmd(ops_step_speed + ops_start)
  
  
  def test():
      ops = b''.join((
          ev3.opOutput_Test,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.GVX(0)  # BUSY
      ))
      reply = my_ev3.send_direct_cmd(ops, global_mem=4)
      return struct.unpack('<i', reply)[0]
  
  
  def stop():
      ops = b''.join((
          ev3.opOutput_Stop,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.LCX(0)  # BRAKE - no
      ))
      my_ev3.send_direct_cmd(ops)
  
  
  speed = 5
  
  prepare()
  for i in range(5):
      step_speed(speed)
      while test():
          sleep(.2)
  
      step_speed(-speed)
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

  13:07:55.041998 Sent 0x|0C:00|2A:00|00|00:00|A1:00:04:08:A2:00:04|
  13:07:55.113310 Recv 0x|03:00|2A:00|02|
  13:07:55.113883 Sent 0x|11:00|2B:00|80|00:00|AE:00:04:05:0F:81:3C:0F:01:A6:00:04|
  13:07:55.114853 Sent 0x|09:00|2E:00|00|04:00|A9:00:04:60|
  13:07:55.153222 Recv 0x|07:00|2E:00|02|01:00:00:00|
  13:07:55.354035 Sent 0x|09:00|2F:00|00|04:00|A9:00:04:60|
  13:07:55.398233 Recv 0x|07:00|2F:00|02|01:00:00:00|
  13:07:55.599135 Sent 0x|09:00|30:00|00|04:00|A9:00:04:60|
  13:07:55.636234 Recv 0x|07:00|30:00|02|01:00:00:00|
  13:07:55.837061 Sent 0x|09:00|32:00|00|04:00|A9:00:04:60|
  13:07:55.872174 Recv 0x|07:00|32:00|02|01:00:00:00|
  13:07:56.072891 Sent 0x|09:00|33:00|00|04:00|A9:00:04:60|
  13:07:56.113274 Recv 0x|07:00|33:00|02|01:00:00:00|
  13:07:56.314191 Sent 0x|09:00|35:00|00|04:00|A9:00:04:60|
  13:07:56.351244 Recv 0x|07:00|35:00|02|00:00:00:00|
  13:07:56.351700 Sent 0x|11:00|36:00|80|00:00|AE:00:04:3B:0F:81:3C:0F:01:A6:00:04|
  13:07:56.352497 Sent 0x|09:00|37:00|00|04:00|A9:00:04:60|
  13:07:56.388243 Recv 0x|07:00|37:00|02|01:00:00:00|
  13:07:56.589178 Sent 0x|09:00|38:00|00|04:00|A9:00:04:60|
  13:07:56.626238 Recv 0x|07:00|38:00|02|01:00:00:00|
  13:07:56.827141 Sent 0x|09:00|39:00|00|04:00|A9:00:04:60|
  13:07:56.889289 Recv 0x|07:00|39:00|02|01:00:00:00|
  13:07:57.090144 Sent 0x|09:00|3B:00|00|04:00|A9:00:04:60|
  13:07:57.136205 Recv 0x|07:00|3B:00|02|01:00:00:00|
  13:07:57.337015 Sent 0x|09:00|3C:00|00|04:00|A9:00:04:60|
  13:07:57.397386 Recv 0x|07:00|3C:00|02|01:00:00:00|
  13:07:57.598350 Sent 0x|09:00|3F:00|00|04:00|A9:00:04:60|
  13:07:57.654115 Recv 0x|07:00|3F:00|02|00:00:00:00|
  13:07:57.654501 Sent 0x|11:00|40:00|80|00:00|AE:00:04:05:0F:81:3C:0F:01:A6:00:04|
  13:07:57.654757 Sent 0x|09:00|41:00|00|04:00|A9:00:04:60|
  13:07:57.748313 Recv 0x|07:00|41:00|02|01:00:00:00|
  13:07:57.949263 Sent 0x|09:00|42:00|00|04:00|A9:00:04:60|
  13:07:58.031262 Recv 0x|07:00|42:00|02|01:00:00:00|
  13:07:58.232120 Sent 0x|09:00|44:00|00|04:00|A9:00:04:60|
  13:07:58.284231 Recv 0x|07:00|44:00|02|01:00:00:00|
  13:07:58.488698 Sent 0x|09:00|45:00|00|04:00|A9:00:04:60|
  13:07:58.529164 Recv 0x|07:00|45:00|02|01:00:00:00|
  13:07:58.730003 Sent 0x|09:00|47:00|00|04:00|A9:00:04:60|
  13:07:58.768157 Recv 0x|07:00|47:00|02|01:00:00:00|
  13:07:58.969070 Sent 0x|09:00|48:00|00|04:00|A9:00:04:60|
  13:07:59.006252 Recv 0x|07:00|48:00|02|00:00:00:00|
  13:07:59.006638 Sent 0x|11:00|49:00|80|00:00|AE:00:04:3B:0F:81:3C:0F:01:A6:00:04|
  13:07:59.006928 Sent 0x|09:00|4A:00|00|04:00|A9:00:04:60|
  13:07:59.042180 Recv 0x|07:00|4A:00|02|01:00:00:00|
  13:07:59.243014 Sent 0x|09:00|4B:00|00|04:00|A9:00:04:60|
  13:07:59.281222 Recv 0x|07:00|4B:00|02|01:00:00:00|
  13:07:59.482081 Sent 0x|09:00|4D:00|00|04:00|A9:00:04:60|
  13:07:59.561269 Recv 0x|07:00|4D:00|02|01:00:00:00|
  13:07:59.762133 Sent 0x|09:00|4E:00|00|04:00|A9:00:04:60|
  13:07:59.801158 Recv 0x|07:00|4E:00|02|01:00:00:00|
  13:08:00.001978 Sent 0x|09:00|51:00|00|04:00|A9:00:04:60|
  13:08:00.062103 Recv 0x|07:00|51:00|02|01:00:00:00|
  13:08:00.262997 Sent 0x|09:00|52:00|00|04:00|A9:00:04:60|
  13:08:00.316139 Recv 0x|07:00|52:00|02|00:00:00:00|
  13:08:00.316578 Sent 0x|11:00|53:00|80|00:00|AE:00:04:05:0F:81:3C:0F:01:A6:00:04|
  13:08:00.316844 Sent 0x|09:00|54:00|00|04:00|A9:00:04:60|
  13:08:00.382341 Recv 0x|07:00|54:00|02|01:00:00:00|
  13:08:00.583257 Sent 0x|09:00|56:00|00|04:00|A9:00:04:60|
  13:08:00.676297 Recv 0x|07:00|56:00|02|01:00:00:00|
  13:08:00.877230 Sent 0x|09:00|57:00|00|04:00|A9:00:04:60|
  13:08:00.925141 Recv 0x|07:00|57:00|02|01:00:00:00|
  13:08:01.126119 Sent 0x|09:00|59:00|00|04:00|A9:00:04:60|
  13:08:01.162266 Recv 0x|07:00|59:00|02|01:00:00:00|
  13:08:01.363105 Sent 0x|09:00|5A:00|00|04:00|A9:00:04:60|
  13:08:01.400151 Recv 0x|07:00|5A:00|02|01:00:00:00|
  13:08:01.601098 Sent 0x|09:00|5B:00|00|04:00|A9:00:04:60|
  13:08:01.645123 Recv 0x|07:00|5B:00|02|00:00:00:00|
  13:08:01.645677 Sent 0x|11:00|5C:00|80|00:00|AE:00:04:3B:0F:81:3C:0F:01:A6:00:04|
  13:08:01.646127 Sent 0x|09:00|5D:00|00|04:00|A9:00:04:60|
  13:08:01.682154 Recv 0x|07:00|5D:00|02|01:00:00:00|
  13:08:01.883141 Sent 0x|09:00|5E:00|00|04:00|A9:00:04:60|
  13:08:01.920102 Recv 0x|07:00|5E:00|02|01:00:00:00|
  13:08:02.120889 Sent 0x|09:00|5F:00|00|04:00|A9:00:04:60|
  13:08:02.160165 Recv 0x|07:00|5F:00|02|01:00:00:00|
  13:08:02.360915 Sent 0x|09:00|62:00|00|04:00|A9:00:04:60|
  13:08:02.397189 Recv 0x|07:00|62:00|02|01:00:00:00|
  13:08:02.597976 Sent 0x|09:00|63:00|00|04:00|A9:00:04:60|
  13:08:02.660192 Recv 0x|07:00|63:00|02|01:00:00:00|
  13:08:02.861155 Sent 0x|09:00|65:00|00|04:00|A9:00:04:60|
  13:08:02.898085 Recv 0x|07:00|65:00|02|00:00:00:00|
  13:08:02.898633 Sent 0x|11:00|66:00|80|00:00|AE:00:04:05:0F:81:3C:0F:01:A6:00:04|
  13:08:02.899055 Sent 0x|09:00|67:00|00|04:00|A9:00:04:60|
  13:08:02.935094 Recv 0x|07:00|67:00|02|01:00:00:00|
  13:08:03.136089 Sent 0x|09:00|68:00|00|04:00|A9:00:04:60|
  13:08:03.172185 Recv 0x|07:00|68:00|02|01:00:00:00|
  13:08:03.372951 Sent 0x|09:00|69:00|00|04:00|A9:00:04:60|
  13:08:03.410162 Recv 0x|07:00|69:00|02|01:00:00:00|
  13:08:03.611147 Sent 0x|09:00|6B:00|00|04:00|A9:00:04:60|
  13:08:03.648133 Recv 0x|07:00|6B:00|02|01:00:00:00|
  13:08:03.849032 Sent 0x|09:00|6C:00|00|04:00|A9:00:04:60|
  13:08:03.896073 Recv 0x|07:00|6C:00|02|01:00:00:00|
  13:08:04.096970 Sent 0x|09:00|6D:00|00|04:00|A9:00:04:60|
  13:08:04.133113 Recv 0x|07:00|6D:00|02|00:00:00:00|
  13:08:04.133566 Sent 0x|11:00|6E:00|80|00:00|AE:00:04:3B:0F:81:3C:0F:01:A6:00:04|
  13:08:04.133903 Sent 0x|09:00|6F:00|00|04:00|A9:00:04:60|
  13:08:04.170198 Recv 0x|07:00|6F:00|02|01:00:00:00|
  13:08:04.371073 Sent 0x|09:00|70:00|00|04:00|A9:00:04:60|
  13:08:04.432159 Recv 0x|07:00|70:00|02|01:00:00:00|
  13:08:04.632976 Sent 0x|09:00|71:00|00|04:00|A9:00:04:60|
  13:08:04.682204 Recv 0x|07:00|71:00|02|01:00:00:00|
  13:08:04.883438 Sent 0x|09:00|74:00|00|04:00|A9:00:04:60|
  13:08:04.921126 Recv 0x|07:00|74:00|02|01:00:00:00|
  13:08:05.121975 Sent 0x|09:00|76:00|00|04:00|A9:00:04:60|
  13:08:05.158072 Recv 0x|07:00|76:00|02|01:00:00:00|
  13:08:05.359032 Sent 0x|09:00|78:00|00|04:00|A9:00:04:60|
  13:08:05.421040 Recv 0x|07:00|78:00|02|00:00:00:00|
  13:08:05.421427 Sent 0x|11:00|79:00|80|00:00|AE:00:04:05:0F:81:3C:0F:01:A6:00:04|
  13:08:05.421685 Sent 0x|09:00|7A:00|00|04:00|A9:00:04:60|
  13:08:05.457028 Recv 0x|07:00|7A:00|02|01:00:00:00|
  13:08:05.657988 Sent 0x|09:00|7C:00|00|04:00|A9:00:04:60|
  13:08:05.693119 Recv 0x|07:00|7C:00|02|01:00:00:00|
  13:08:05.894086 Sent 0x|09:00|7E:00|00|04:00|A9:00:04:60|
  13:08:05.931054 Recv 0x|07:00|7E:00|02|01:00:00:00|
  13:08:06.132000 Sent 0x|09:00|7F:00|00|04:00|A9:00:04:60|
  13:08:06.168059 Recv 0x|07:00|7F:00|02|01:00:00:00|
  13:08:06.369037 Sent 0x|09:00|80:00|00|04:00|A9:00:04:60|
  13:08:06.431267 Recv 0x|07:00|80:00|02|01:00:00:00|
  13:08:06.632150 Sent 0x|09:00|82:00|00|04:00|A9:00:04:60|
  13:08:06.667121 Recv 0x|07:00|82:00|02|00:00:00:00|
  13:08:06.667692 Sent 0x|11:00|83:00|80|00:00|AE:00:04:3B:0F:81:3C:0F:01:A6:00:04|
  13:08:06.668142 Sent 0x|09:00|84:00|00|04:00|A9:00:04:60|
  13:08:06.705128 Recv 0x|07:00|84:00|02|01:00:00:00|
  13:08:06.906077 Sent 0x|09:00|85:00|00|04:00|A9:00:04:60|
  13:08:06.942083 Recv 0x|07:00|85:00|02|01:00:00:00|
  13:08:07.142931 Sent 0x|09:00|88:00|00|04:00|A9:00:04:60|
  13:08:07.180151 Recv 0x|07:00|88:00|02|01:00:00:00|
  13:08:07.381093 Sent 0x|09:00|89:00|00|04:00|A9:00:04:60|
  13:08:07.417028 Recv 0x|07:00|89:00|02|01:00:00:00|
  13:08:07.617959 Sent 0x|09:00|8B:00|00|04:00|A9:00:04:60|
  13:08:07.655037 Recv 0x|07:00|8B:00|02|01:00:00:00|
  13:08:07.856157 Sent 0x|09:00|8D:00|00|04:00|A9:00:04:60|
  13:08:07.892093 Recv 0x|07:00|8D:00|02|00:00:00:00|
  13:08:08.093030 Sent 0x|09:00|8F:00|80|00:00|A3:00:04:00|
  
Some remarks:

  - Much more data traffic, but smooth and correct execution of
    movements, tones and LED lights.
  - All the direct commands block the EV3 brick only for a very short
    timespan, short enough to be not recognized.
  - The message counters show gaps, where the direct commands
    of the song have been sent.

You can easily imagine, how adding some movements of the whole robot
will complicate the code. Therefore it's good practice to separate the
the tasks. Here the song has been separated as a `thread task
<https://thread-task.readthedocs.io/en/latest/>`_ object and we didn't
need to care about its internals.
    

Exact Movements as a Thread Task
................................

We modify this program once more and create a `thread task
<https://thread-task.readthedocs.io/en/latest/>`_ object, which can be
started and stopped. This will play the song and move the motor. Doing
so helps to build applications of more and more parallel activities.

Connect your EV3 medium motor with port C, connect your computer via
Wifi with your EV3 brick, replace the MAC-address with the one of your
EV3 brick, then run this program:

.. code:: python3
  
  import ev3_dc as ev3
  import struct
  from thread_task import Task, Periodic, Repeated
  from time import sleep
  
  
  my_ev3 = ev3.EV3(protocol=ev3.WIFI, host='00:16:53:42:2B:99')
  my_ev3.verbosity = 1
  
  jukebox = ev3.Jukebox(ev3_obj=my_ev3)
  
  
  def prepare():
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Set_Type,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_C),  # NOS
              ev3.LCX(8),  # TYPE - Medium motor
              ev3.opOutput_Reset,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_C)  # NOS
          )),
          sync_mode=ev3.SYNC
      )
  
  
  def step_speed(speed: int):
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Step_Speed,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_C),  # NOS
              ev3.LCX(speed),  # SPEED
              ev3.LCX(15),  # STEP1
              ev3.LCX(60),  # STEP2
              ev3.LCX(15),  # STEP3
              ev3.LCX(1),  # BRAKE - yes
              ev3.opOutput_Start,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_C)  # NOS
          ))
      )
  
  
  def test():
      ops = b''.join((
          ev3.opOutput_Test,
          ev3.LCX(0),  # LAYER
          ev3.LCX(ev3.PORT_C),  # NOS
          ev3.GVX(0)  # BUSY
      ))
      reply = my_ev3.send_direct_cmd(ops, global_mem=4)
      busy = struct.unpack('<i', reply)[0]
      if busy:
          return False
      else:
          return True
  
  
  def stop():
      my_ev3.send_direct_cmd(
          b''.join((
              ev3.opOutput_Stop,
              ev3.LCX(0),  # LAYER
              ev3.LCX(ev3.PORT_C),  # NOS
              ev3.LCX(0)  # BRAKE - no
          ))
      )
  
  
  speed = 5

  t_song = jukebox.song(ev3.FRERE_JACQUES)
  
  t_forwards = Task(step_speed, args=(speed,)) + Periodic(.2, test)
  t_forwards.action_stop = stop
  
  t_backwards = Task(step_speed, args=(-speed,)) + Periodic(.2, test)
  t_backwards.action_stop = stop
  
  t = (
      Task(t_song.start) +
      Task(prepare) +
      Repeated(
          Task(t_forwards) + Task(t_backwards),
          num=5
      ) +
      Task(stop)
  )
  
  t.start()
  
  sleep(2)
  t.stop()

Some remarks:
  - Nearly all of the program is about creating t as a thread task
    object. Its execution is only the few lines at the end. You can
    easily imagine to hide the creation behind the public API of a
    class.
  - The parallel execution of motor movements and playing a song is handled inside of t.
  - This thread task is not perfect because its continuation logic is not proper coded.

