# ev3-python3
Use python3 to program your LEGO Mindstorms EV3. The program runs on the local host
and sends direct commands to the EV3 device. It communicates via bluetooth, wifi or USB.
I wrote a [blog](http://ev3directcommands.blogspot.com) about this code.

There is no need to boot the EV3 device from a SD Card or manipulate
its software. You can use it as it is, the EV3 is designed to execute
commands which come from outside.

The code consists of the following modules:
* **ev3.py**  
Base class EV3, that represents the LEGO EV3 device.
* **ev3_file.py**  
FileSystem, subclass of EV3. Access to EV3's filesystem.
* **ev3_sound.py**  
Jukebox, subclass of EV3. Combines sound and LED light effects, plays music.
* **ev3_vehicle.py**  
TwoWheelVehicle, subclass of EV3. Precise movements of a vehicle with two drived wheels.
* **task.py**  
Organizes tasks. Allows parallel and sequential execution of functions.

## Examples

### Writing and sending direct commands
This program communicates via USB with
an EV3 device (mac-address: '00:16:53:42:2B:99')
and plays a tone with a frequency of 440 Hz
for a duration of 1 sec.

    #!/usr/bin/env python3
    
    import ev3
    
    my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
	my_ev3.verbosity = 1
    ops = b''.join([
        ev3.opSound,
        ev3.TONE,
        ev3.LCX(1),    # VOLUME
        ev3.LCX(440),  # FREQUENCY
        ev3.LCX(1000), # DURATION
    ])
    my_ev3.send_direct_cmd(ops)

Its output:

    11:48:31.188008 Sent 0x|0E:00|2A:00|80|00:00|94:01:01:82:B8:01:82:E8:03|

This shows the direct command, which was sent to the EV3 device.  

### Subclasses of EV3 encapsulate direct commands
Class **Jukebox** of module **ev3_sound** has a method **play_tone**,
which also plays tones:

	#!/usr/bin/env python3

	import ev3, ev3_sound

	jukebox = ev3_sound.Jukebox(protocol=ev3.BLUETOOTH, host='00:16:53:42:2B:99')
	jukebox.verbosity = 1
	jukebox.play_tone("a'", duration=1)


This program communicates via Bluetooth and sends a direct command too. Its output:

    11:55:11.324701 Sent 0x|0E:00|2A:00|80|00:00|94:01:01:82:B8:01:82:E8:03|
