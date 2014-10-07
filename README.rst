nsrslib - networker scripting library
=====================================
:Description: nsrslib provides some tiny helpers for administrators
              of the enterprise backup software `EMC Networker`_ 8.x 

nsrslib tries to provide easy access to basic networker-config-information
via python by wrapping networker-commands like `nsradmin` and `mminfo`.

it could be used directly on a networker server or on any host where the
networker client-software is installed.


usage
-----

.. code::

    #!/usr/bin/python
    # -*- coding: utf-8 -*-
    """
    usage-example.py
    """
    
    import nsrslib as nsrs
    import nsrslib.settings as settings
    
    print "nsrslib version: ", nsrs.get_version()
    
    print settings.NSR_SERVER
    
    # query for nsr-server defined in settings.NSR_SERVER
    
    print nsrs.get_clients() 
    
    # query for any other nsr-server
    
    print nsrs.get_clients(nsr_server="other-nsr-server.example.com")
    
    # same data as json... 
    
    clientconf = nsrs.get_clients_json(nsr_server=srv)
    print clientconf
    
    # ... and transformed back into a python-datastructure
    
    import json
    datastruct = json.loads(clientconf)
    for client in datastruct:
        print client
    

for more try::

    cd nsrslib && pydoc ./core.py


Contributing
============

If you've found a bug, added a feature or improved nsrslib and 
think it is useful then please consider contributing.
Patches, pull requests or just suggestions are always welcome!

Source code: https://github.com/s3h10r/nsrslib

If you don’t like Github and Git you’re welcome to send regular patches.


License
=======

Copyright (c) 2009-2014 Sven Hessenmüller <sven.hessenmueller@gmail.com>

nsrslib is licensed under the GNU General Public License v3 or later (GPLv3+)


.. --- resolving defined links ---
.. _EMC Networker : http://www.emc.com/products/detail/software/networker.htm
