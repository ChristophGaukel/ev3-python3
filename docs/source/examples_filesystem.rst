-----------
File System
-----------

.. role:: python(code)
   :language: python3

:py:class:`~ev3_dc.FileSystem` is a subclass of
:py:class:`~ev3_dc.EV3`.  It uses system commands and allows to
operate on EV3's file system (read LEGO's `Communication Developer Kit
<https://www.lego.com/cdn/cs/set/assets/blt6879b00ae6951482/LEGO_MINDSTORMS_EV3_Communication_Developer_Kit.pdf>`_
for the details). You can read, write and delete files and
directories. Please take care, you can damage the software of your EV3
brick.


Method list_dir
~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  
  def print_header(type: str):
      print()
      if type == 'rsf':
          print('robot sound file             size (bytes)  md5-checksum')
      elif type == 'rgf':
          print('robot graphics file          size (bytes)  md5-checksum')
      elif type == 'rbf':
          print('robot brick file             size (bytes)  md5-checksum')
      print('-'*75)
  
  
  def print_table(files: tuple, type: str):
      header_printed = False
      for file in files:
          if file[0].endswith('.' + type):
              if not header_printed:
                  print_header(type)
                  header_printed = True
              print(
                  '{:27s}  {:12d}  {:12s}'.format(*file)
              )
  
  
  folders, files = my_ev3.list_dir('/home/root/lms2012/sys/ui')
  print_table(files, 'rsf')
  print_table(files, 'rgf')
  print_table(files, 'rbf')

  
Some remarks:

  - This program reads files and subfolders in directory
    */home/root/lms2012/sys/ui*. Then it prints the sound-, graphics-
    and brick-files as tables.
  - The operating system of the EV3 brick is Unix, therefore use
    slashes, not backslashes when writing the path of a directory.
  - You can use absolute or relative paths, releative paths are
    relative to */home/root/lms2012/sys*, e.g. our path could also be
    written as *./ui*.
  - files is a tuple of tuples. Per file, we get three data:

    - name of the file,
    - size of the file,
    - md5 checksum of the file's data.

  - We ignore subfolders, because in this directory, there is none.

The output:

.. code-block:: none

  robot sound file             size (bytes)  md5-checksum
  ---------------------------------------------------------------------------
  Startup.rsf                          3109  7BE0A201F57917BC0DDE508E63DD7AD8
  PowerDown.rsf                        7939  2381EF46C5166BFF0B5852369E5A2CC7
  OverpowerAlert.rsf                   8553  BE802DF67CBBC4E4A40C223BFFF4C14A
  GeneralAlarm.rsf                     7300  A40C190AF86C8FA9A7FE9143B36B86EC
  DownloadSucces.rsf                   6599  681C88B5930DE152C0BB096F890C492F
  Click.rsf                             173  A16F9F1FDDACF56EDF81B4CD968826B4
  
  robot graphics file          size (bytes)  md5-checksum
  ---------------------------------------------------------------------------
  settings_screen.rgf                   600  55186477FDBAF838AEDA09BFDBFAABA2
  screen.rgf                           2049  ACE80443D1FA8736231BA21D63260CA4
  playrecent_screen.rgf                 600  CDBAE801B780484D80DA95538CF867C2
  mindstorms.rgf                        302  BCED9CC85FCB72259F4901E836AED8DF
  file_screen.rgf                       600  EFF6FAE6C487828734800AFB912DD700
  apps_screen.rgf                       600  19EA377DAD1869512B3759E28B6DECCD
  Ani1x.rgf                              42  AB225E46367E84D5FC23649EC4DE1CE9
  144x82_POP4.rgf                      1478  7E255363590442E339F93CBDAF222CA1
  144x65_POP3.rgf                      1172  2BED43A3D00A5842E4B91E136D232CEA
  
  robot brick file             size (bytes)  md5-checksum
  ---------------------------------------------------------------------------
  ui.rbf                               5030  6F46636743FBDE68B489071E590F0752
  

Now we come to directories. The following program demonstrates, how to
recursively read a directory subtree.

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  
  def dir_recursive(path: str):
      folders, files = my_ev3.list_dir(path)
      for folder in folders:
          if folder in ('.', '..'):
              continue
          next_path = path + '/' + folder
          print(next_path)
          dir_recursive(next_path)
  
  
  dir_recursive('/home')

This program recursively reads the */home* folder, where Unix systems
hold the user-owned data. It prints all subfolders, but ignores files
inside the folders.

The output:

