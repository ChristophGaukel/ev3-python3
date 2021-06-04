#####
Voice
#####

:py:class:`~ev3_dc.Voice` is a subclass of :py:class:`~ev3_dc.Sound`.
You can use it to get your EV3 device speaking. This is done by
supportting `text to speech
<https://en.wikipedia.org/wiki/Speech_synthesis>`_. Method
:py:meth:`~ev3_dc.Voice.speak` generates robot sound files (rsf) from
text strings, copies them to the EV3 device and plays them.


++++++++++++++++++++++++++++
Get your EV3 Device Speaking
++++++++++++++++++++++++++++

Take an USB cable and connect your EV3 brick with your computer, then
start this program:

.. code:: python3

  import ev3_dc as ev3
  
  with ev3.Voice(protocol=ev3.USB, lang='it') as voice:
      (
          voice.speak(
              '''
              Bona sera, cara Francesca! Come stai?
              Non vedo l'ora di venire in Italia.
              Stasera è una bella serata.
              '''
          ) + voice.speak(
              '''
              Hello Brian,
              this is your LEGO EV3 device.
              I speak english and hope, you can understand me.
              If not so, select another language please.
              ''',
              lang='en'
          ) + voice.speak(
              '''
              Guten Abend, lieber Kurt! Wie geht es Dir?
              Hier regnet es viel, wie schon den ganzen März und April.
              ''',
              lang='de'
          )
      ).start(thread=False)

Some remarks:

  - Per call of method :py:meth:`~ev3_dc.Voice.speak` this program
    does the following steps in the background:

    - It calls `google's tts server
      <https://gtts.readthedocs.io/en/latest/index.html>`_, which
      answers with mp3 data.
    - It calls the system's program *ffmpeg* to convert mp3 into pcm
      data of the requested sample rate and resolution.
    - It splits the pcm into parts, adds headers and sends part by part to the EV3
      device, where they are played.

  - This voice was defined as italian speaking. The first call of
    method :py:meth:`~ev3_dc.Voice.speak` is without argument
    *lang*. The second and third calls are with an explicit *lang*
    argument.
  - The timing is automatic, each text gets the time it needs.

+++++++++++++++++++++++++++++++++
Use Voice for your User Interface
+++++++++++++++++++++++++++++++++

Class *Voice* allows to design user interfaces with spoken
elements. We run a little program, which uses the EV3 device as a
competitve game tool. Two players have 5 seconds time to push a touch
sensor as often they can.

Take an USB cable and connect your EV3 brick with your computer,
connect two touch sensors to ports 1 and 4, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from time import sleep
  
  with ev3.Voice(protocol=ev3.USB, volume=100) as voice:
      left_touch = ev3.Touch(ev3.PORT_1, ev3_obj=voice)
      right_touch = ev3.Touch(ev3.PORT_4, ev3_obj=voice)
  
      voice.speak('Ready', duration=2).start(thread=False)
      voice.speak('Steady', duration=2).start(thread=False)
      voice.speak('Go').start()
      left_touch.bumps = 0
      right_touch.bumps = 0
      sleep(5)
  
      cnt_left = left_touch.bumps
      cnt_right = right_touch.bumps
      voice.speak(
          f'''
          Stop,
          {cnt_left} on the left side and
          {cnt_right} on the right side
          '''
      ).start(thread=False)
  
Some remarks:

  - Compare with program :ref:`bump_mode`, which uses the display for a
    simular user interface.
  - Keyword argument *ev3_obj* allows the three objects, *voice*,
    *left_touch* and *right_touch* to share a single connection.
    *voice* owns the connection and shares it with *left_touch* and
    *right_touch*.
  - Optional argument *duration* lets a task wait some additional time
    until the duration time is over. This helps for precise timing.
  - speaking *Go* executes parallel in its own thread. This says: the
    five seconds timespan starts when the speaking starts.
  - resetting *bumps* prevents from jump starts.
  - the formatted multiline string makes *cnt_left* and *cnt_right*
    part of the spoken text.


++++++++++++++++++++++++++++++++++++++++++++++++
Combine Text to Speech with existing Sound Files
++++++++++++++++++++++++++++++++++++++++++++++++

Class :py:class:`~ev3_dc.Voice` is a subclass of
:py:class:`~ev3_dc.Sound` and inherits all their methods. Therefore it
is straight forward to combine the playing of existing sound files
with the speaking of individual texts.

Find the location of LEGO's sound files, which in my case was:
*./Program Files (x86)/LEGO Software/LEGO MINDSTORMS EV3 Home
Edition/Resources/BrickResources/Retail/Sounds/files* (I, on my Unix
system, created a soft link named *Sound*, to get easy access). Modify
the program by replacing the file locations. Take an USB cable and
connect your EV3 device with your computer then start the following
program.

.. code:: python3

  import ev3_dc as ev3
  from thread_task import Periodic
  
  with ev3.Voice(protocol=ev3.USB, volume=20, lang='en') as hugo:
      (
          Periodic(
              2,  # interval
              hugo.sound(
                  '../Sound/Animals/Dog bark 1.rsf',
                  local=True
              ),
              num=2,
              duration=3
          ) +
          hugo.speak("Don't panic, she plays only", volume=100) +
          hugo.sound(
              '../Sound/Animals/Dog bark 2.rsf',
              local=True,
              volume=100
          )
      ).start(thread=False)

Some remarks:

  - All the sound files still exist on the local machine or are
    produced on the local machine. From there, they are loaded to the
    EV3 device and played.
  - The first barking is wrapped in a Periodic, which repeats it 2
    times in an interval of 2 seconds and sets the duration to 3
    seconds.
  - The speaking, which follows the first barking, takes the language from
    its *Voice* object, but overwrites the volume.
  - The second barking is straight forward. Its not repeated and it
    reads its duration from the header of the sound file.
