============
Installation
============

Use pip to install module **ev3_dc**:

.. code-block:: none

  python3 -m pip install --user ev3_dc

or:

.. code-block:: none

  pip3 install --user ev3_dc


Before you can use bluetooth, you need to `couple (only steps 1 - 12)
<https://nrca.zendesk.com/hc/en-us/articles/115002669503-Bluetooth-How-to-connect-the-EV3-Robot-to-your-PC-Computer-by-wireless-Bluetooth>`_
the computer (that executes the python programs) and the EV3 brick.

If you own a wifi dongle, and you want use it, `connect (only steps
1 - 12)
<https://de.mathworks.com/help/supportpkg/legomindstormsev3io/ug/connect-to-an-ev3-brick-over-wifi.html>`_
the EV3 brick with the Wifi network.
  

Linux
-----

ev3_dc should work out of the box.


Windows
-------

Bluetooth works from Python 3.9 upwards (in the time of this writing,
this means to install a `python pre release version
<https://www.python.org/downloads/windows/>`_).

USB works if libusb is installed with a driver for EV3 devices. Follow
this `instruction
<https://www.smallcab.net/download/programme/xm-07/how-to-install-libusb-driver.pdf>`_
and replace *Xin-Mo Programmer* by *EV3*  (when I did it, I
clicked the *Install Now* button in the Inf-Wizard and it was
successfully installing).

