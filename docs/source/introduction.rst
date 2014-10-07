Overview
========

nsrslib ("networker scripting library") provides some tiny helpers for
administrators of the enterprise backup software `EMC Networker`_ 8.x.

nsrslib tries to provide easy access to basic networker-config-information
via python by wrapping networker-commands like `nsradmin` and `mminfo`.

it could be used directly on a networker server or on any host where the 
networker client-software is installed.


.. _installation:

Installation
------------

Download, install, upgrade and uninstall nsrslib with these commands::

  $ wget https://github.com/s3h10r/nsrslib/blob/develop/dist/nsrslib-0.0.9.tar.gz?raw=true
  $ pip install nsrslib-0.0.9.tar.gz
  $ pip install --upgrade nsrslib-0.0.9.tar.gz
  $ pip uninstall nsrslib


.. _contributing:

Contributing
============

If you've found a bug, added a feature or improved nsrslib and
think it is useful then please consider contributing.
Patches, pull requests or just suggestions are always welcome!

Source code: https://github.com/s3h10r/nsrslib

If you don’t like Github and Git you’re welcome to send regular patches.


.. _license:

License
=======

Copyright (c) 2009-2014 Sven Hessenmüller <sven.hessenmueller@gmail.com>

nsrslib is licensed under the GNU General Public License v3 or later (GPLv3+)


.. --- resolving defined links here ---
.. _EMC Networker : http://www.emc.com/products/detail/software/networker.htm 