.. code-block:: none

  /home/root
  /home/root/lms2012
  /home/root/lms2012/tools
  /home/root/lms2012/tools/WiFi
  /home/root/lms2012/tools/Volume
  /home/root/lms2012/tools/Sleep
  /home/root/lms2012/tools/Brick Info
  /home/root/lms2012/tools/Bluetooth
  /home/root/lms2012/sys
  /home/root/lms2012/sys/ui
  /home/root/lms2012/sys/settings
  /home/root/lms2012/sys/mod
  /home/root/lms2012/sys/lib
  /home/root/lms2012/source
  /home/root/lms2012/prjs
  /home/root/lms2012/prjs/BrkProg_SAVE
  /home/root/lms2012/prjs/BrkProg_SAVE/CVS
  /home/root/lms2012/apps
  /home/root/lms2012/apps/Brick Program
  /home/root/lms2012/apps/Brick Program/CVS
  /home/root/lms2012/apps/IR Control
  /home/root/lms2012/apps/IR Control/CVS
  /home/root/lms2012/apps/Port View
  /home/root/lms2012/apps/Port View/CVS
  /home/root/lms2012/apps/Motor Control
  /home/root/lms2012/apps/Motor Control/CVS

Some remarks:

  - *root* is the only user on this Unix system.
  - If you already worked on some projects and did run them on your EV3 brick, you will find them
    in */home/root/lms2012/prjs*.
  - The sequence of subfolders is backward-sorted by name as is the sequence of files.


Method create_dir
~~~~~~~~~~~~~~~~~

Method :py:meth:`~ev3_dc.FileSystem.create_dir` allows to create
directories in the filesystem of the EV3 brick.

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  dir = '/home/root/lms2012/prjs'
  subdir = 'tmp'
  
  # read sub-directories
  folders, files = my_ev3.list_dir(dir)
  print('*** old ***')
  for folder in folders:
      print(folder)
  
  # create directory
  my_ev3.create_dir(dir + '/' + subdir)
  
  # read sub-directories
  folders, files = my_ev3.list_dir(dir)
  print('*** new ***')
  for folder in folders:
      print(folder)

This program first reads the sub-directories of
*/home/root/lms2012/prjs*, then it creates directory
*/home/root/lms2012/prjs/tmp* and finally it again reads the
sub-directories of */home/root/lms2012/prjs*.

There are a lot of restrictions for user *root*'s filesystem. E.g. you
are not allowed to create sub-directories in */home/root* or
*/home/root/lms2012*. If you try to do that, the EV3 brick answers
with an error.

The output:

.. code-block:: none

  *** old ***
  BrkProg_SAVE
  ..
  .
  *** new ***
  BrkProg_SAVE
  tmp
  ..
  .
  
Indeed, after creating directory */home/root/lms2012/prjs/tmp* there
is an additional sub-directory named *tmp* in
*/home/root/lms2012/prjs*.

If you start this program a second time, you will get an error because
you can't create a directory that allready exists.


Method del_dir
~~~~~~~~~~~~~~~~~

Method :py:meth:`~ev3_dc.FileSystem.del_dir` allows to delete
directories in the filesystem of the EV3 brick.

Connect your EV3 brick and your computer with an USB cable and replace
the MAC-address by the one of your EV3 brick. The following program is thought
to be executed after the one above:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  dir = '/home/root/lms2012/prjs'
  subdir = 'tmp'
  
  # read sub-directories
  folders, files = my_ev3.list_dir(dir)
  print('*** old ***')
  for folder in folders:
      print(folder)
  
  # delete directory
  my_ev3.del_dir(dir + '/' + subdir)
  
  # read sub-directories
  folders, files = my_ev3.list_dir(dir)
  print('*** new ***')
  for folder in folders:
      print(folder)

The program is very similar to the one above, but it deletes a
directory instead of creating it.

The output:

.. code-block:: none

  *** old ***
  BrkProg_SAVE
  tmp
  ..
  .
  *** new ***
  BrkProg_SAVE
  ..
  .
  
Indeed, after deleting directory */home/root/lms2012/prjs/tmp* there
is no more a sub-directory named *tmp* in
*/home/root/lms2012/prjs*.

And again, you can't run this program a second time. If you do so, you
will get an error because you can't delete a directory that doesn't
exist.

If you need to delete non-empty directories, setting keword argument
*secure=False* allows to do so.


Method read_file
~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick, then start this program:

.. code:: python3

  import ev3_dc as ev3
  from hashlib import md5
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  folder = '/bin'
  filename = 'usb-devices'
  
  # read data from EV3 brick, calculate md5 and write data to local file
  data = my_ev3.read_file(folder + '/' + filename)
  print('md5-checksum (copy):', md5(data).hexdigest().upper())
  with open(filename, 'w') as f:
      f.write(data.decode('utf-8'))
  
  # get md5 of the file from EV3 brick
  subfolders, files = my_ev3.list_dir(folder)
  for file in files:
      if file[0] == filename:
          print('md5-checksum (orig):', file[2])

This program reads file */bin/usb-devices* from the EV3 brick and
writes a local copy. The file is part of the brick's operating
system. It's human readable because it is a `bash-script
<https://en.wikipedia.org/wiki/Bash_(Unix_shell)>`_. The correctness
of the reading is demonstrated by two `md5-checksums
<https://en.wikipedia.org/wiki/MD5>`_, one from the original on the
EV3 brick, the other from the read data.

The output:

