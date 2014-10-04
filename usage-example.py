#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
TODO
"""

import nsrslib as nsrs
import nsrslib.settings as settings

print settings.NSR_SERVER

print nsrs.get_version()

nsrs.bla() # using pre-defined settings

# dyn. overwrite settings 
# without changing func-signature (no param)?
# kwargs?

nsrs.init_settings(NSR_SERVER="zaphod")
nsrs.bla()

nsrs.get_clients()
