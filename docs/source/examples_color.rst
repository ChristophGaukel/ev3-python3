-----
Color
-----

Class :py:class:`~ev3_dc.Color` is a subclass of
:py:class:`~ev3_dc.EV3`. You can use it to read values from a single
color sensor without any knowledge of direct command syntax. The color
sensor measures light intensity or colors. This may be reflected
light. If you like to use multiple color sensors simultaneously, then
create more than one instance of this class.


The reflected intensity of red light
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Color` has an attribute
:py:attr:`~ev3_dc.Color.reflected`, which is of type int and tells the
intensity of the reflected red light in percent. This says: it
switches on red light and then measures the reflection from a
surface. From then on the red light shines permanently. With constant
surface type and color, this allows to measure small distances (this
needs calibration). Alternatively, when the distance is constant, it
allows to distinguish dark from bright surfaces (e.g. for line
followers). Because of the red light, it tends to categorize red
surfaces as bright and green surfaces as dark.

Take an USB cable and connect your EV3 device with your
computer. Replace MAC-address ``00:16:53:42:2B:99`` by the one of your
EV3 brick, connect a color sensor (it may be of type
ev3.NXT_COLOR or ev3.EV3_COLOR) with PORT 1, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_color = ev3.Color(
          ev3.PORT_1,
          protocol=ev3.USB,
          host='00:16:53:42:2B:99'
  )
  
  print(f'reflected intensity is {my_color.reflected} %')
      
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or WiFi.
  - Run the program multiple times with different surface colors and
    distances.
  - Test what happens, when no sensor is connected to PORT 1.
  - Test what happens, when another sensor type is connected to PORT 1.
  - Every reference of property *reflected* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Color.verbosity` to value 1 and you will see the
    communication data.

My program's output was:

.. code-block:: none

  reflected intensity is 17 %


Recognize colors
~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Color` has an attribute
:py:attr:`~ev3_dc.Color.color`, which is of type int and tells the
color of the surface in front of the sensor. This ist done when the
sensor shines white.

Take an USB cable and connect your EV3 device with your
computer. Replace MAC-address ``00:16:53:42:2B:99`` by the one of your
EV3 brick, connect a color sensor (it may be of type
ev3.NXT_COLOR or ev3.EV3_COLOR) with PORT 1, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_color = ev3.Color(
          ev3.PORT_1,
          protocol=ev3.USB,
          host='00:16:53:42:2B:99'
  )
  
  color = (
      'none',
      'black',
      'blue',
      'green',
      'yellow',
      'red',
      'white',
      'brown'
  )[my_color.color]
  print('the color is', color)
        
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or WiFi.
  - Run the program multiple times with different surface colors in
    front of the sensor.
  - Test what happens, when no sensor is connected to PORT 1.
  - Test what happens, when another sensor type is connected to PORT 1.
  - Every reference of property *color* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Color.verbosity` to value 1 and you will see the
    communication data.
  - The light emission is permanent. Therefore the sensor permanently
    switches on white light.
  - NXT-Color does never answer with 0 or 7, it therefore will never
    see *none* or *brown*.
  - You can use the constants *ev3.NONECOLOR*, *ev3.BLACKCOLOR*,
    etc. if your program asks for specific colors.

My program's output was:

.. code-block:: none

  the color is green


Red green blue Color Intensities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Color` has an attribute
:py:attr:`~ev3_dc.Color.rgb_raw`, which is a tuple of three int type values and tells the
color of the surface in front of the sensor. This ist done when the
sensor shines with all three led colors on.

Take an USB cable and connect your EV3 device with your
computer, connect a color sensor (it must be of type
ev3.EV3_COLOR) with PORT 1, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_color = ev3.Color(
          ev3.PORT_1,
          protocol=ev3.USB
  )
  print(my_color.rgb_raw)
        
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or WiFi.
  - Run the program multiple times with different surface colors in
    front of the sensor. Also vary the distance from the surface.
  - Be aware, that every reference of property *rgb_raw* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Color.verbosity` to value 1 and you will see the
    communication data.
  - The light emission is permanent. Therefore the sensor permanently
    switches on all its LED light colors.

