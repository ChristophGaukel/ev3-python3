----------
Gyro
----------

Class :py:class:`~ev3_dc.Gyro` is a subclass of
:py:class:`~ev3_dc.EV3`. You can use it to read values from a single
gyro sensor without any knowledge of direct command syntax.

The gyro sensor is used to measure rotation. 
It has a single attrivute :py:attr:`~ev3_dc.Gyro.angle`, which is an integer representing the sensors clockwise rotation.


If you like to use multiple gyro sensors simultaneously (e.g. to receive rotations along multiple axes), you can
create more than one instance of this class.


Asking for the current angle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose settings (protocol and host) to connect the EV3 to your computer.
Replace the settings in the program below, connect a gyro sensor to PORT_1, run this program and rotate the gyrosensor:

.. code:: python3

    from time import sleep
    import ev3_dc as ev3
    settings = {"protocol":ev3.BLUETOOTH, "host":"00:16:53:81:D7:E2"}
    with ev3.Gyro(ev3.PORT_1, **settings) as gyro:
        start_angle = gyro.angle
        while True:
            current_angle = gyro.angle
            print("The current angle is %s" % current_angle)
            if current_angle - start_angle >= 360:
                print("I made a full clockwise turn!")
                break
            elif current_angle - start_angle <= -360:
                print("I made a full counterclockwise turn!")
                break
            sleep(0.05)
    
Some remarks:
  - Every reference of property *angle* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Gyro.verbosity` to value 1 and you will see
    the communication data.