.. code-block:: none

  md5-checksum (copy): 5E78E1B8C0E1E8CB73FDED5DE384C000
  md5-checksum (orig): 5E78E1B8C0E1E8CB73FDED5DE384C000


Method write_file
~~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick and start the following
program, that creates sub-directory and a file on the EV3 brick. It
writes some text into the file and it allows to test if the
md5-checksum is the correct one.

.. code:: python3

  import ev3_dc as ev3
  from hashlib import md5
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  dir = '/home/root/lms2012/prjs'
  subdir = 'tmp'
  filename = 'some.txt'
  txt = 'This is some text.'
  txt_bytes = txt.encode('utf-8')
  
  # md5-ckecksum of txt
  print('md5-checksum (text):', md5(txt_bytes).hexdigest().upper())
  
  # create directory
  my_ev3.create_dir(dir + '/' + subdir)
  
  # write txt into file
  my_ev3.write_file(
      dir + '/' + subdir + '/' + filename,
      txt_bytes
  )
  
  # md5-checksum of file
  folders, files = my_ev3.list_dir(dir + '/' + subdir)
  print('md5-checksum (file):', files[0][2])
  
  # delete directory
  my_ev3.del_dir(dir + '/' + subdir, secure=False)

Some remarks:

  - Method *write-file* accepts *bytes* not *str*, therefore we need to encode the text.
  - Setting *secure=False* allows to delete the subdirectory with its content. This is
    done at the end of the program.

The output:

.. code-block:: none

  md5-checksum (text): 5A42E1F277FBC664677C2D290742176B
  md5-checksum (file): 5A42E1F277FBC664677C2D290742176B


Method copy_file
~~~~~~~~~~~~~~~~

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick and start the following
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  dir = '../prjs/tmp'
  filename = dir + '/' + 'some.txt'
  filename_copy = dir + '/' + 'copy.txt'
  txt = 'This is some text.'
  
  # create directory
  my_ev3.create_dir(dir)
  
  # write txt into file
  my_ev3.write_file(filename, txt.encode('utf-8'))
  
  # copy file
  my_ev3.copy_file(filename, filename_copy)
  
  # read directory's content
  folders, files = my_ev3.list_dir(dir)
  print('file                         size (bytes)  md5-checksum')
  print('-'*75)
  for file in files:
      print(
          '{:27s}  {:12d}  {:12s}'.format(*file)
      )
  
  # delete directory
  my_ev3.del_dir(dir, secure=False)
  
Some remarks:

  - This program works with relative paths.
  - As above it creates a sub-directory */home/root/lms2012/prjs/tmp*.
  - File */home/root/lms2012/prjs/tmp/some.txt* is created by method
    :py:meth:`~ev3_dc.FileSystem.write_file`, file
    */home/root/lms2012/prjs/tmp/copy.txt* is created by method
    :py:meth:`~ev3_dc.FileSystem.copy_file`.

The output:

.. code-block:: none

  file                         size (bytes)  md5-checksum
  ---------------------------------------------------------------------------
  some.txt                               18  5A42E1F277FBC664677C2D290742176B
  copy.txt                               18  5A42E1F277FBC664677C2D290742176B

As expected, both files have the same sizes and md5-checksums.


Method del_file
~~~~~~~~~~~~~~~

Method :py:meth:`~ev3_dc.FileSystem.del_file` allows to delete single
files in the file-system of an EV3 brick. Be careful, when using it,
you can even delete files of the EV3 brick's operating system.

Connect your EV3 brick and your computer with an USB cable. Replace
the MAC-address by the one of your EV3 brick and start the following
program:

.. code:: python3

  import ev3_dc as ev3
  
  my_ev3 = ev3.FileSystem(
      protocol=ev3.USB,
      host='00:16:53:42:2B:99',
  )
  
  dir = '../prjs/tmp'
  filename = dir + '/' + 'some.txt'
  filename_copy = dir + '/' + 'copy.txt'
  txt = 'This is some text.'
  
  # create directory
  my_ev3.create_dir(dir)
  
  # write txt into file
  my_ev3.write_file(filename, txt.encode('utf-8'))
  
  # copy file
  my_ev3.copy_file(filename, filename_copy)

  # delete file
  my_ev3.del_file(filename)
  
  # read directory's content
  folders, files = my_ev3.list_dir(dir)
  print('file                         size (bytes)  md5-checksum')
  print('-'*75)
  for file in files:
      print(
          '{:27s}  {:12d}  {:12s}'.format(*file)
      )
  
  # delete directory
  my_ev3.del_dir(dir, secure=False)
  
The program is very similar to the one above. It uses nearly all
methods of class :py:class:`~ev3_dc.FileSystem`.

.. code-block:: none

  file                         size (bytes)  md5-checksum
  ---------------------------------------------------------------------------
  copy.txt                               18  5A42E1F277FBC664677C2D290742176B

File *some.txt* has been deleted, only the copy did exist, when
:py:meth:`~ev3_dc.FileSystem.list_dir` was called.