My program's output with a white surface in front of the sensor:

.. code-block:: none

  (253, 292, 183)
        
Some remarks:

  - Maybe you did not expect to get values higher than 255. Keep in
    mind, that sensor ev3.EV3_COLOR is normed to values from 0
    to 1024.
  - The intensity of the three raw colors is not balanced. A white
    surface should be seen with all three colors at the same
    level. Here green is dominant and blue is underrepresented. Both,
    different LED light intensities and unbalanced color sensitiveness
    of the sensor combine to cause this effect. This is what
    photography or image processing names `color balance
    <https://en.wikipedia.org/wiki/Color_balance>`_.
  - The geometry also plays its role in the measured intensities. the
    blue light source is closest to the sensor, the green one is most
    distant. The smaller the distance between sensor and a white
    surface becomes, the more balanced are the three colors.


Balanced red green blue Color Intensities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Color` has an attribute
:py:attr:`~ev3_dc.Color.rgb`, which is very similar to attribute
:py:attr:`~ev3_dc.Color.rgb_raw`, but is white balanced.

Take an USB cable and connect your EV3 device with your
computer, connect a color sensor (it must be of type
ev3.EV3_COLOR) with PORT 1, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_color = ev3.Color(
          ev3.PORT_1,
          protocol=ev3.USB
  )
  my_color.rgb_white_balance = (253, 292, 183)
  print(my_color.rgb)
            
Some remarks:

  - This program uses the raw values, measured on a white surface to
    do the white balance.
  - Run the program multiple times with different surface colors in
    front of the sensor. Also vary the distance from the surface.

My program's output with a green surface in front of the sensor:

.. code-block:: none

  (43, 114, 54)
            
Some remarks:

  - Attribute :py:attr:`~ev3_dc.Color.rgb` is normed to values between 0 and 255. This is what you know as rgb colors.
  - Use a color picker, like `this one
    <https://www.w3schools.com/colors/colors_rgb.asp>`_ to control
    your results.


Ambient light intensity
~~~~~~~~~~~~~~~~~~~~~~~

Class :py:class:`~ev3_dc.Color` has an attribute
:py:attr:`~ev3_dc.Color.ambient`, which is of type int and tells the
intensity of the ambient light in percent. One would expect, that this
ist done without any light emission.  Surprisingly the EV3_Color
sensor switches on its blue light, when it measures ambient light. The
NXT-Color sensor behaves as expected, it switches its light off.

Take an USB cable and connect your EV3 device with your
computer. Replace MAC-address ``00:16:53:42:2B:99`` by the one of your
EV3 brick, connect a color sensor (it may be of type
ev3.NXT_COLOR or ev3.EV3_COLOR) with PORT 1, then start this
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_color = ev3.Color(
          ev3.PORT_1,
          protocol=ev3.USB,
          host='00:16:53:42:2B:99'
  )
  
  print(f'ambient intensity is {my_color.ambient} %')
      
Some remarks:

  - You already know, how to change the program for using protocols
    Bluetooth or WiFi.
  - Run the program multiple times with different light intensity in
    front of the sensor.
  - Test what happens, when no sensor is connected to PORT 1.
  - Test what happens, when another sensor type is connected to PORT 1.
  - Every reference of property *ambient* starts a new communication
    between the program and the EV3 device.
  - Switch on verbosity by setting attribute
    :py:attr:`~ev3_dc.Color.verbosity` to value 1 and you will see the
    communication data.
  - The light emission is permanent. Therefore EV3-Color permanently
    changes to blue light, NXT-Color permanently switches its light
    off.

My program's output was:

.. code-block:: none

  ambient intensity is 9 %
