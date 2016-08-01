# ev3-python3
Use python3 to program your LEGO Mindstorms EV3. The program runs on the local host
and sends direct commands to the EV3 device. It communicates via bluetooth, wifi or USB.
There is a [blog](http://ev3directcommands.blogspot.de) about this code.

The code consists of the following modules:
* **ev3.py**  
Base class EV3, that represents the LEGO EV3 device.
* **ev3_sound.py**  
Jukebox, subclass of EV3. Combines sound and LED light effects, plays music.
* **ev3_vehicle.py**  
TwoWheelVehicle, subclass of EV3. Precise movements of a vehicle with two drived wheels.
* **task.py**  
Organizes tasks. Allows parallel and sequential execution of functions.

## Example
This program communicates via USB with
an EV3 device (mac-address: '00:16:53:42:2B:99')
and plays a tone with a frequency of 440 Hz
for a duration of 1 sec.

    #!/usr/bin/env python3
    
    import ev3
    
    my_ev3 = ev3.EV3(protocol=ev3.USB, host='00:16:53:42:2B:99')
    ops = b''.join([
        ev3.opSound,
        ev3.TONE,
        ev3.LCX(1),    # VOLUME
        ev3.LCX(440),  # FREQUENCY
        ev3.LCX(1000), # DURATION
    ])
    my_ev3.send_direct_cmd(ops)
