# ev3-python3
Use python3 to program your LEGO EV3. Communicate via bluetooth, wifi or USB. Send direct commands.

The code consists of the following modules:

ev3.py
Base class EV3, that represents the LEGO EV3 device.

ev3_vehicle.py
TwoWheelVehicle, subclass of EV3. Precise movements of a vehicle with two drived wheels.

ev3_sound.py
Jukebox, subclass of EV3. Combines sound and LED light effects, plays music.

task.py
Organizes tasks. Allows parallel and sequential execution of functions.


There is a blog about this code: http://ev3directcommands.blogspot.de
