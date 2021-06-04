============
Installation
============

Use pip to install module **ev3_dc**:

.. code-block:: none

  python3 -m pip install --user ev3_dc

or:

.. code-block:: none

  pip3 install --user ev3_dc


pip also allows to upgrade module **ev3_dc**:

.. code-block:: none

  python3 -m pip install --upgrade --user ev3_dc

**ev3_dc** supports `text to speech
<https://en.wikipedia.org/wiki/Speech_synthesis>`_. You need to
install `ffmpeg <https://ffmpeg.org/>`_ to get it working. On a
Windows machine, you have to download an archive (e.g. `this
<https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z>`_) and
unpack it. Finally you have to add the directory with the binary files
to your environment variable *path*. MacOS and Unix provide
installation packages (MacOS: *brew install ffmpeg*, Ubuntu: *sudo
apt-get install ffmpeg*).

Before you can use Bluetooth, you need to couple the computer (that
executes the python programs) and the EV3 brick.

If you own a compatible WiFi dongle, and you want to use it, you have
to connect the EV3 brick with the WiFi network.

Protocol USB is the fastest option, both to establish the connection
and to communicate. But using USB may need some additional
installations.

Read more in section :ref:`connect_with_device`.

